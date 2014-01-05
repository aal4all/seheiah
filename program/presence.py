#presence.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 05.01.2014
@brief reads and writes presence file
"""

class Presence():
	
	def __init__(self):
		self.presenceFileName = "/tmp/seheiah_presence"
	"""
	sets presence
	"""
	def set(self,present):
		try:
			presenceFile = open(self.presenceFileName, "w")
			try:
				presenceFile.write(str(present))
			except IOError:
				logging.error("couldn't write to file " + self.presenceFileName)
			finally:
				presenceFile.close()
		except IOError:
			logging.error("couldn't open file " + self.presenceFileName)
	
	#checks via file, if subject at home
	def get(self):
		presenceValue = True
		try:
			presenceFile = open(self.presenceFileName, "r")
			try:
				presenceValue = int(presenceFile.read())
			except IOError:
				logging.error("couldn't read from file" + self.presenceFileName)
			finally:
				presenceFile.close()
		except IOError:
			logging.error("file " + self.presenceFileName + " doesn't exists")
		return bool(presenceValue)

