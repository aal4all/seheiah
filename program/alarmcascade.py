#emergencyca.py
# -*- coding: utf-8 -*-

#stoesst Alarmcascade an

import time #serial,sys
import socket, os, os.path #für Kommunikation mit Unix-Sockets
import threading
import logging
from ConfigParser import SafeConfigParser
#eigene klassen


#read variables
CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)

class AlarmCascade(threading.Thread):
	#initialisieren
	def __init__(self):
		threading.Thread.__init__(self) #threading-class initialisieren
		self.daemon = True
		
		#Socket
		if os.path.exists( "/tmp/seheiah_alarm.sock" ):
			os.remove( "/tmp/seheiah_alarm.sock" )
		print "Opening socket..."
		self.server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) #DGRAM
		self.server.setblocking(0)
		self.server.bind("/tmp/seheiah_alarm.sock")
		
		self.incomingAlarmTime = 0	#Zeitstempel eines möglichen Alarms
		#time to interrupt alarm
		self.alarmValidateTime = config.getint('alarmcascade','alarmValidateTime')
		self.alarm = False
		self.snapshotFilename = "" #name der Snaphot-Datei
		self.messageSended = False #Marker, ob NAchricht bereits gesendet wurde


	"""
	Nimmt Kommandos des Sockets entgegen, prüft sie und setzt Alarm-Variablen
	"""
	def interpretMessage(self,message):
		#nur schlucken, wenn noch kein Alarm ausgelöst wurde
		if((message == "UNEXPECTED BEHAVIOR") and (self.incomingAlarmTime == 0)):
			print "perhaps Alarm"
			self.incomingAlarmTime = int(time.time())
		#für den Fall eines eindeutigen Notfalls, etwa Hilferuf von Spracherkennung
		elif(message == "ALARM"):
			print "Alarm !!!"
			self.alarm = True
			print "self.alarm=",self.alarm
		#wenn abweichendes Verhalten festgestellt wurde, kann Alarm duch Wasserverbrauch entschärft werden
		#ganz üble Frickellösung, unbedingt durch Spracherkennung oder von wasserverbrauch unabhängige Methode ersetzen
		elif(("WATERFLOW" in message) and ((self.incomingAlarmTime > 0) or (self.alarm == True))):
			splitMessage = message.split()
			print "Message: ", message
			try:
				"""
				wenn Wasserfluss einsetzt, nachdem unerwartetes Verhalten festgestellt wurde, kann von Fehlalarm ausgegangen werden
				wenn Alarm bereits läuft, zurücksetzen, um nächstes Auftreten zu erkennen
				"""
				if(int(splitMessage[1]) > self.incomingAlarmTime):
					self.incomingAlarmTime = 0
					self.alarm = False
					self.messageSended = False
			except ValueError:	
				pass
		

	#spielt audiofile ab
	def playAudioFile(self):
		from subprocess import Popen, PIPE
		output = Popen(['mpg321', os.path.realpath(__file__)+'../mp3s/unexpected_behavior.mp3'], stdout=PIPE)
		print output.stdout.read()
		
    
	#does a beautyful picture of a room
	def makeSnapshot(self):
		import cv
		my_width = 320
		my_height = 240
		print "makeSnapshot"
		#initialise webcam  (cam 0)
		capture = cv.CaptureFromCAM(0)
		if not capture:
			print "capture-Fehler"
		else:
			#bildeigenschaften
			cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, my_height)
			cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, my_width)
		img = cv.QueryFrame(capture)
		if not img:
			print "imagefehler"
		else:
			self.snapshotFilename = config.get('alarmcascade','snapshotpath')+str(int(time.time()))+".jpg"
			cv.SaveImage(self.snapshotFilename, img)
	
	
	#versendet Nachricht an liebe Verwandte, Freunde, ...
	def sendMessage(self):
		import smtplib
		from email import Encoders
		from email.MIMEBase import MIMEBase
		from email.MIMEText import MIMEText
		from email.MIMEMultipart import MIMEMultipart
		from email.Utils import formatdate
		
		filePath = self.snapshotFilename
		
		print "sendMessage"
		
		TO = config.get('alarmcascade','recipients').split(',')
		FROM = config.get('alarmcascade','sender')
		#mailserver
		HOST = config.get('alarmcascade','mailhost')
		PORT = config.getint('alarmcascade','mailport')
		PASSWORD = config.get('alarmcascade','mailpass')
 		
		#Anhang vorbereiten
		attachment = MIMEBase('application', "octet-stream")
		attachment.set_payload( open(filePath,"rb").read() )
		Encoders.encode_base64(attachment)
		attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filePath))
 		
		# Nachricht klar machen
		#header
		msg = MIMEMultipart()
		msg["From"] = FROM
		msg["To"] = TO
		msg["Subject"] = config.get('alarmcascade','mailsubject').strip('"')
		msg['Date']    = formatdate(localtime=True)
		msg.attach(MIMEText(config.get('alarmcascade','mailmessage').strip('"')))
		msg.attach(attachment)
		print "Server kontaktieren"
		#mailserver kontaktieren
		server = smtplib.SMTP(HOST,PORT) #evtl. Inhalt in Klammern löschen
		#server.connect(HOST,PORT)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(FROM, PASSWORD)  # optional
 
		#mail versenden
		try:
			print "Mail versenden"
			sended = server.sendmail(FROM, TO, msg.as_string())
			print "sended=",sended
			server.quit()
			self.snapshotFilename = ""
			self.messageSended = True
		except Exception, e:
			errorMsg = "Unable to send email. Error: %s" % str(e)
		#snapshot zurücksetzen, so dass nie alte Bilder versand werden


	#Bild machen, angehörige informieren
	def processAlarm(self):
		if(self.messageSended == False):
			print "processAlarm Action"
			self.makeSnapshot()
			self.sendMessage()
	
	#prüft, ob Alarm auszulösen ist, z.B. wenn unerwartetes Verhalten auftritt oder 
	def checkAlarm(self):
		if((self.incomingAlarmTime > 0) and (int(time.time()) <= self.incomingAlarmTime + self.alarmValidateTime)):
			#hier eine schöne Nachricht abspielen
			print "unerwartetes Verhalten überprüfen"
			self.playAudioFile()
		elif((self.incomingAlarmTime > 0) and (int(time.time()) > self.incomingAlarmTime + self.alarmValidateTime)):
			self.alarm = True


	def run(self):
		while True:
			#auf Socket Nachrichten empfangen und weiterreichen
			try:
				data = self.server.recv(32) #so viele Daten werden nicht erwartet
				if not data:
					break
				else: #falls Daten vorhanden sind, werden sie ausgewertet
					self.interpretMessage(data)
			except socket.error:
				time.sleep(1)
			#bei unerwartetem Verhalten prüfen, ob es sich um Fehlalarm handelt und evtl. Alarm auslösen
			self.checkAlarm()
			if(self.alarm == True):
				self.processAlarm()
			
		print "Shutting down..."
		self.server.close()
		os.remove("/tmp/seheiah_alarm.sock")
