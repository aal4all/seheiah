#visualize.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 04.02.2014
@brief visualize activities
"""

import logdb
import numpy as np
import matplotlib
matplotlib.use("AGG") #to plot directly in file
import matplotlib.pyplot as plt
import time
import readConfig as rc

db = logdb.logDB()

#get Activities
activities = np.asarray(db.getActivities4Vis())

#combine arrays to get all start and end time values, must be somthing like xs0,0->xs0,1->xe0,1->xe0,0
longdays = np.zeros(activities.shape[0]*4).astype('int')
longtimes = np.zeros(activities.shape[0]*4)
longvalues = np.zeros(activities.shape[0]*4).astype('int')
for i in range(0,activities.shape[0]):
	for j in range(0,4):
		longdays[i*4+j] = activities[i][0]/86400
		if(j < 2):
			longtimes[i*4+j] = activities[i][0]%86400/3600.0
		else:
			longtimes[i*4+j] = activities[i][1]%86400/3600.0
		if(0 < j < 3): #if y 1 or 2
			longvalues[i*4+j] = 1
		else: #fist and last
			longvalues[i*4+j] = 0

days =  db.getSavedDays(int(time.time()))
#End getactivities
#getprobabilities
probabilities = np.asfarray(db.getProbabilities4Vis())
conditions = [10,15,17,20,30,40,50,60,70,71,72,73,74,75,76,77]
probYLabelDic = {
	10 : "daily",
	15 : "working days",
	17 : "weekend days",
	20 : "every 2 days",
	30 : "every 3 days",
	40 : "every 4 days",
	50 : "every 5 days",
	60 : "every 6 days",
	70 : "weekly",
	71 : "mondays",
	72 : "tuesdays",
	73 : "wednesdays",
	74 : "thursday",
	75 : "fridays",
	76 : "saturdays",
	77 : "sundays"
	}
#create data arrays
pconditions = probabilities[:,0].astype('int') #select criteria
ptimes = probabilities[:,1]/3600.0 #timeslices
pprobs = probabilities[:,2] #probalilities
#end getprobabilities

f, ax = plt.subplots(len(days),1, sharex=True)
#behavior plots
ax[0].set_title("water flow within the last "+str(len(days))+" days")
for i in range(0, len(days)):
	x = longtimes[longdays==days[i]/86400]
	y = longvalues[longdays==days[i]/86400]
	#ax[i].axes.get_yaxis().set_visible(False)
	#ax1.set_yticklabels(axis='y',which='both', left='off', right='off')
	ax[i].set_yticks([]) 
	ax[i].set_ylabel(time.strftime('%y-%m-%d (%w)',time.gmtime(days[i] - time.timezone)),rotation=0, fontsize='small')
	ax[i].set_xticks(range(0,24))
	ax[i].set_xticklabels(range(0,24),rotation=0,fontsize=8)
	#ax[i].set_xlabel("Time")
	ax[i].plot(x,y)
ax[len(days)-1].set_xlabel("Time")
plt.figure(1)
filename = "events_" + time.strftime('%y%m%d',time.gmtime(days[i] - time.timezone))+".png"
plt.savefig(filename, dpi=150, bbox_inches=0)

#probabilities plots
f, bx = plt.subplots(len(conditions),1, sharex=True)
bx[0].set_title("Probabilities of waterflow based on history for "+time.strftime('%y-%m-%d (%w)',time.gmtime()))
for j in range(0,len(conditions)):
	x = ptimes[pconditions == conditions[j]]
	y = pprobs[pconditions == conditions[j]]
	bx[j].set_ylim(0,1.4)
	bx[j].set_yticks([0,1])
	bx[j].set_yticklabels([0,1],rotation=0,fontsize=8)
	#bx[j].minorticks_on()
	bx[j].set_ylabel("P("+probYLabelDic[conditions[j]]+")",rotation=0, fontsize='small')
	bx[j].set_xticks(range(0,24))
	bx[j].set_xticklabels(range(0,24),rotation=0,fontsize=8)
	bx[j].vlines(x, [0], y)
	bx[j].plot(np.array([0,24]),np.array([1,1]),'r-')
	bx[j].plot(np.array([0,24]),np.array([rc.config.getfloat('classification','thresholdProbability'),rc.config.getfloat('classification','thresholdProbability')]),'b-')
bx[len(conditions)-1].set_xlabel("Time")
plt.figure(2)
filename = "probs_" + time.strftime('%y%m%d',time.gmtime(days[i] - time.timezone))+".png"
plt.savefig(filename, dpi=150, bbox_inches=0)
#plt.show()
