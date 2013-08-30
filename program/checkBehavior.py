#checkBehavior.py
# -*- coding: utf-8 -*-

#fragt DB ab und prüft Cosinus-Ahnlichkeit

import threading, time
import numpy #Cosinius-Ähnlichkeit
import logging #logdatei
from ConfigParser import SafeConfigParser
#own classes
import logdb

#read variables
CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)

class Check(threading.Thread):
	def __init__(self, mon):
		threading.Thread.__init__(self) #threading-class initialisieren
		self.daemon = True
		self.mon = mon #monitor object for time requests
		#intervals to considering in seconds
		self.interval = config.getint('checkbehavior','interval')
		#tolerance, in which an activity event (in this case water flow) has to occure
		#means an regulary event can fire in an timeslot +/- (tolerance * interval) seconds 
		self.intervalQuantum = config.getint('checkbehavior','intervalquantum')
		#number of recorded days, per workdays and free days
		self.observePeriod = config.getint('checkbehavior','observePeriod')
		#threshold for accepted cosinus similarity
		self.tresholdCosSimilarity = config.getfloat('checkbehavior','tresholdCosSimilarity')
		#threshold for probability of relevant behavior occurence, necessary to filter one-time or rarely events
		self.tresholdProbability = config.getfloat('checkbehavior','tresholdProbability')
		
		#emergency counter
		self.emergency = 0
		
		#marker for actions
		self.markerCheckBehavior = False #wurde verhalten im interval abgefragt?
		self.markerCheckDelete = False #wurden alte Werte korrekt gelöscht?
		
	"""
	ermittelt Zeiten für Vektoren
	Die ermittelten Zeiten sind für einen Tag und werden später für Modulo-Berechnungen in den Datenbankabfragen verwendet.
	"""
	def getCurrentTimeValues(self,currTime):
		timeValues = [] #speichert die Zeiten
		currentDaytime = int(currTime % 86400)
		currentValue = currentDaytime - (currentDaytime % 300) #geht an den Anfang des aktuellen Zeitbereichs
		i = self.intervalQuantum
		while i >= 0:
			newValue = currentValue - i * self.interval
			if newValue < 0: #negative Werte vermeiden
				newValue + 86400
			timeValues.append(newValue) #ermittelt Zeitwerte und steckt sie in Liste
			i -= 1 #i reduzieren
		return timeValues;
	
	#extrahiert Vektor für geamten Tag
	def getAllTimeValues(self):
		timeValues = []
		currentValue = 0
		while currentValue <= 86400:
			timeValues.append(currentValue)
			currentValue += self.interval
		return timeValues;
	
	#errechnet Wahrscheinlichkeiten für gesamten Tag
	def getProbabilityVector(self,db,timeValues,weekend):
		tolerance = self.interval * self.intervalQuantum #setzt Toleranzbereich
		historical = True #historische Werte abfragen
		currTime = int(time.time())
		#Anzahl bereits gespeicherter Tage (wochentage oder Wochenenden) abfragen
		savedDays = db.getSavedDays(self.getCurrentDay(currTime),weekend)
		probabilityVector = numpy.zeros(len(timeValues),float) #Numpy-Array mit Nullen gefüllt
		i = 0
		while i < len(timeValues)-1:
			if(savedDays > 0):
				#Wahrscheinlichkeit, dass ein Verhalten innerhalb der Toleranz auftritt
				probability = float(db.getVectorValues(timeValues[i],timeValues[i+1],currTime, tolerance, weekend, historical)) / savedDays
				probabilityVector[i] = probability
				print time.strftime("%H:%M:%S",time.gmtime(timeValues[i] + self.interval/2))+" "+str(probability)
			i += 1
		return 	probabilityVector
			
	
	"""
	gibt aktuellen Tag aus, nötig für Abfrage der aufgezeichneten Tage 
	und ob Tag Wochenende oder Feiertag ist
	"""
	def getCurrentDay(self,currTime):
		return currTime / 86400


	"""
	prüft, ob aktuell Wochenende ist
	Sonntag == 0
	Samstag == 6
	time.strftime("%w", time.localtime(TIMESTAMP))
	"""
	def getWeekend(self,currTime):
		dow = time.strftime("%w", time.localtime(currTime))
		if((dow == "0") or (dow == "6")):
			weekend = True
		else:
			weekend = False
		return weekend
	
	
	#erstellt Vector für zurückliegenden Zeitraum
	#rechnet Toleranz mit rein
	def getHistoricalVector(self,db,currentTimeValues,currTime):
		tolerance = self.interval * self.intervalQuantum #setzt Toleranzbereich
		weekend = self.getWeekend(currTime) #prüfen, ob gerade WE ist
		historical = True #historische Werte abfragen
		
		#Anzahl bereits gespeicherter Tage (wochentage oder Wochenenden) abfragen
		savedDays = db.getSavedDays(self.getCurrentDay(currTime),weekend)
		logging.info("SavedDays: %s" % savedDays)
		historicalVector = numpy.zeros(self.intervalQuantum,float) #Numpy-Array mit Nullen gefüllt
		i = 0
		while i < self.intervalQuantum:
			if(savedDays > 0):
				#Wahrscheinlichkeit, dass ein Verhalten innerhalb der Toleranz auftritt
				logging.info("Vectorvalues: %s" % db.getVectorValues(currentTimeValues[i],currentTimeValues[i+1],currTime, tolerance, weekend, historical))
				probability = float(db.getVectorValues(currentTimeValues[i],currentTimeValues[i+1],currTime, tolerance, weekend, historical)) / savedDays
				logging.info("Probalility: %s" % probability)
				if(probability >= self.tresholdProbability):
					historicalVector[i] = probability
			i += 1
		return 	historicalVector


	"""		
	erstellt Vector für letzten Beobachtungszeitraum
	berücksichtigt, ob Sensor gerade aktiv ist oder nicht
	"""
	def getCurrentVector(self,db,currentTimeValues,currTime):
		tolerance = 0 #setzt Toleranzbereich, bei aktivem Vektor nicht nötig, da Zeiten genau bekannt sind und nicht nach vorn oder hinten ausreissen können
		weekend = self.getWeekend(currTime) #prüfen, ob gerade WE ist
		historical = False #letzten Zeitraum abfragen
		
		currentVector = numpy.zeros(self.intervalQuantum,float) #Numpy-Array mit Nullen gefüllt, Tupel mit tolerance Elementen
		i = 0
		#normalen Vector erstellen
		while i < self.intervalQuantum:
			currentVector[i] = db.getVectorValues(currentTimeValues[i],currentTimeValues[i+1],currTime,tolerance,weekend,historical)
			#currentVector.append(db.getVectorValues(currentTimeValues[i],currentTimeValues[i+1],int(time.time()),False)) #false, weil nur aktuelle Werte
			i += 1
		#pruefen, ob Sensor gerade feuert
		#wenn ja, könnten noch werte in der DB fehlen und Vektor muss angepasst werden
		sensorIsFiring = self.mon.getStartTime()
		if sensorIsFiring > 0:
			logging.info("sensor feuert: %s" % sensorIsFiring)
			j = 0
			while j < self.intervalQuantum:
				#wenn ein Zeitwert j>0 kleiner als wert j=0 ist, erfolgte ein Tageswechsel (0:00) und entsprechender Wert muss erhöht werden
				if currentTimeValues[j+1] < currentTimeValues[0]:
					currentTimeValues[j+1] += 86400
				#wenn der SEnsorwert kleiner als einer der zu beobachtenden Zeitwerte ist, ist der Sensor seit dem interval aktiv
				if sensorIsFiring%86400 <= currentTimeValues[j+1]:
					currentVector[j] = 1.0
				j += 1
		return currentVector
		
	
	"""
	prüft auf Abweichungen und zieht dazu aktuelles und erlerntes Verhalten heran
	extrahiert Teilvektoren aus erlernten Verhalten und vergleicht sie mit 
	aktuellem Verhalten (Cosinusähnlichkeit)
	Wenn Vektoren voneinander abweichen und die Ähnlichkeit permanent einen 
	Grenzwert unterschreitet -> Alarm auslösen
	"""
	def checkBehavior(self,database):
		db = database
		self.markerCheckBehavior = True
		currTime = int(time.time())
		currentTimeValues = self.getCurrentTimeValues(currTime) #betrachtungszeitraum
		#logging.info("CurrentTimeValues %s" % currentTimeValues)
		#print historicalTimeValues
		v_his = self.getHistoricalVector(db,currentTimeValues,currTime)
		#logging.info("historischer Vector: %s" % v_his)
		v_curr = self.getCurrentVector(db,currentTimeValues,currTime)
		
		"""
		laenge l (euklidische Norm, Skalarprodukt) des aktuellen Verhaltensvectors. 
		Ist 0<||v||_2<tolerance, ist alles ok und dem zu beobachtenden Subjekt 
		geht es offensichtlich gut
		"""
		l_v_curr = numpy.linalg.norm(v_curr)
		logging.info("aktueller Vektor: %s La:nge: %s" % (v_curr, l_v_curr))
		if(l_v_curr == 0): #kein Wasserberbrauch
			if(numpy.linalg.norm(v_his) !=  l_v_curr): #wenn normalerweise Wasser verbraucht wird ...
				self.emergency += 1 #Alarmwert hochzählen
			else:	#wenn auch in Vergangenheit kein Wasser verbraucht wurde
				self.emergency = 0
		elif(l_v_curr == numpy.sqrt(self.intervalQuantum)): #langanhaltender Wasserverbrauch über gesamten Toleranzzeitraum
			if(numpy.linalg.norm(v_his) > 0):
				similarity = (numpy.dot(v_curr,v_his)/(numpy.linalg.norm(v_his)*numpy.linalg.norm(v_curr))) #cos(v_curr,v_his)
			elif(numpy.linalg.norm(v_his) == 0): #Division durch Null!!! falls normalerweise kein Wasser verbraucht wird, Wasser aber trotzdem lange fließt, Alarm auslösen
				similarity = 0
				
			if(similarity < self.tresholdCosSimilarity):
				self.emergency += 3
		else:
			self.emergency = 0 #alles ok, evtl. Katatstrophenvorbereitungen entschärfen
		logging.info("Alarm: %s" % self.emergency)
		if(self.emergency >= 9): #Alarm auslösen
			logging.info("UNEXPECTED BEHAVIOR")
			self.messageToAlarmCascade("UNEXPECTED BEHAVIOR")
		#!!!Prüfen, OB ALARM wirklich eintreten kann
	
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
	
	
	#prüft via Datei, ob Patient anwesend ist
	def getPresence(self):
		presenceValue = True
		try:
			presenceFile = open("/tmp/seheiah_presence", "r")
			try:
				presenceValue = int(presenceFile.read())
			except IOError:
				logging.error("couldn't read from file /tmp/seheiah_presence")
			finally:
				presenceFile.close()
		except IOError:
			logging.error("file /tmp/seheiah_presence doesn't exists")
		return bool(presenceValue)
	
	#set presence of monitored subject
	def setPresence(self):
		try:
			presenceFile = open("/tmp/seheiah_presence", "w")
			try:
				presenceFile.write('1')
			except IOError:
				logging.error("couldn't write to file /tmp/seheiah_presence")
			finally:
				presenceFile.close()
		except IOError:
			logging.error("couldn't open file /tmp/seheiah_presence")
	
	def run(self):
		db = logdb.logDB()
		
		#set logging
		logfile = config.get('logging','logfile')
		loglevel = config.getint('logging','loglevel')
		logging.basicConfig(filename=logfile,filemode = 'a',level=loglevel,format = "%(threadName)s: %(asctime)s  %(name)s [%(levelname)-8s] %(message)s")
		logging.info("Thread Checkbehavior started")
		
		#Gesamtwahrscheinlichkeit ausgeben
		#weekendAllDayProbability = self.getProbabilityVector(db,self.getAllTimeValues(),True)
		#workdayAllDayProbability = self.getProbabilityVector(db,self.getAllTimeValues(),False)
		
		while True:
			currTime = int(time.time())
			#pro interval einmal Verhalten prüfen, falls Patient anwesend ist
			if((0 < currTime % self.interval <= 25) and self.getPresence() and not self.markerCheckBehavior):
				self.checkBehavior(db)
			#nach prüfung Marker wieder zurücksetzen
			elif((currTime % self.interval > 25) and self.markerCheckBehavior):
				self.markerCheckBehavior = False
				
			#einmal pro Tag Datenbank von alten Einträgen befreien
			if((0 < currTime % 86400 <= 600) and not self.markerCheckDelete):
				logging.info("delOldEntries")
				self.markerCheckDelete = True
				weekend = db.delOldEntries(self.getWeekend(currTime))
				if(db.getSavedDays(self.getCurrentDay(currTime),weekend) > self.observePeriod):
					db.delOldEntries(weekend)
			elif(currTime % 86400 > 600):
				self.markerCheckDelete = False				
			
			time.sleep(5)
			#immer Starttime an Socket senden, um Fehlalarme zu kennzeichnen
			self.messageToAlarmCascade("WATERFLOW %s" % self.mon.getStartTime())
			
