#logdb.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 04.02.2014
@brief database operations for activity monitor
"""

import sqlite3, os, time
import logging

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
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
	
	"""
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
	"""
	getSavedDays
	returns, how many days are saved in database
	@value int today timestamp
	@value int condition
	@return list
	@desc conditions
	  10 dayly
	  15 every working day
			starttime - timezone
			strftime('%w',starttime,'unixepoch','localtime') BETWEEN '1' AND '5' AND "
	  17 every weekend day
			starttime - timezone
			" strftime('%w',starttime,'unixepoch','localtime') NOT BETWEEN '1' AND '5' AND "
		20 every two days
			where ((starttime - starttime % 86400) / 86400) % 2 = dnrToday % 2
		30 every three days
			where ((starttime - starttime % 86400) / 86400) % 3 = dnrToday % 3
		40 every four days
			where ((starttime - starttime % 86400) / 86400) % 4 = dnrToday % 4
		50 every five days
			where ((starttime - starttime % 86400) / 86400) % 5 = dnrToday % 5
		60 every six days
			where ((starttime - starttime % 86400) / 86400) % 6 = dnrToday % 6
		70 weekly
			where ((starttime - starttime % 86400) / 86400) % 7 = dnrToday % 7
		Für Visualisierung
			starttime - timezone
		71 every monday
			" strftime('%w',starttime,'unixepoch','localtime') = '1'
		72 every tuesday
			" strftime('%w',starttime,'unixepoch','localtime') = '2'
		73 every wednesday
			" strftime('%w',starttime,'unixepoch','localtime') = '3'
		74 every thursday
			" strftime('%w',starttime,'unixepoch','localtime') = '4'
		75 every friday
			" strftime('%w',starttime,'unixepoch','localtime') = '5'
		76 every saturday
			" strftime('%w',starttime,'unixepoch','localtime') = '6'
		77 every sunday
			" strftime('%w',starttime,'unixepoch','localtime') = '0'
	"""
	def getSavedDays(self,today,condition = 10):
		savedDays = []
		#where clause as dictionary
		whereClause = {
			10 : "", #daily
			15 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') BETWEEN '1' AND '5'", #workdays, consider timezone
			17 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') NOT BETWEEN '1' AND '5'", #weekends, consider timezone
			20 : "AND (logged_day / 86400) % 2 = "+ str((today / 86400) % 2), #every 2 days
			30 : "AND (logged_day / 86400) % 3 = "+ str((today / 86400) % 3), #every 3 days
			40 : "AND (logged_day / 86400) % 4 = "+ str((today / 86400) % 4), #every 4 days
			50 : "AND (logged_day / 86400) % 5 = "+ str((today / 86400) % 5), #every 5 days
			60 : "AND (logged_day / 86400) % 6 = "+ str((today / 86400) % 6), #every 6 days
			70 : "AND (logged_day / 86400) % 7 = "+ str((today / 86400) % 7), #weekly
			}
			#~ 71 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') = '1'",#every monday, consider timezone
			#~ 72 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') = '2'",#every tuesday, consider timezone
			#~ 73 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') = '3'",#every wednesday, consider timezone
			#~ 74 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') = '4'",#every thursday, consider timezone
			#~ 75 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') = '5'",#every friday, consider timezone
			#~ 76 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') = '6'",#every saturday, consider timezone
			#~ 77 : "AND strftime('%w',logged_day-(" + str(time.timezone) +"),'unixepoch','localtime') = '0'",#every sunday, consider timezone
		try:
			self.cursor.execute("SELECT logged_day FROM logged_days WHERE logged_day < ? " + whereClause[condition] +";", (today,))
			for element in self.cursor.fetchall(): #liefere alle tage zurück, Für Tagesanzahl muss Liste gezählt werden	 
				savedDays.append(element[0])
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
		del whereClause
		return savedDays
	

	"""
	createProbabilities
	track through historical data, count events in a specific period (interval + tolerance) and tries to calculate probailities for an event today
	within a period it clusters events, so that many small events looks like one event
	alle ereignisse zählen, die innerhalb eines bestimmten Zeitraumes aufgetreten sind
	"""
	def createProbabilities(self):
		t1 = int(time.time()) # starttime of creation of probabilities
		#at first clean probabilities table
		self.truncProbabilities() #perhaps update is better
		#then caclulate probs
		interval = rc.config.getint('checkbehavior','interval') #get timeslice length
		tolerance = interval * rc.config.getint('checkbehavior','toleranceIntervals') #tolerance 
		today = int(time.time()) - (int(time.time()) % 86400) #today timestamp
		#dictionary with where clauses ,	(condition,beforeMidnight,afterMidnight):Clause
		whereClause = {
			#daily
			(10,False,False) : "",
			(10,True,False) : "",
			(10,False,True) : "",
			#workdays, considers timezone
			#normal
			(15,False,False) : " AND (strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') BETWEEN '1' AND '5' OR strftime('%w',starttime+duration-(" + str(time.timezone) +"),'unixepoch','localtime') BETWEEN '1' AND '5')",
			#from Friday to saturday, before midnight, e.g. time 23:55 -> starttime 23:40, endtime 0:10 in saturday, but monday not
			(15,True,False) : "AND (strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') BETWEEN '2' AND '6' OR strftime('%w',starttime+duration-(" + str(time.timezone) +"),'unixepoch','localtime') BETWEEN '2' AND '6') ",
			#from sunday to monday, after midnight, e.g time 0:05 -> starttime 23:50, means include sunday, but not friday
			(15,False,True) : "AND (strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') BETWEEN '0' AND '4' OR strftime('%w',starttime+duration-(" + str(time.timezone) +"),'unixepoch','localtime') BETWEEN '0' AND '4')",
			#weekends, consider timezone
			#normal
			(17,False,False) : "AND (strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('0', '6') OR strftime('%w',starttime+duration-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('0', '6'))",
			#from sunday to monday, before midnight, e.g. time 23,55 -> endtime 0:10 in monday, but saturday not
			(17,True,False) : "AND (strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('0', '1') OR strftime('%w',starttime+duration-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('0', '1'))",
			#from Friday to saturday, after midnight, e.g time 0:05 -> starttime 23:50, means include friday, but not sunday
			(17,False,True) : "AND (strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('5', '6') OR strftime('%w',starttime+duration-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('5','6'))",
			#every 2 days
			#normal
			(20,False,False)  : "AND ((starttime / 86400) % 2 = "+ str((today / 86400) % 2) + " OR ((starttime+duration) / 86400) % 2 = "+ str((today / 86400) % 2) + ")",
			#before midnight, search endtime also in next day
			(20,True,False)  : "AND ((starttime / 86400) % 2 IN  ("+ str((today / 86400) % 2) +","+str(((today / 86400)+1) % 2) + ") OR  ((starttime+duration) / 86400) % 2 IN  ("+ str((today / 86400) % 2) +","+str(((today / 86400)+1) % 2) + "))",
			#after midnight, search starttime also in day before
			(20,False,True)  : "AND ((starttime / 86400) % 2 IN  ("+ str((today / 86400) % 2) +","+str(((today / 86400)-1) % 2) + ") OR  ((starttime+duration) / 86400) % 2 IN  ("+ str((today / 86400) % 2) +","+str(((today / 86400)-1) % 2) + "))",
			#every 3 days
			#normal
			(30,False,False)  : "AND ((starttime / 86400) % 3 = "+ str((today / 86400) % 3) + " OR ((starttime+duration) / 86400) % 3 = "+ str((today / 86400) % 3) + ")",
			#before midnight, search endtime also in next day
			(30,True,False)  : "AND ((starttime / 86400) % 3 IN  ("+ str((today / 86400) % 3) +","+str(((today / 86400)+1) % 3) + ") OR  ((starttime+duration) / 86400) % 3 IN  ("+ str((today / 86400) % 3) +","+str(((today / 86400)+1) % 3) + "))",
			#after midnight, search starttime also in day before
			(30,False,True)  : "AND ((starttime / 86400) % 3 IN  ("+ str((today / 86400) % 3) +","+str(((today / 86400)-1) % 3) + ") OR  ((starttime+duration) / 86400) % 3 IN  ("+ str((today / 86400) % 3) +","+str(((today / 86400)-1) % 3) + "))",
			#every 4 days
			#normal
			(40,False,False)  : "AND ((starttime / 86400) % 4 = "+ str((today / 86400) % 4) + " OR ((starttime+duration) / 86400) % 4 = "+ str((today / 86400) % 4) + ")",
			#before midnight, search endtime also in next day
			(40,True,False)  : "AND ((starttime / 86400) % 4 IN  ("+ str((today / 86400) % 4) +","+str(((today / 86400)+1) % 4) + ") OR  ((starttime+duration) / 86400) % 4 IN  ("+ str((today / 86400) % 4) +","+str(((today / 86400)+1) % 4) + "))",
			#after midnight, search starttime also in day before
			(40,False,True)  : "AND ((starttime / 86400) % 4 IN  ("+ str((today / 86400) % 4) +","+str(((today / 86400)-1) % 4) + ") OR  ((starttime+duration) / 86400) % 4 IN  ("+ str((today / 86400) % 4) +","+str(((today / 86400)-1) % 4) + "))",
			#every 5 days
			#normal
			(50,False,False)  : "AND ((starttime / 86400) % 5 = "+ str((today / 86400) % 5) + " OR ((starttime+duration) / 86400) % 5 = "+ str((today / 86400) % 5) + ")",
			#before midnight, search endtime also in next day
			(50,True,False)  : "AND ((starttime / 86400) % 5 IN  ("+ str((today / 86400) % 5) +","+str(((today / 86400)+1) % 5) + ") OR  ((starttime+duration) / 86400) % 5 IN  ("+ str((today / 86400) % 5) +","+str(((today / 86400)+1) % 5) + "))",
			#after midnight, search starttime also in day before
			(50,False,True)  : "AND ((starttime / 86400) % 5 IN  ("+ str((today / 86400) % 5) +","+str(((today / 86400)-1) % 5) + ") OR  ((starttime+duration) / 86400) % 5 IN  ("+ str((today / 86400) % 5) +","+str(((today / 86400)-1) % 5) + "))",
			#every 6 days
			#normal
			(60,False,False)  : "AND ((starttime / 86400) % 6 = "+ str((today / 86400) % 6) + " OR ((starttime+duration) / 86400) % 6 = "+ str((today / 86400) % 6) + ")",
			#before midnight, search endtime also in next day
			(60,True,False)  : "AND ((starttime / 86400) % 6 IN  ("+ str((today / 86400) % 6) +","+str(((today / 86400)+1) % 6) + ") OR  ((starttime+duration) / 86400) % 6 IN  ("+ str((today / 86400) % 6) +","+str(((today / 86400)+1) % 6) + "))",
			#after midnight, search starttime also in day before
			(60,False,True)  : "AND ((starttime / 86400) % 6 IN  ("+ str((today / 86400) % 6) +","+str(((today / 86400)-1) % 6) + ") OR  ((starttime+duration) / 86400) % 6 IN  ("+ str((today / 86400) % 6) +","+str(((today / 86400)-1) % 6) + "))",
			#weekly
			#normal
			(70,False,False)  : "AND ((starttime / 86400) % 7 = "+ str((today / 86400) % 7) + " OR ((starttime+duration) / 86400) % 7 = "+ str((today / 86400) % 7) + ")",
			#before midnight, search endtime also in next day
			(70,True,False)  : "AND ((starttime / 86400) % 7 IN  ("+ str((today / 86400) % 7) +","+str(((today / 86400)+1) % 7) + ") OR  ((starttime+duration) / 86400) % 7 IN  ("+ str((today / 86400) % 7) +","+str(((today / 86400)+1) % 7) + "))",
			#after midnight, search starttime also in day before
			(70,False,True)  : "AND ((starttime / 86400) % 7 IN  ("+ str((today / 86400) % 7) +","+str(((today / 86400)-1) % 7) + ") OR  ((starttime+duration) / 86400) % 7 IN  ("+ str((today / 86400) % 7) +","+str(((today / 86400)-1) % 7) + "))",
			}
			#~ #every monday, consider timezone
			#~ #normal
			#~ (71,False,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') = '1'",
			#~ #before midnight, see for endtime also next day
			#~ (71,True,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('1','2')",
			#~ #after midnight, search in day before
			#~ (71,False,True) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('0','1')",
			#~ #every tuesday, consider timezone
			#~ #normal
			#~ (72,False,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') = '2'",
			#~ #before midnight, see for endtime also next day
			#~ (72,True,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('2','3')",
			#~ #after midnight, search in day before
			#~ (72,False,True) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('1','2')",
			#~ #every wednesday, consider timezone
			#~ (73,False,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') = '3'",
			#~ #before midnight, see for endtime also next day
			#~ (73,True,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('3','4')",
			#~ #after midnight, search in day before
			#~ (73,False,True) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('2','3')",
			#~ #every thursday, consider timezone
			#~ (74,False,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') = '4'",
			#~ #before midnight, see for endtime also next day
			#~ (74,True,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('4','5')",
			#~ #after midnight, search in day before
			#~ (74,False,True) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('3','4')",
			#~ #every friday, consider timezone
			#~ (75,False,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') = '5'",
			#~ #before midnight, see for endtime also next day
			#~ (75,True,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('5','6')",
			#~ #after midnight, search in day before
			#~ (75,False,True) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('4','5')",
			#~ #every saturday, consider timezone
			#~ (76,False,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') = '6'",
			#~ #before midnight, see for endtime also next day
			#~ (76,True,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('6','7')",
			#~ #after midnight, search in day before
			#~ (76,False,True) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('5','6')",
			#~ #every sunday, consider timezone
			#~ (77,False,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') = '0'",
			#~ #before midnight, see for endtime also next day
			#~ (77,True,False) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('0','1')",
			#~ #after midnight, search in day before
			#~ (77,False,True) : "AND strftime('%w',starttime-(" + str(time.timezone) +"),'unixepoch','localtime') IN ('6','0')",
		#list with times
		t = range(0, 86400, interval)
		#list with daily probabilities, prefilled with 0s
		c10 = []
		for i in range(0,len(t)):
			c10.append(0.0)		
		dbValues = []	
		for condition in (10,15,17,20,30,40,50,60,70): #,71,72,73,74,75,76,77):
			#dbValues = []
			for i in range(0,len(t)):
				probability = 0.0 #default, no event at time
				#build list for daily probs and test only for other conditions, in there at least one event in all the time
				if(condition == 10 or c10[i] > 0.0):
					startTime = t[i] - tolerance #starttime with tolerance
					endTime = t[i] + tolerance #endtime with tolerance
					# when starttime is shortly before midnight, endtime falls in the next day
					beforeMidnight = False
					endAfterMidnight = 0
					# when starttime is shortly before midnight, endtime falls in the next day
					AfterMidnight = False
					startBeforeMidnight = 0 # when starttime falls in last day
					#shortly before midnight
					if (endTime > 86400):
						# endTime = endTime - 86400
						beforeMidnight = True
						endAfterMidnight = 86400
					#shortly after midnight 
					if (startTime < 0):
						#startTime = startTime + 86400
						afterMidnight = True
						startBeforeMidnight = 86400
					values = (today, startTime, startTime, endTime, endTime) #werte für query
					#suche alle in der Vergangenheit, die innerhalb des Tolleranzbereichs beginnen oder enden
					countSql = "SELECT COUNT(DISTINCT (starttime/86400)) FROM activity_log WHERE starttime < ? AND (((starttime%86400)-" + str(startBeforeMidnight) + " > ? OR ((starttime+duration)%86400)-" + str(startBeforeMidnight) + " > ?) " + whereClause[condition,beforeMidnight,afterMidnight] + " ) AND (((starttime%86400)+" + str(endAfterMidnight) + " <= ? OR ((starttime+duration)%86400)+" + str(endAfterMidnight) + " <= ? ) " +  whereClause[condition,beforeMidnight,afterMidnight] + ");"
					if(i == 1):
						logging.debug("SQL-query: %s \n values: %s" % (countSql,values))
					try:
						self.cursor.execute(countSql, values)
						frequency = float(self.cursor.fetchone()[0]) #anzahl erfasster Activitäten im definierten Zeitraum
					except sqlite3.OperationalError,e:
						time.sleep(3)
						logging.error("%s, sql: %s, values %s" % (e,countSql,values)) 
					del countSql # throw fat string away
					#get alls days, which belongs to condition
					if(frequency>0):
						savedDays = self.getSavedDays(today,condition)
						offDays = self.getAbsences(t[i],interval,today,savedDays)
						probability = frequency/(len(savedDays)-offDays)
						logging.debug("Freq: %s : savedDays: %s : offDays: %s : prob %s" % (frequency,savedDays,offDays,probability))
					if(condition == 10):
						c10[i] = probability
				dbValues.append((condition,t[i],probability))
				#self.addProbability(condition,t[i],probability) # t = 603.259572029 sec
			#self.addProbabilities(dbValues) # t = 10.5220549107 sec
			#del dbValues[:]
		self.addProbabilities(dbValues) # t = 8.7100520134 sec
		del dbValues[:]
		del c10[:]
		del whereClause
		del t[:]
		logging.info("time for create probs: %s sec" % (time.time()-t1))

	"""
	writes frequency (probability) of an event in past for an timeslice with tolerance into database
	
	def addProbability(self,behaviorType, timeSliceStarttime, probability):
		try:
			self.cursor.execute("INSERT INTO probabilities (behavior_type, time_slice_starttime, probability) VALUES (?,?,?);", (behaviorType,timeSliceStarttime,probability))
			self.conn.commit()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
	"""
	
	"""
	add many probabilities at once, try to reduce time consumption of database operations
	"""
	def addProbabilities(self,dbValues):
		try:
			logging.debug("execute addProbabilities")
			self.cursor.executemany("INSERT INTO probabilities (behavior_type, time_slice_starttime, probability) VALUES (?,?,?);", dbValues)
			self.conn.commit()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
	
	
	"""
	deletes all entries from probabilities table, it's not neccessary to hold it over long time
	"""
	def truncProbabilities(self):
		try:
			self.cursor.execute("DELETE FROM probabilities;")
			self.conn.commit()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
	
	"""
	returns, how often a senior at a time wasn't at home
	we've got monitored days and times of absence
	an absence can extend over some minutes but also some days, means
	we take the concerning day and test, if senior was at home or not. 
	He wasn't at home, if we find records, which starts before day+starttime and ends after day+endtime
	@param int starttime
	@param int interval
	@param int today
	@param list savedDays
	@returns int
	"""
	def getAbsences(self,starttime,interval,today,savedDays):
		#per default, senior is all the time at home
		offDays = 0
		endtime = starttime + interval
		if (endtime >= 86400): #should never occur, if interval divider of 86400
			endtime = 86399
		for day in savedDays:
			#look for values in past -> <today
			#(day + starttime) and (day + endtime) must be between startAbsence and endAbsence 
			#count(*) should be always 1 
			try:
				self.cursor.execute("SELECT COUNT(*) FROM absence WHERE endAbsence <= ? AND startAbsence <= ? AND endAbsence >= ?;", (today,day+starttime,day+endtime))
				offDays += int(self.cursor.fetchone()[0]) #anzahl Abwesenheiten im definierten Zeitraum
			except sqlite3.OperationalError,e:
				time.sleep(3)
				logging.error(str(e))
		return offDays
	
	"""
	returns a list with last recent events
	@params int moment, current timestamp
	@return list
	take the timestamp and get the begin of actual time slice via modulo-operations
	then take this and get the three timeslices before
	
	"""
	def getRecentValues(self,moment):
		#get interval length
		interval = rc.config.getint('checkbehavior','interval')
		toleranceIntervals = rc.config.getint('checkbehavior','toleranceIntervals')
		#resultlist
		values = []
		#get time slice start for last recent values
		ctstart = moment - (moment % interval)
		#because the current timeslice isn't finished, we consider the slices before
		#get last recent values
		for i in range(ctstart - (2 * toleranceIntervals * interval), ctstart, interval):
			try:
				self.cursor.execute("SELECT DISTINCT COUNT(DISTINCT (starttime/86400)) FROM activity_log WHERE starttime >= ? OR starttime + duration >= ?;",(i, i))
				values.append(float(self.cursor.fetchone()[0])) #we will operate with floats later
			except sqlite3.OperationalError,e:
				time.sleep(3)
				logging.error(str(e))
		return values
			
		
	"""
	when recent values looks critical, get probabilities of sensor activity based on histical data
	get Values for every condition, without day of weeks (means every monday, tuesday, ...)
	"""
	def getProbabilities(self, moment):
		#get interval length
		interval = rc.config.getint('checkbehavior','interval')
		toleranceIntervals = rc.config.getint('checkbehavior','toleranceIntervals')
		#get time slice start for historical values, get actual daytime and strip away interval
		htstart = (moment - (moment % interval)) % 86400
		#list for value lists
		values = []	
		for condition in (10,15,17,20,30,40,50,60,70):
			#values per condition
			cvalues = []
			for i in range(htstart - (2 * toleranceIntervals * interval), htstart, interval):
				if(i < 0): #if i negative, then get get values of evening before
					i += 86400
				try:
					self.cursor.execute("SELECT probability FROM probabilities WHERE behavior_type = ? AND time_slice_starttime = ?;",(condition,i))
					res = self.cursor.fetchone()
					if (not res):
						prob = 0.0		
					else:
						prob = float(res[0])
					cvalues.append(prob)
				except sqlite3.OperationalError,e:
					time.sleep(3)
					logging.error(str(e))
			values.append(cvalues[:])
			del cvalues[:]
		return values
		

	
	"""
	Deletes everythin from tables activity_log, logged_days and absences, 
	that's older than observePeriod
	"""
	def delOldEntries(self,today):
		observePeriod = rc.config.getint('checkbehavior','observePeriod') #get observed period
		delTimestamp = today - (observePeriod * 86400) #and remove everything, which is older
		try:
			self.cursor.execute("DELETE FROM activity_log WHERE starttime+duration < ?;", (delTimestamp, ))
			self.cursor.execute("DELETE FROM absence WHERE endAbsence < ?;", (delTimestamp, ))
			self.cursor.execute("DELETE FROM logged_days WHERE logged_day < ?;", (delTimestamp, ))
			self.conn.commit()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
	
	"""
	inserts for every day one timestamp to table to track and count days, which where monitored
	"""
	def addDayRecord(self,currenttime):
		#strip away time, hold only timestamp for day
		try:
			self.cursor.execute("INSERT OR IGNORE INTO logged_days (logged_day) VALUES (?);", (currenttime - (currenttime % 86400),))
			self.conn.commit()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
	
	"""
	returns last inserted day
	"""
	def getLastDayRecord(self):
		try:
			self.cursor.execute("SELECT MAX(logged_day) FROM logged_days;")
			result = self.cursor.fetchone()[0]
			if result is None:
				lastLoggedDay = 0
			else:
				lastLoggedDay = int(result)
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
		return lastLoggedDay
			
	"""
	set times of absence
	it's neccessary to get right number of events and probabilities
	for example, if there recorded 30 days, but survived person goes out everey second day in evening, the maximal probability of an event is 50 %, with unoccured absence. When we can remove absence times from all days, probalitity of an event should be around 100 percent
	"""
	def addAbsence(self,starttime,endtime):
		#tests, if midnight occurs considering timezones
		try:
			self.cursor.execute("INSERT INTO absence (startAbsence, endAbsence) VALUES (?,?);", (starttime,endtime))
			self.conn.commit()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
	
	def truncatedb(self):
		self.cursor.execute("DELETE FROM probabilities;")
		self.cursor.execute("DELETE FROM activity_log")
		self.cursor.execute("DELETE FROM logged_days")
		self.cursor.execute("DELETE FROM absence")
		self.conn.commit()
	
	#visualisation
	"""
	returns all Activities
	@return list
	"""
	def getActivities4Vis(self):
		try:
			self.cursor.execute("SELECT starttime, starttime+duration FROM activity_log ;")
			activities = self.cursor.fetchall()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
		return activities
		
	"""
	returns all probabilities
	@return list
	"""
	def getProbabilities4Vis(self):
		try:
			self.cursor.execute("SELECT behavior_type, time_slice_starttime, probability FROM probabilities ;")
			probabilities = self.cursor.fetchall()
		except sqlite3.OperationalError,e:
			time.sleep(3)
			logging.error(str(e))
		return probabilities
	#end visualisation
		
	def closeDB(self):
		self.conn.close()
		
