#checkBehavior.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 25.01.2014
@brief queries database and checks cosinus similarity
"""

import threading, time
import numpy #Cosinius-Ähnlichkeit
import logging #logdatei
#own
import logdb
import readConfig as rc
import absence
import playAudio
import classify


class Check(threading.Thread):
	def __init__(self, mon):
		threading.Thread.__init__(self) #threading-class initialisieren
		self.daemon = True
		self.mon = mon #monitor object for time requests
		self.classify = classify.Classify()
		#intervals to considering in seconds
		self.interval = rc.config.getint('checkbehavior','interval')
		#tolerance, in which an activity event (in this case water flow) has to occure
		#means an regulary event can fire in an timeslot +/- (tolerance * interval) seconds 
		self.toleranceIntervals = rc.config.getint('checkbehavior','toleranceIntervals')
		#number of recorded days, per workdays and free days
		self.observePeriod = rc.config.getint('checkbehavior','observePeriod')
		#number of days to learn before seheiah decide about emergency case
		self.minObservedPeriod = rc.config.getint('checkbehavior','minObservedPeriod')
		
		#emergency counter
		self.emergency = 0
		
		#marker for actions
		self.markerCheckBehavior = False #wurde verhalten im interval abgefragt?
		self.markerCheckDelete = False #wurden alte Werte korrekt gelöscht?
		
		self.absence = absence.Absence()
		
		#load playaudio
		self.pa = playAudio.playAudio()
		

	#erstellt Vector für zurückliegenden Zeitraum
	#rechnet Toleranz mit rein
	def getUsuallyVector(self,db,currTime):		
		usuallyVector = numpy.asarray(db.getProbabilities(currTime))
		return 	usuallyVector


	"""		
	erstellt Vector für letzten Beobachtungszeitraum
	berücksichtigt, ob Sensor gerade aktiv ist oder nicht
	"""
	def getCurrentVector(self,db,currTime):
		#get last recent events from database
		currentVector = numpy.asarray(db.getRecentValues(currTime))
		#test, if sensor is actually firing
		sensorIsFiring = self.mon.getStartTime()
		#if sensor is firing, update currentVector
		if sensorIsFiring > 0:
			#momentary timslice
			ctstart = currTime - (currTime % self.interval)
			#we've got the values for last three slices
			i = currentVector.shape[0]
			while i > 0:
				if(sensorIsFiring < (ctstart - ((i-1) * self.interval))):
					currentVector[currentVector.shape[0]-i] = 1.0
				i -= 1
		return currentVector
		
	
	"""
	prüft auf Abweichungen und zieht dazu aktuelles und erlerntes Verhalten heran
	extrahiert Teilvektoren aus erlernten Verhalten und vergleicht sie mit 
	aktuellem Verhalten (Cosinusähnlichkeit)
	Wenn Vektoren voneinander abweichen und die Ähnlichkeit permanent einen 
	Grenzwert unterschreitet -> Alarm auslösen
	"""
	def checkBehavior(self,db, currTime):
		
		self.markerCheckBehavior = True
		#check recent behavior
		recentBehavior = self.getCurrentVector(db,currTime)
		#if conspicuous
		if(self.classify.suspiciousBehavior(recentBehavior)):
			usuallyBehavior = self.getUsuallyVector(db,currTime)
			
			if(self.classify.behaviorDiffCos(recentBehavior, usuallyBehavior)):
				self.emergency += 1
				print recentBehavior
				print usuallyBehavior
				print self.emergency
				#logging.info("UNEXPECTED BEHAVIOR")
				#self.messageToAlarmCascade("UNEXPECTED BEHAVIOR")	
			else:
				self.emergency = 0
		
		if(self.emergency >= (self.toleranceIntervals * 2)): #Alarm auslösen
			logging.info("UNEXPECTED BEHAVIOR")
			self.messageToAlarmCascade("UNEXPECTED BEHAVIOR")	
			#reset alarm counter
			self.emergency = 0
		
	

	
	def messageToAlarmCascade(self,message):
		import socket
		import os, os.path
		if os.path.exists("/tmp/seheiah_alarm.sock"):
			client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) #DGRAM
			try:
				client.connect("/tmp/seheiah_alarm.sock")
				client.send(message)
			except socket.error:
				logging.error("Couldn't connect to socket /tmp/seheiah_alarm.sock")
			finally:
				client.close()
		else:
			logging.error("socket /tmp/seheiah_alarm.sock doesn't exists")
	
	def run(self):
		db = logdb.logDB()
		
		logging.info("Thread Checkbehavior started")
		
		while True:
			currTime = int(time.time())
			#Anzahl gespeicherter Tage
			savedDays = len(db.getSavedDays(currTime - (currTime % 86400)))
			#check, if patient at home
			patientPresent = not self.absence.get()
			
			if (0 < currTime % self.interval <= self.interval/30):
				#at least on time per interval write monitored day to database, to avoid, that it will be forgotten, because seheiah is'nt running or switched on at false time
				print "db.lastrec ", db.getLastDayRecord(), "today ", (currTime - currTime%86400)
				if (currTime%86400 > self.toleranceIntervals * self.interval) and not (db.getLastDayRecord() == (currTime - currTime%86400)): #at first delete old entries, then build probs
					try:
						#when insert day-record, also create probabilities
						db.addDayRecord(currTime)
						if (savedDays >= self.minObservedPeriod):
							db.createProbabilities()
					except:
						logging.error("Impossibile to create probabilities or insert day record")
				#if patient not at home, play all 5 minutes a small file to remember, that monitoring is disabled and avoid unintentional turn off
				if not (patientPresent):
					mp3file = rc.config.get('general','seheiahPath') + rc.config.get('audiofiles','monitoringOff')
					self.pa.playMp3(mp3file)
			#pro interval einmal Verhalten prüfen, falls Patient anwesend ist
			if((0 < currTime % self.interval <= self.interval/10) and savedDays >= self.minObservedPeriod and patientPresent and not self.markerCheckBehavior):
				self.checkBehavior(db, currTime)
			#nach prüfung Marker wieder zurücksetzen
			elif((currTime % self.interval > self.interval/10) and self.markerCheckBehavior):
				self.markerCheckBehavior = False
				
			#einmal pro Tag Datenbank von alten Einträgen befreien
			if((0 < currTime % 86400 <= self.toleranceIntervals * self.interval) and not self.markerCheckDelete):
				logging.info("delOldEntries")
				self.markerCheckDelete = True
				if(savedDays > self.observePeriod):
					db.delOldEntries(currTime - currTime % 86400)
			elif(currTime % 86400 > 600):
				self.markerCheckDelete = False				
			
			time.sleep(self.interval/60)
			#immer Starttime an Socket senden, um Fehlalarme zu kennzeichnen
			#self.messageToAlarmCascade("WATERFLOW %s" % self.mon.getStartTime())
			
