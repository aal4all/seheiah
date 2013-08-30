#gst_sphinx_cli.py
#-*- coding: utf-8 -*-

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

import threading
import logging #logfile

import gobject
import pygst
pygst.require('0.10')
import gst
from ConfigParser import SafeConfigParser

CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)

class GstSphinxCli(threading.Thread): #object

	def __init__(self): #hmm, lm, dic
		threading.Thread.__init__(self) #threading-class initialisieren
		self.daemon = True
				
		gobject.threads_init()
		
		hmm = config.get('speechrecognition','hmdir')
		lm = config.get('speechrecognition','lm')
		dic = config.get('speechrecognition','dict')
		self.init_gst(hmm, lm, dic)
		
	def init_gst(self, hmm, lm, dic):
		self.pipeline = gst.parse_launch('pulsesrc device="alsa_input.usb-046d_0825_6FD11520-02-U0x46d0x825.analog-mono" ! audioconvert ! audioresample ! vader name=vad auto-threshold=true ! pocketsphinx name=asr ! fakesink')
		"""alsasrc device=hw:1,0 ! "audio/x-raw-int,channels=1,rate=16000" ! audioconvert ! audioresample ! vader name=vad auto-threshold=true ! pocketsphinx name=asr ! fakesink"""
		#lm=' + lm + ' dict=' + dic + ' hmm=' + hmm + ' 
		asr = self.pipeline.get_by_name('asr')
		asr.connect('partial_result', self.asr_partial_result)
		asr.connect('result', self.asr_result)
		print "HMM" + hmm + ", LM: " + lm + ", DIC " + dic
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
		"PARTIAL RESULT: ", hyp
		pass

	def final_result(self, hyp, uttid):
		""" handle final result `hyp' here """
		print "*************************************"
		print "FINAL RESULT: ", hyp
		pass
	
	
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
	
	def run(self):
		#set logging
		logfile = config.get('logging','logfile')
		loglevel = config.getint('logging','loglevel')
		logging.basicConfig(filename=logfile,filemode = 'a',level=loglevel,format = "%(threadName)s: %(asctime)s  %(name)s [%(levelname)-8s] %(message)s")
		logging.info("Thread pocketsphinx started")
		
		gobject.MainLoop().run()
