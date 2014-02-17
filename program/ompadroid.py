#ompadroid.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 05.02.2014
@brief fills database with regulary events, to test the classifiers
In time of testing Seheiah isn't able to collect event data reliably
"""
import time, random
import numpy as np
import logdb
import readConfig as rc
import classify

class Ompadroid():
	def __init__(self):
		self.db = logdb.logDB()
		self.classify = classify.Classify()
		
	"""
	backups original database
	
	def backupdb(self):
		dbbackup = self.db + ".backup"
		os.system ("cp %s %s" % (self.db, dbbackup))
	"""
	"""
	restores original database
	
	def restoredb(self):
		dbbackup = self.db + ".backup"
		os.system ("mv %s %s" % (dbbackup, self.db))
	"""
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
	def createData(self, duration, withTolerance):
		#self.backupdb()
		self.db.truncatedb()
		today = int(time.time())-(int(time.time()) % 86400)
		observePeriod = rc.config.getint('checkbehavior','observePeriod')
		interval = rc.config.getint('checkbehavior','interval')
		toleranceIntervals = rc.config.getint('checkbehavior','toleranceIntervals')
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
			self.db.addDayRecord(day)
			for daytime in range(8*3600, 20*3600+1,3600):
				if(withTolerance):
					tolerance=random.randint(-interval*toleranceIntervals, interval*toleranceIntervals) 
				else:
					tolerance = 0
				self.db.add_log(day + daytime + tolerance, duration + random.randint(-duration/2, duration/2))
		self.db.createProbabilities()
	
	#erstellt Vector für zurückliegenden Zeitraum
	#rechnet Toleranz mit rein
	def getUsuallyVector(self,daytime):		
		usuallyVector = np.asarray(self.db.getProbabilities(daytime))
		return 	usuallyVector
	
	#testet, ob abweichendes Verhalten bei Inaktivität zero = true oder übermäßig langem Wasserfluss  zero = false erkannt wird
	def testBehavior(self,zero):
		interval = rc.config.getint('checkbehavior','interval')
		toleranceIntervals = rc.config.getint('checkbehavior','toleranceIntervals')
		starttime = 8*3600 #start in the morning
		recentBehavior = np.asarray(self.db.getRecentValues(starttime))
		if(zero):
			recentBehavior[:] = 0.0
		else:
			recentBehavior[:] = 1.0
		emergency = 0 #counter for emergency
		alarms = 0 # for inactivity should be 20 alarms at the end, for activity it should be something about 
		for daytime in range(starttime,21*3600, interval):
			usuallyBehavior = self.getUsuallyVector(daytime)
			
			if(self.classify.behaviorDiffCos(recentBehavior, usuallyBehavior)):
				emergency += 1
				#print recentBehavior
				#print usuallyBehavior
				#print emergency
			else:
				emergency = 0
		
			if(emergency >= (toleranceIntervals * 2)): #Alarm auslösen
				#print recentBehavior
				#print usuallyBehavior
				alarms += 1
				#reset alarm counter
				emergency = 0
		
		return alarms
			

