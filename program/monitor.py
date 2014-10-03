#monitor.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 17.09.2014
@brief monitors flow and pir sensors
"""

import serial, sys, time
import threading
import logging
#own
import logdb
import readConfig as rc
import absence
import playAudio

class Monitor(threading.Thread):
	#initialisieren
	def __init__(self):
		threading.Thread.__init__(self) #threading-class initialisieren
		self.daemon = True
		self.port = rc.config.get('monitor','arduino_port')
		self.sensor_threshold_min = rc.config.getint('monitor','sensor_threshold_min')
		self.pir = rc.config.getboolean('monitor','pir')
		if(self.pir):
			import RPi.GPIO as GPIO
			self.pirGPIO = rc.config.getint('monitor','pirGPIO')
			GPIO.setmode(GPIO.BOARD)
			GPIO.setup(self.pirGPIO,GPIO.IN)
			self.pirFunc = rc.config.getint('monitor','pirFunc') #pir works as sensor or filter
			if (self.pirFunc == 2):
				self.pirStarttime = 0
			#try:
			#	import pigpio
			#except ImportError:
			#	self.pigpio = None
			#else:
			#	self.pigpio = pigpio
			#	self.pirGPIO = rc.config.getint('monitor','pirGPIO')
			#	self.pirFunc = rc.config.getint('monitor','pirFunc')
			#	self.pigpio.start()
			#	self.pigpio.set_mode(self.pirGPIO,  self.pigpio.INPUT)
			#	if (self.pirFunc == 2):
			#		self.pirStarttime = 0
		self.starttime = 0
		
		
		#read absence
		self.absence = absence.Absence()
		#audioplayback
		self.pa = playAudio.playAudio()

	#set start time, if a sensor is firing
	def setStartTime(self):
		self.starttime = int(time.time())
		#if there is water flow or motion, the monitored senior is alive and home
		if(self.absence.get()):
			self.absence.set(0)
			mp3file = rc.config.get('general','seheiahPath') + rc.config.get('audiofiles','enableMonitoring')
			self.pa.playMp3(mp3file)
	
	#returns starttime, it's important to detect long waterflow
	def getStartTime(self):
		return self.starttime

	def run(self):
		
		logging.info("Thread Monitor started")
		
		db = logdb.logDB()	#load database
		
		if(self.pir):
			try:
				import RPi.GPIO as GPIO
				GPIO.setmode(GPIO.BOARD)
				GPIO.setup(self.pirGPIO,GPIO.IN)
			except RuntimeError:
				logging.error("Error importing RPi.GPIO!  You need superuser privileges. use 'sudo' or run your script as root")
							
		#connection arduino flow sensor
		serialFromArduino=serial.Serial(self.port,9600)
		serialFromArduino.flushInput()
		
		while True:
			self.starttime = 0
			#read flowsensor
			try:
				inputAsInteger=int(serialFromArduino.readline())
				if(inputAsInteger >= self.sensor_threshold_min):
					"""
					set starttime only, if 
					#	there is no pir
					#	or pir as supporter
					# or pir as filter, which was firing in previos 2 minutes
					"""
					if not (self.pir) or (self.pir and self.pirFunc == 1) or (self.pir and self.pirFunc == 2 and (int(time.time()) - self.pirStarttime < 120)) :
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
					#pirState = self.pigpio.read(self.pirGPIO)
					pirState = GPIO.input(self.pirGPIO)
					if(pirState == 1):
						#if pir is in the area, where the subject is staying most of the time, you need another variable than  
						if (self.pirFunc == 1): #if Pir is supporter
							self.setStartTime()
						else:	#if Pir ist filter
							self.pirStarttime = int(time.time()) #set starttime of pir
							print "pirStart=",self.pirStarttime
						#while pir is firing
						while not (pirState == 0) and (self.pirFunc == 1): #only go in while loop, if pir is supporter
							time.sleep(0.5)
							#pirState = self.pigpio.read(self.pirGPIO)
							pirState = GPIO.input(self.pirGPIO)
				except Exception, e:
					logging.error(str(e))
					
			#time of water consumption (min 2 sek)
			if(self.starttime > 0):
				duration = (int(time.time())) - self.starttime
				#writes waterconsumption or pir sensor firing in database, if duration is more than two seconds
				if(duration >= 2):
					db.add_log(self.starttime,duration)
	
	def stop():	
		#close database
		db.closeDB()
		# Reset GPIO settings
		GPIO.cleanup()
		#self.pigpio.stop()
