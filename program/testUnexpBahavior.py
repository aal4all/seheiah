#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
testUnexpBahavior.py
@author Falko Benthin
@Date 02.09.2013
@brief initiate unexpected behavior for test dases
"""
import socket
import os, os.path
if os.path.exists("/tmp/seheiah_alarm.sock"):
	client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) #DGRAM
	client.connect("/tmp/seheiah_alarm.sock")
	client.send("UNEXPECTED BEHAVIOR")
	client.close()
else:
	print "Couldn't Connect!"
