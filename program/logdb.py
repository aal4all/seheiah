#logdb.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 17.01.2014
@brief database operations for activity monitor
"""

import sqlite3, os, time
#own
import readConfig as rc

class logDB(object):
	#initialisieren
	def __init__(self):
		db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rc.config.get('logdb','database'))
		#Datenbank verbinden
		self.conn = sqlite3.connect(db, timeout=10)
		#Cursor-Objekt, um mit DB zu intaragieren
		self.cursor = self.conn.cursor()
	
		
	#schreibt neue Datensätze in DB
	def add_log(self,starttime,duration):
		#tests, if midnight occurs considering timezones
		if((starttime - time.timezone) / 86400 < (starttime - time.timezone + duration) / 86400):
			secondDuration = int(starttime - time.timezone + duration) % 86400
			secondStarttime = int(starttime + duration) - secondDuration
			duration = duration - secondDuration - 1
			values = [(starttime,duration), (secondStarttime,secondDuration)]
		else:
			values = [(starttime,duration)] #werte für db
		try:
			self.cursor.executemany("INSERT INTO activity_log (starttime, duration) VALUES (?,?);", values)
			self.conn.commit()
		except sqlite3.OperationalError:
			time.sleep(3)
	
	#fragt ab, wie viele Tage bereits in DB gespeichert wurden
	def getSavedDays(self,currentDay,weekend):
		#DB-Abfrage anpassen, je nachdem ob WE ist oder nicht
		if weekend: #Wochenende
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') NOT BETWEEN '1' AND '5' AND "
		else: #Wochentag
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') BETWEEN '1' AND '5' AND "
		try:
			self.cursor.execute("SELECT COUNT(DISTINCT (starttime/86400)) FROM activity_log WHERE " + sql_weekend + "(starttime/86400) < ?;", (currentDay,))
			savedDays = int(self.cursor.fetchone()[0]) #nur tagesanzahl interessant
		except sqlite3.OperationalError:
			time.sleep(3)
		return savedDays
	
	
	"""
	prüft, wie oft Sensor in Vergangenheit (historical = True) oder innerhalb der letzten  
	24 Stunden (86400 Sekunden) um eine bestimmte Uhrzeit gefeuert hat (modulo)	
	mittels DISTINCT(starttime/86400) werden mehrere Werte innerhalb eines Intervalls eines Tages auf 1 reduziert
	bei den historischen Vergleichen wird der aktuelle Bereich +/- die toleranz (interval * quantum) betrachtet, um Aussagen treffen zu können, mit welcher Wahrscheinlichkeit ein Verhalten innerhalb dieser Zeit autritt
	
	Bei Werten
	"""
	def getVectorValues(self, intervalStart, intervalEnd, currentTime, tolerance, weekend, historical):
		"""
		berücksichtigen, ob Wochentag oder WE
		 SELECT strftime('%w',1363440713,'unixepoch','localtime');
		 Sonntag == 0
		 Samstag == 6
		 time.strftime("%w", time.localtime(1363440713))
		"""
		#DB-Abfrage anpassen, je nachdem ob WE ist oder nicht
		if weekend: #Wochenende
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') NOT BETWEEN '1' AND '5' AND "
		else: #Wochentag
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') BETWEEN '1' AND '5' AND "
		
		#Intervallstart und Ende im Falle von Toleranzen korrigieren
		startTime = intervalStart-tolerance
		endTime = intervalEnd+tolerance
		if(startTime < 0):
			startTime += 86400
		if(endTime > 86400):
			startTime -= 86400
		values = (currentTime, startTime, startTime, endTime, endTime) #werte für query
		if historical == False: # aktueller Tag
			sql = "SELECT COUNT(DISTINCT (starttime/86400)) FROM activity_log WHERE " + sql_weekend + "starttime > ? - 86400 AND ((starttime%86400) > ? OR ((starttime+duration)%86400) > ?) AND ((starttime%86400) <= ? OR ((starttime+duration)%86400) <= ?);"
		else: #historische Daten
			sql = "SELECT COUNT(DISTINCT (starttime/86400)) FROM activity_log WHERE " + sql_weekend + "starttime <= ? - 86400 AND ((starttime%86400) > ? OR ((starttime+duration)%86400) > ?) AND ((starttime%86400) <= ? OR ((starttime+duration)%86400) <= ?);"
		try:
			self.cursor.execute(sql, values)
			frequency = int(self.cursor.fetchone()[0]) #anzahl erfasster Activitäten im definierten Zeitraum
		except sqlite3.OperationalError:
			time.sleep(3)
		return frequency
	
	
	"""
	loescht bei mehr als zu speichernden Tagen die ältesten Werte
	wochenenden und Wochentage berücksichtigen
	"""
	def delOldEntries(self,weekend):
		#DB-Abfrage anpassen, je nachdem ob WE ist oder nicht
		if weekend: #Wochenende
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') NOT BETWEEN '1' AND '5' AND "
		else: #Wochentag
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') BETWEEN '1' AND '5' AND "
		try:
			self.cursor.execute("DELETE FROM activity_log WHERE " + sql_weekend + "starttime/86400 = (SELECT MIN(starttime/86400) FROM activity_log);")
			self.conn.commit()
		except sqlite3.OperationalError:
			time.sleep(3)
	
	#visualisation
	def getActivities(self,weekend):
		#DB-Abfrage anpassen, je nachdem ob WE ist oder nicht
		if weekend: #Wochenende
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') NOT BETWEEN '1' AND '5'"
		else: #Wochentag
			sql_weekend = " strftime('%w',starttime,'unixepoch','localtime') BETWEEN '1' AND '5'"
		#sql = "SELECT date(starttime,'unixepoch','localtime'), time(starttime,'unixepoch','localtime'), date(starttime+duration,'unixepoch','localtime'), time(starttime+duration,'unixepoch','localtime') FROM activity_log WHERE " + sql_weekend + " ;"
		sql = "SELECT starttime, starttime+duration FROM activity_log WHERE " + sql_weekend + " ;"
		try:
			self.cursor.execute(sql)
			activities = self.cursor.fetchall()
		except sqlite3.OperationalError:
			time.sleep(3)
		return activities
		
	def closeDB(self):
		self.conn.close()
		
