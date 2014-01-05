#monitor.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 05.01.2014
@brief monitors flow and pir sensors
"""

import serial, sys, time
import threading
import logging
#own
import logdb
import readConfig as rc

class Monitor(threading.Thread):
	#initialisieren
	def __init__(self):
		threading.Thread.__init__(self) #threading-class initialisieren
		self.daemon = True
		#self.port = #port='/dev/sensors/arduino_A400fXzQ' #Mutterns Sensor
		self.port = rc.config.get('monitor','arduino_port')
		self.sensor_threshold_min = rc.config.getint('monitor','sensor_threshold_min')
		self.pir = rc.config.getboolean('monitor','pir')
		if(self.pir):
			"""
			import RPi.GPIO as GPIO
			self.pirGPIO = rc.config.int('monitor','pirGPIO')
			GPIO.setup(pirGPIO,GPIO.IN)
			"""
			try:
				import pigpio
			except ImportError:
				self.pigpio = None
			else:
				self.pigpio = pigpio
				self.pirGPIO = rc.config.getint('monitor','pirGPIO')
				self.pigpio.start()
				self.pigpio.set_mode(self.pirGPIO,  self.pigpio.INPUT)
		self.starttime = 0
		
		
		#presence
		#per default assume, that patient is at home when monitoring starts
		self.setPresence(1)

	#set start time, if a sensor is firing
	def setStartTime(self):
		self.starttime = int(time.time())
		#if there is water flow or motion, the monitored senior is alive and home
		self.setPresence(1)
	
	#returns starttime, it's important to detect long waterflow
	def getStartTime(self):
		return self.starttime

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
		
		logging.info("Thread Monitor started")
		
		db = logdb.logDB()	#load database
		#connection arduino flow sensor
		serialFromArduino=serial.Serial(self.port,9600)
		serialFromArduino.flushInput()
		
		while True:
			self.starttime = 0
			#read flowsensor
			try:
				inputAsInteger=int(serialFromArduino.readline())
				if(inputAsInteger >= self.sensor_threshold_min):
					self.setStartTime()
					#while flow sensor is firing
					while not (inputAsInteger < self.sensor_threshold_min):
						time.sleep(0.5)
						inputAsInteger = int(serialFromArduino.readline())
			except ValueError:	
				pass
			#read pir
			if(self.pir):
				try:
					pirState = self.pigpio.read(self.pirGPIO)
					if(pirState == 1):
						#if pir is in the area, where the subject is staying most of the time, you need another variable than  
						self.setStartTime()
						#while pir is firing
						while not (pirState == 0):
							time.sleep(0.5)
							pirState = self.pigpio.read(self.pirGPIO)
				except Exception, e:
					logging.error(str(e))
					
			#Zeit berechnen, die Wasser entnommen wurde (min 1 sek)
			if(self.starttime > 0):
				duration = (int(time.time())) - self.starttime
				#schreibt Werte in DB, wenn mindestens 3 Sekunden Wasser entnommen wurde
				if(duration > 3):
					db.add_log(self.starttime,duration)
					
		#close database
		db.closeDB()
		# Reset GPIO settings
		#GPIO.cleanup()
		self.pigpio.stop()
