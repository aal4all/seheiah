#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author Falko Benthin
@Date 02.09.2013
@brief seheiah daemion, which starts the threads
"""

import time, os
from daemon import runner
import threading
import logging
#eigene
import monitor
import checkBehavior
import alarmcascade
import gstSphinxCli
import readConfig as rc

class Seheiah(object):
	#initialisieren
	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path =  '/tmp/seheiah.pid'
		self.pidfile_timeout = 7
		#set logfile
		self.logfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rc.config.get('logging','logfile'))
		
	#als daemon laufen
	def run(self):
		#set logging
		loglevel = rc.config.getint('logging','loglevel')
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
		#mythreads.append(pocketsphinx)
		
		for thread in mythreads:
			thread.start()
		pocketsphinx.run()
		
		while True:
			time.sleep(0.01)
		
		pocketsphinx.quit()
		
app = Seheiah()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()

