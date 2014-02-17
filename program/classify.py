#classify.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 24.01.2014
@brief classificator for alarms
"""

import numpy as np
#import scipy as sp
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
		if(lenghtV == 0.0 or lenghtV == np.sqrt(1.0*recentBehavior.shape[0])):
			return True
		else:
			return False
	
	"""
	check, if usually bahavior was different from recent, clean ans smooth values first
	@param numpy array  recentBehavior
	@param numpy array usuallyBehavior
	return bool
	"""
	def behaviorDiffCos(self, recentBehavior, usuallyBehavior):
		thresholdProbability = rc.config.getfloat('classification','thresholdProbability')
		#clean data, remove noise, means everything < thresholdProbability, because this were rare events 
		usuallyBehavior[usuallyBehavior < thresholdProbability] = 0.0
		usuallyBehavior[usuallyBehavior >= thresholdProbability] = 1.0
		lenghtRB = np.linalg.norm(recentBehavior)
		result = False	#per default thers no strange behavior	
		#checks, if senior normally has water consumption
		if(lenghtRB == 0.0):
			norms = []
			for behavior in usuallyBehavior:
				norms.append(np.linalg.norm(behavior))
			if(max(norms) > lenghtRB):
				result = True
		#otherwise checks, if senior normally has water consumption over long duration		
		else:
			similarity = [] # otherwise
			for behavior in usuallyBehavior:
				if(np.linalg.norm(behavior) > 0.0):
					similarity.append(self.cosSimilarity(recentBehavior,behavior))
				else: #avoid division through zero
					similarity.append(0.0)
			if(max(similarity) < self.thresholdCosSimilarity):
				result = True
		return result

	
	"""
	calculate cosinus similarity between two vectors
	@param numpy array
	@param numpy array
	@return float
	"""
	def cosSimilarity(self, vector1, vector2):
		return np.dot(vector1,vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
		#return sp.spatial.distance.cosine(vector1, vector2)
	
	"""
	calculate euclidian distance between two points
	@param numpy array
	@param numpy array
	@return float 
	"""
	def distance(self, pt1, pt2):
		pass
	
