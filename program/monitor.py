#monitor.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 02.09.2013
@brief monitors sensor
"""

import serial, sys, time
import threading
from ConfigParser import SafeConfigParser
#own classes
import logdb

#read variables
CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)

class Monitor(threading.Thread):
	#initialisieren
	def __init__(self):
		threading.Thread.__init__(self) #threading-class initialisieren
		self.daemon = True
		#self.port = #port='/dev/sensors/arduino_A400fXzQ' #Mutterns Sensor
		self.port = config.get('monitor','arduino_port')
		self.starttime = 0
		
		#presence
		#per default assume, that patient is at home when monitoring starts
		self.setPresence(1)
	
	#an Spracherkennung binden
	#Setzt Anwesenheit via DAtei
	def setPresence(self,value):
		try:
			presenceFile = open("/home/falko/nactivity_presence", "w")
			try:
				presenceFile.write(str(value))
			finally:
				presenceFile.close()
		except IOError:
			pass
	
	def run(self):
		db = logdb.logDB()	#Datenbank übernehmen
		#Sensor abfragen
		serialFromArduino=serial.Serial(self.port,9600)
		serialFromArduino.flushInput()
		
		while True:
			try:
				inputAsInteger=int(serialFromArduino.readline())
				self.starttime = 0
				if(inputAsInteger >= 10):
					self.starttime = int(time.time()) #setzt Startzeit
					self.setPresence(1) #Wenn Wasser verbraucht wird, ist Typ auch daheim
					#solange sensor feuert, Zeit festhalten
					while (int(serialFromArduino.readline()) != 0):
						time.sleep(0.5)
				
					#Zeit berechnen, die Wasser entnommen wurde (min 1 sek)
					duration = (int(time.time())) - self.starttime
					#schreibt Werte in DB, wenn mindestens 3 Sekunden Wasser entnommen wurde
					if(duration > 3):
						db.add_log(self.starttime,duration)
			except ValueError:	
				pass
		db.closeDB()
		
	def getStartTime(self):
		return self.starttime
