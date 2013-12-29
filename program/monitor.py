#monitor.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 22.12.2013
@brief monitors flow sensor
"""

import serial, sys, time
import threading
from ConfigParser import SafeConfigParser
import logging
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
		self.sensor_threshold_min = config.getint('monitor','sensor_threshold_min')
		self.sensor_threshold_max= config.getint('monitor','sensor_threshold_max')
		self.starttime = 0
		
		
		#presence
		#per default assume, that patient is at home when monitoring starts
		self.setPresence(1)
	
	#an Spracherkennung binden
	#Setzt Anwesenheit via DAtei
	def setPresence(self,value):
		try:
			presenceFile = open("/tmp/seheiah_presence", "w")
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
				if(inputAsInteger >= self.sensor_threshold_min):
					self.starttime = int(time.time()) #setzt Startzeit
					self.setPresence(1) #Wenn Wasser verbraucht wird, ist Typ auch daheim
					#solange sensor feuert, Zeit festhalten
					while not (inputAsInteger < self.sensor_threshold_min):
						time.sleep(0.5)
						inputAsInteger = int(serialFromArduino.readline())
						#log for debugging and get trhesholds
						if(int(time.time()) % 5 == 0):
							logging.debug("Value: %s" % inputAsInteger)
						
						
				
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
