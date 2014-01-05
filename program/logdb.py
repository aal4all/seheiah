#logdb.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 02.09.2013
@brief database operations for activity monitor
"""

import sqlite3, os
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
		values = (starttime,duration) #werte für db
		try:
			self.cursor.execute("INSERT INTO activity_log (starttime, duration) VALUES (?,?);", values)
			self.conn.commit()
		except sqlite.OperationalError:
			time.sleep(3)
			retry
	
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
		except sqlite.OperationalError:
			time.sleep(3)
			retry
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
		except sqlite.OperationalError:
			time.sleep(3)
			retry
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
		except sqlite.OperationalError:
			time.sleep(3)
			retry
	
		
	def closeDB(self):
		self.conn.close()
