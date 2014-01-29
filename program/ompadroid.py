#ompadroid.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 26.01.2014
@brief fills database with regulary events, to test the classifiers
In time of testing Seheiah isn't able to collect event data reliably
"""
import sqlite3, os, time, random
import readConfig as rc

class Ompadroid():
	def __init__(self):
		self.db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rc.config.get('logdb','database'))
	
	"""
	backups original database
	"""
	def backupdb(self):
		dbbackup = self.db + ".backup"
		os.system ("cp %s %s" % (self.db, dbbackup))
	
	"""
	restores original database
	"""
	def restoredb(self):
		dbbackup = self.db + ".backup"
		os.system ("mv %s %s" % (dbbackup, self.db))
	
	def truncatedb(self):
		conn = sqlite3.connect(self.db, timeout=10)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM probabilities;")
		cursor.execute("DELETE FROM activity_log")
		cursor.execute("DELETE FROM logged_days")
		cursor.execute("DELETE FROM absence")
		conn.commit()
		conn.close()
	
	"""
	fills db with historical data, so that Seheiah within few minutes after given time should detect unexpected behavior 
	@param int daycondition:
		10 daily
		20 every two days
		30 every three days
		40 every four days
		50 every five days
		60 every six days
		70 weekly
	@param int daytime: time of day, default: next event startx in +interval seconds
	@param int duration
	@param bool withTolerance: events occurs with torlerances
	"""
	def createData(self, daytime, duration, withTolerance):
		self.backupdb()
		self.truncatedb()
		conn = sqlite3.connect(self.db, timeout=10)
		cursor = conn.cursor()
		today = int(time.time())-(int(time.time()) % 86400)
		observePeriod = rc.config.getint('checkbehavior','observePeriod')
		interval = rc.config.getint('checkbehavior','interval')
		toleranceIntervals = rc.config.getint('checkbehavior','toleranceIntervals')
		if (daytime>86400):
			daytime = daytime % 86400
		#generate data
		dayinterval = {
			10 : 1, #daily
			20 : 2, #every 2 days
			30 : 3, #every 3 days
			40 : 4, #every 4 days
			50 : 5, #every 5 days
			60 : 6, #every 6 days
			70 : 7, #weekly
			}
		for day in range(today - (observePeriod * 86400),today,86400):
			print day, ", ", type(day)
			if(withTolerance):
				tolerance=random.randint(-interval*toleranceIntervals, interval*toleranceIntervals) 
			else:
				tolerance = 0
			cursor.execute("INSERT INTO logged_days (logged_day) VALUES (?);",(day,))
			cursor.execute("INSERT INTO activity_log (starttime,duration) VALUES (?,?);",(day + (daytime + interval*(toleranceIntervals+1)) + tolerance,duration + random.randint(-duration/2, duration/2)))
		conn.commit()
		conn.close()
		
			
			
			
