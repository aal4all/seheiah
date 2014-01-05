#gst_sphinx_cli.py
#-*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 05.01.2013
@brief Speech recognition of seheiah

#	Modified from gst_sphinx_cli.py
# http://gitorious.org/code-dump/gst-sphinx-cli
# Copyright (c) 2012, Jacob Burbach <jmburbach@gmail.com>
#
# Modified from livedemo.py, part of pocketsphinx
# Copyright (c) 2008 Carnegie Mellon University.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#	Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer. Redistributions in binary
#   form must reproduce the above copyright notice, this list of conditions and
#   the following disclaimer in the documentation and/or other materials
#   provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
"""

#import threading
import logging #logfile
import os,time
import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst
from ConfigParser import SafeConfigParser

CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)

class GstSphinxCli(object): #object threading.Thread

	def __init__(self): #hmm, lm, dic
		#threading.Thread.__init__(self) #threading-class initialisieren
		#self.daemon = True
		hmm = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.get('speechrecognition','hmdir'))
		lm = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.get('speechrecognition','lm'))
		dic = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.get('speechrecognition','dict'))
		self.init_gst(hmm, lm, dic)
		
	def init_gst(self, hmm, lm, dic):
		#pulsesrc
		#self.pipeline = gst.parse_launch('pulsesrc device="' + config.get('speechrecognition','mic') + '" ! audioconvert ! audioresample ! vader name=vad auto-threshold=true ! pocketsphinx name=asr ! fakesink dump=1')
		#alsasrc
		self.pipeline = gst.parse_launch('alsasrc device=' + config.get('speechrecognition','mic') + ' ! queue ! audioconvert ! audioresample ! vader name=vader auto-threshold=true ! pocketsphinx name=asr ! fakesink dump=1')
		#lm=' + lm + ' dict=' + dic + ' hmm=' + hmm + ' 
		asr = self.pipeline.get_by_name('asr')
		asr.connect('partial_result', self.asr_partial_result)
		asr.connect('result', self.asr_result)
		asr.set_property("hmm", hmm)
		asr.set_property("lm", lm)
		asr.set_property("dict", dic)
		asr.set_property('configured', True)
		bus = self.pipeline.get_bus()
		bus.add_signal_watch()
		bus.connect('message::application', self.application_message)
		self.pipeline.set_state(gst.STATE_PLAYING)

	def asr_partial_result(self, asr, text, uttid):
		"""Forward partial result signals on the bus to the main thread."""
		struct = gst.Structure('partial_result')
		struct.set_value('hyp', text)
		struct.set_value('uttid', uttid)
		asr.post_message(gst.message_new_application(asr, struct))

	def asr_result(self, asr, text, uttid):
		"""Forward result signals on the bus to the main thread."""
		struct = gst.Structure('result')
		struct.set_value('hyp', text)
		struct.set_value('uttid', uttid)
		asr.post_message(gst.message_new_application(asr, struct))

	def application_message(self, bus, msg):
		"""Receive application messages from the bus."""
		msgtype = msg.structure.get_name()
		if msgtype == 'partial_result':
			self.partial_result(msg.structure['hyp'], msg.structure['uttid'])
		elif msgtype == 'result':
			self.final_result(msg.structure['hyp'], msg.structure['uttid'])

	def partial_result(self, hyp, uttid):
		""" handle partial result in `hyp' here """
		pass

	def final_result(self, hyp, uttid):
		""" handle final result `hyp' here """
		#hyp is unicode string
		#start Alarmcascade
		logging.debug('pocketsphinx:' + hyp + ' erkannt')
		if(u'SEHEIAH HILFE' in hyp):
			logging.info("SEHEIAH HILFE detected")
			print "SEHEIAH HILFE detected"
			self.messageToAlarmCascade('HILFE')
			#send Alarm-message to socket
		#start test
		#if(u'SEHEIAH TEST' in hyp):
			#logging.info("SEHEIAH TEST detected")
			#future project
		#interrupt alarmcascade in case of unexpected behavior
		if(u'SEHEIAH ALARM' in hyp):
			logging.info("SEHEIAH ALARM AUS detected")
			self.messageToAlarmCascade('ALARM AUS')
			#sends alarm aus
		#deactivate monitoring
		if(u'SEHEIAH BYE' in hyp):
			logging.info("SEHEIAH BYE BYE detected")
			self.setAbsence()	
	
	#set absence of monitored subject
	def setAbsence(self):
		try:
			presenceFile = open("/tmp/seheiah_presence", "w")
			try:
				presenceFile.write('0')
			except IOError:
				logging.error("couldn't write to file /tmp/seheiah_presence")
			finally:
				presenceFile.close()
		except IOError:
			logging.error("couldn't open file /tmp/seheiah_presence")
	
	#sends message to alarm cascade
	#future todo:DRY
	def messageToAlarmCascade(self,message):
		import socket
		import os, os.path
		if os.path.exists("/tmp/seheiah_alarm.sock"):
			client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) #DGRAM
			try:
				client.connect("/tmp/seheiah_alarm.sock")
				client.send(message)
			except socket.error:
				logging.error("Couldn't connect to socket /tmp/seheiah_alarm.sock")
			finally:
				client.close()
		else:
			logging.error("socket /tmp/seheiah_alarm.sock doesn't exists")
			
	
	def run(self):
		logging.info("Thread Pocketsphinx started")
		gobject.MainLoop().run()
