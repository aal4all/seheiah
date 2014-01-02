#alarmcascade.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 02.01.2014
@brief initiate alarm cascade
"""
import sys
import cv
from ConfigParser import SafeConfigParser
#eigene klassen


#read variables
CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)

snapshotFilename = sys.argv[1]

my_width = 320
my_height = 240
print "makeSnapshot"
#initialise webcam  (cam 0)
capture = cv.CaptureFromCAM(0)
if not capture:
	print "capture-Fehler"
else:
	#bildeigenschaften
	cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, my_height)
	cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, my_width)
img = cv.QueryFrame(capture)
if not img:
	print "imagefehler"
else:
	#self.snapshotFilename = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.get('alarmcascade','snapshotpath'))+str(int(time.time()))+".jpg"
	cv.SaveImage(snapshotFilename, img)
