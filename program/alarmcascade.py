#alarmcascade.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 04.02.2014
@brief initiate alarm cascade
"""

import time
import subprocess
import socket, os, os.path #für Kommunikation mit Unix-Sockets
import threading
import logging
#eigene
import readConfig as rc
import playAudio

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
		self.server.setblocking(1) #this was 0
		self.server.bind("/tmp/seheiah_alarm.sock")
		
		self.timestampUnexpBeh = 0	#timestamp unexpected behavior
		#time to interrupt alarm
		self.alarmValidateTime = rc.config.getint('alarmcascade','alarmValidateTime')
		#use sip-client for feedback?
		self.sipClient = rc.config.getint('alarmcascade','sipClient')
		
		self.alarm = False
		self.snapshotFilename = "" #name der Snaphot-Datei
		self.messageSended = False #Marker, ob NAchricht bereits gesendet wurde
		
		#load audioplay
		self.pa = playAudio.playAudio()


	"""
	receive commands from socket, checks and set alarm varaibles
	"""
	def interpretMessage(self,message):
		#nur schlucken, wenn noch kein Alarm ausgelöst wurde
		if((message == "UNEXPECTED BEHAVIOR") and (self.timestampUnexpBeh == 0)):
			print "perhaps Alarm"
			self.timestampUnexpBeh = int(time.time())
			self.messageSended = False
			
		#für den Fall eines eindeutigen Notfalls, etwa Hilferuf von Spracherkennung
		elif(message == "HILFE"):
			print "HILFE !!!"
			self.alarm = True
			self.messageSended = False
			#print "self.alarm=",self.alarm
		elif(message == "ALARM AUS"):
			try:
				#self.timestampUnexpBeh = 0
				print "KOMMANDO ALARM AUS"
				self.alarm = False
				self.messageSended = False
				self.timestampUnexpBeh = 0
				if (self.sipClient == 1):
					p = subprocess.Popen(rc.config.get('alarmcascade','cmdSipClientStop'))
					p.communicate()
			except ValueError:	
				pass

	#does a beautyful picture of a room
	def makeSnapshot(self):
		#delegate the snapshot to subprocess. because its memoryintensive
		self.snapshotFilename = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rc.config.get('alarmcascade','snapshotpath'))+str(int(time.time()))+".jpg"
		p = subprocess.Popen(["python", os.path.join(os.path.dirname(os.path.abspath(__file__)),"snapshot.py"), self.snapshotFilename])
		p.communicate()
	
	#sends E-Mail to family, friends, ...
	def sendEmailMessage(self):
		import smtplib
		from email import Encoders
		from email.MIMEBase import MIMEBase
		from email.MIMEText import MIMEText
		from email.MIMEMultipart import MIMEMultipart
		from email.Utils import formatdate
		
		filePath = self.snapshotFilename
		#recipients
		TO = rc.config.get('alarmcascade','recipients').split(',')
		FROM = rc.config.get('alarmcascade','sender')
		#mailserver
		HOST = rc.config.get('alarmcascade','mailhost')
		PORT = rc.config.getint('alarmcascade','mailport')
		PASSWORD = rc.config.get('alarmcascade','mailpass')
 		
		#prepare attachment
		attachment = MIMEBase('application', "octet-stream")
		attachment.set_payload( open(filePath,"rb").read() )
		Encoders.encode_base64(attachment)
		attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filePath))
 		
		for mailAddress in TO:
			#header
			logging.info("prepare e-mail for: %s" % mailAddress)
			msg = MIMEMultipart()
			msg["From"] = FROM
			msg["To"] = mailAddress
			msg["Subject"] = rc.config.get('alarmcascade','mailsubject').strip('"')
			msg['Date']    = formatdate(localtime=True)
			msg.attach(MIMEText(rc.config.get('alarmcascade','mailmessage').strip('"')))
			msg.attach(attachment)
			#contact mailserver
			server = smtplib.SMTP(HOST,PORT)
			server.ehlo()
			server.starttls()
			server.ehlo()
			loginSuccess = server.login(FROM, PASSWORD)
			logging.info(loginSuccess)
			
			#send e-mail
			try:
				logging.info("try to send email to: %s" % mailAddress)
				server.sendmail(FROM, mailAddress, msg.as_string())
				server.quit()
				self.messageSended = True
				logging.info("email to: %s sended" % mailAddress)
			except Exception, e:
				errorMsg = "Unable to send email. Error: %s" % str(e)
				logging.error(errorMsg)
	
		#if message sended, reset snapshot, so that no old picture will be sended
		if(self.messageSended):
			self.snapshotFilename = ""
		
	#Bild machen, angehörige informieren
	def processAlarm(self):
		if(self.messageSended == False):
			mp3file = rc.config.get('general','seheiahPath') + rc.config.get('audiofiles','emergencyCallStart')
			self.pa.playMp3(mp3file)
			self.makeSnapshot()
			self.sendEmailMessage()
			mp3file = rc.config.get('general','seheiahPath') + rc.config.get('audiofiles','emergencyCallDone')
			self.pa.playMp3(mp3file)
			if (self.sipClient == 1):
				p = subprocess.Popen(rc.config.get('alarmcascade','cmdSipClientStart'))
				p.communicate()
			self.messageSended = True
	
	#prüft, ob Alarm auszulösen ist, z.B. wenn unerwartetes Verhalten auftritt oder 
	def checkAlarm(self):
		if((self.timestampUnexpBeh > 0) and (int(time.time()) <= self.timestampUnexpBeh + self.alarmValidateTime)):
			#hier eine schöne Nachricht abspielen
			if(0 <= int(time.time())%20 <= 3):
				mp3file = rc.config.get('general','seheiahPath') + rc.config.get('audiofiles','unexpectedBehavior')
				self.pa.playMp3(mp3file)
		elif((self.timestampUnexpBeh > 0) and (int(time.time()) > self.timestampUnexpBeh + self.alarmValidateTime)):
			self.alarm = True


	def run(self):
		logging.info("Thread AlarmCascade started")
		while True:
			#auf Socket Nachrichten empfangen und weiterreichen
			time.sleep(1)
			try:
				data = self.server.recv(32) #so viele Daten werden nicht erwartet
				if not data:
					break
				else: #falls Daten vorhanden sind, werden sie ausgewertet
					self.interpretMessage(data)
			except socket.error, e:
				time.sleep(1)
				logging.error("Socket error" + str(e))
			#bei unerwartetem Verhalten prüfen, ob es sich um Fehlalarm handelt und evtl. Alarm auslösen
			self.checkAlarm()
			if(self.alarm == True):
				self.processAlarm()
			
		print "Shutting down..."
		self.server.close()
		os.remove("/tmp/seheiah_alarm.sock")
