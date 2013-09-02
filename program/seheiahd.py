#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author Falko Benthin
@Date 02.09.2013
@brief seheiah daemion, which starts the threads
"""

import serial, sys, time, os
from daemon import runner
import threading
import logging
from ConfigParser import SafeConfigParser
#eigene Klassen
import monitor
import checkBehavior
import alarmcascade
import gstSphinxCli

#read variables
CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)

class Seheiah(object):
	#initialisieren
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path =  '/tmp/seheiah.pid'
		self.pidfile_timeout = 7
		#set logfile
		self.logfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.get('logging','logfile'))
		
	
	#at the start of seheiah subject is at home
	def setPresence(self):
		try:
			presenceFile = open("/tmp/seheiah_presence", "w")
			try:
				presenceFile.write('1')
			except IOError:
				logging.error("couldn't write to file /tmp/seheiah_presence")
			finally:
				presenceFile.close()
		except IOError:
			logging.error("couldn't open file /tmp/seheiah_presence")
	
	#als daemon laufen
	def run(self):
		#set presence
		self.setPresence()
		#set logging
		loglevel = config.getint('logging','loglevel')
		logging.basicConfig(filename=self.logfile,filemode = 'w',level=loglevel,format = "%(threadName)s: %(asctime)s  %(name)s [%(levelname)-8s] %(message)s")
		logging.info("seheiahd started")
		
		mythreads = []
		mon = monitor.Monitor()
		alarm = alarmcascade.AlarmCascade()
		check = checkBehavior.Check(mon)
		pocketsphinx = gstSphinxCli.GstSphinxCli()
		mythreads.append(mon)
		mythreads.append(alarm)
		mythreads.append(check)
		mythreads.append(pocketsphinx)
		
		for thread in mythreads:
			thread.start()

		
		while True:
			time.sleep(0.01)

app = Seheiah()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

