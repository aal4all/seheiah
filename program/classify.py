#classify.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 24.01.2014
@brief classificator for alarms
"""

import numpy as np
import logging
import readConfig as rc

class Classify():
	def __init__(self):
		self.thresholdProbability = rc.config.getfloat('classification','thresholdProbability')
		self.thresholdCosSimilarity = rc.config.getfloat('classification','thresholdCosSimilarity')
	
	"""
	check, if recent bahavior is conspicuous
	this is the case, if there no activity or a lot activity
	when there is no activity, the senior could lie anywhere and we have to check, if no activity at this time is normal
	when there is a lot activity, more than 3*interval lenght, the senior could fallen in shower, so we also have to check, if a lot aktivity is normal
	Is there only a litte bit activity, in one or two time slices, everything seems ok and we have to do nothing
	@param np.array recentBehavior
	@return bool
	"""
	def suspiciousBehavior(self, recentBehavior):
		"""
		length l (euclidic Norm, Skalarprodukt) of current behavior vector 
		if 0<||v||_2<||(1.0,1.0,1.0)||_2 everthing is fine
		||v||_2 = sqrt((v_1)^2 + (v_2)^2 + ... + (v_n)^2)
		
		"""
		lenghtV = np.linalg.norm(recentBehavior)
		logging.debug("aktueller Vektor: %s La:nge: %s" % (recentBehavior, lenghtV))
		if(lenghtV == 0 or lenghtV == np.sqrt(3.0)):
			return True
		else:
			return False
	
	"""
	check, if usually bahavior was different from recent
	@param numpy array  recentBehavior
	@param numpy array usuallyBehavior
	return bool
	"""
	def behaviorDiffCos(self, recentBehavior, usuallyBehavior):
		thresholdProbability = rc.config.getfloat('classification','thresholdProbability')
		#clean data, remove noise, means everything < thresholdProbability, because this were rare events 
		usuallyBehavior[usuallyBehavior < thresholdProbability] = 0.0
		usuallyBehavior[usuallyBehavior >= thresholdProbability] = 1.0
		lenghtV = np.linalg.norm(recentBehavior)
		similarity = 0
		for behavior in usuallyBehavior:
			if(lenghtV == 0):
				if(np.linalg.norm(behavior) != lenghtV): #wenn normalerweise Wasser verbraucht wird ...
					return True #Alarmwert
			else:
				if(np.linalg.norm(behavior) > 0):
					similarity = max(self.cosSimilarity(recentBehavior,behavior), similarity) #cos(v_curr,v_his)
					#Cosinusähnlichkeit in eigene Methode
					#Distanz ebenfalls
		if(similarity < self.thresholdCosSimilarity):
			return True
		else:
			return False

	
	"""
	calculate cosinus similarity between two vectors
	@param numpy array
	@param numpy array
	@return float
	"""
	def cosSimilarity(self, vector1, vector2):
		return np.dot(vector1,vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
	
	"""
	calculate euclidian distance between two points
	@param numpy array
	@param numpy array
	@return float 
	"""
	def distance(self, pt1, pt2):
		pass
	
