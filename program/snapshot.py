#alarmcascade.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 02.01.2014
@brief initiate alarm cascade
"""
import sys
import cv
#eigene klassen

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
	cv.SaveImage(snapshotFilename, img)
