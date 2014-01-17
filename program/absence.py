#absence.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 17.01.2014
@brief reads and writes absence file
"""

import time
import logging
import logdb

class Absence():
	
	def __init__(self):
		self.absenceFileName = "/tmp/seheiah_absence"
		#intervals to considering in seconds
	"""
	sets absence
	"""
	def set(self,absent):
		try:
			absenceFile = open(self.absenceFileName, "r+")
			if (absent == 0): #when home again
				try:
					starttime = int(absenceFile.read())
				except IOError:
					logging.error("couldn't read from file" + self.absenceFileName)
				#logging to database
				db = logdb.logDB()
				db.addAbsence(starttime,int(time.time()))
				db.closeDB()
			try:
				absenceFile.seek(0)
				absenceFile.write(str(absent))
				absenceFile.truncate()
			except IOError:
				logging.error("couldn't write to file " + self.absenceFileName)
			finally:
				absenceFile.close()
		except IOError:
			logging.error("couldn't open file " + self.absenceFileName)
	
	#checks via file, if subject at home
	def get(self):
		try:
			absenceFile = open(self.absenceFileName, "r")
			try:
				absenceValue = int(absenceFile.read())
			except IOError:
				logging.error("couldn't read from file" + self.absenceFileName)
			finally:
				absenceFile.close()
		except IOError:
			logging.error("file " + self.absenceFileName + " doesn't exists")
		return bool(absenceValue)

