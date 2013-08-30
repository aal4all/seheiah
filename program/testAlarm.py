#!/usr/bin/python
# -*- coding: utf-8 -*-
#testAlarm.py
#löst probehalter Alarm aus
import socket
import os, os.path
if os.path.exists("/tmp/seheiah_alarm.sock"):
	client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) #DGRAM
	client.connect("/tmp/seheiah_alarm.sock")
	client.send("ALARM")
	client.close()
else:
	print "Couldn't Connect!"
