#logdb.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 05.02.2014
@brief Testcases Ompadroids
"""

import ompadroid
import numpy as np
ompa = ompadroid.Ompadroid()
runs = 100

#ompadroid mit militärischer Präzision und Hang zum Wassersparen
deadvalues = []
fallenvalues = []
for i in range(0,runs):
	ompa.createData(180, False)
	deadvalues.append(ompa.testBehavior(True))
	fallenvalues.append(ompa.testBehavior(False))
deadOmpaTypeMilPrecSaver = np.asarray(deadvalues)
fallenOmpaTypeMilPrecSaver = np.asarray(fallenvalues)
print "untätiger Ompadroid mit militärischer Präzision und Hang zum Wassersparen"
print "   Testläufe",deadOmpaTypeMilPrecSaver.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(deadOmpaTypeMilPrecSaver)
print "   Min ",np.min(deadOmpaTypeMilPrecSaver)," Max ", np.max(deadOmpaTypeMilPrecSaver)
print "in Dusche gestürzter Ompadroid mit militärischer Präzision und Hang zum Wassersparen"
print "   Testläufe",fallenOmpaTypeMilPrecSaver.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(fallenOmpaTypeMilPrecSaver)
print "   Min ",np.min(fallenOmpaTypeMilPrecSaver)," Max ", np.max(fallenOmpaTypeMilPrecSaver)


#untätiger Ompadroid mit militärischer Präzision
del deadvalues[:]
del fallenvalues[:]
for i in range(0,runs):
	ompa.createData(300, False)
	deadvalues.append(ompa.testBehavior(True))
	fallenvalues.append(ompa.testBehavior(False))
deadOmpaTypeMilPrec = np.asarray(deadvalues)
fallenOmpaTypeMilPrec = np.asarray(fallenvalues)
print "untätiger Ompadroid mit militärischer Präzision "
print "   Testläufe",deadOmpaTypeMilPrec.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(deadOmpaTypeMilPrec)
print "   Min ",np.min(deadOmpaTypeMilPrec)," Max ", np.max(deadOmpaTypeMilPrec)
print "in Dusche gestürzter Ompadroid mit militärischer Präzision "
print "   Testläufe",fallenOmpaTypeMilPrec.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(fallenOmpaTypeMilPrec)
print "   Min ",np.min(fallenOmpaTypeMilPrec)," Max ", np.max(fallenOmpaTypeMilPrec)


#knickriger Amtsschimmelompadroid
del deadvalues[:]
del fallenvalues[:]
for i in range(0,runs):
	ompa.createData(180, True)
	deadvalues.append(ompa.testBehavior(True))
	fallenvalues.append(ompa.testBehavior(False))
deadOmpaTypeMiserlyOfficial = np.asarray(deadvalues)
fallenOmpaTypeMiserlyOfficial = np.asarray(fallenvalues)
print "untätiger knickriger Amtsschimmelompadroid"
print "   Testläufe",deadOmpaTypeMiserlyOfficial.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(deadOmpaTypeMiserlyOfficial)
print "   Min ",np.min(deadOmpaTypeMiserlyOfficial)," Max ", np.max(deadOmpaTypeMiserlyOfficial)
print "in Dusche gestürzter knickriger Amtsschimmelompadroid"
print "   Testläufe",fallenOmpaTypeMiserlyOfficial.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(fallenOmpaTypeMiserlyOfficial)
print "   Min ",np.min(fallenOmpaTypeMiserlyOfficial)," Max ", np.max(fallenOmpaTypeMiserlyOfficial)

#Amtsschimmelompadroid
del deadvalues[:]
del fallenvalues[:]
for i in range(0,runs):
	ompa.createData(300, True)
	deadvalues.append(ompa.testBehavior(True))
	fallenvalues.append(ompa.testBehavior(False))
deadOmpaTypeOfficial = np.asarray(deadvalues)
fallenOmpaTypeOfficial = np.asarray(fallenvalues)
print "untätiger Amtsschimmelompadroid"
print "   Testläufe",deadOmpaTypeOfficial.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(deadOmpaTypeOfficial)
print "   Min ",np.min(deadOmpaTypeOfficial)," Max ", np.max(deadOmpaTypeOfficial)
print "in Dusche gestürzter Amtsschimmelompadroid"
print "   Testläufe",fallenOmpaTypeOfficial.shape[0]
print "   Durchschnitt erkannte Alarme ", np.mean(fallenOmpaTypeOfficial)
print "   Min ",np.min(fallenOmpaTypeOfficial)," Max ", np.max(fallenOmpaTypeOfficial)
