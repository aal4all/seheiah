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


import logging #logfile
import os,time
import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst
#own
import readConfig as rc
import presence
import playAudio

class GstSphinxCli(object):

	def __init__(self): 
		#hmm, lm, dic
		"""
		hmm = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rc.config.get('speechrecognition','hmdir'))
		lm = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rc.config.get('speechrecognition','lm'))
		dic = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), rc.config.get('speechrecognition','dict'))
		"""
		hmm = rc.config.get('general','seheiahPath') + rc.config.get('speechrecognition','hmdir')
		lm = rc.config.get('general','seheiahPath') + rc.config.get('speechrecognition','lm')
		dic = rc.config.get('general','seheiahPath') + rc.config.get('speechrecognition','dict')
		self.presence = presence.Presence()
		#commands for speech recognition
		self.cmdHelp = unicode(rc.config.get('speechrecognition','cmdHelp'))
		self.cmdAlarmOff = unicode(rc.config.get('speechrecognition','cmdAlarmOff'))
		#self.cmdTest = unicode(rc.config.get('speechrecognition','cmdTest'))
		self.cmdBye = unicode(rc.config.get('speechrecognition','cmdBye'))
		
		self.init_gst(hmm, lm, dic)
		
		#load playaudio
		self.pa = playAudio.playAudio()
		
	def init_gst(self, hmm, lm, dic):
		#pulsesrc
		#self.pipeline = gst.parse_launch('pulsesrc device="' + config.get('speechrecognition','mic') + '" ! audioconvert ! audioresample ! vader name=vad auto-threshold=true ! pocketsphinx name=asr ! fakesink dump=1')
		#alsasrc
		self.pipeline = gst.parse_launch('alsasrc device=' + rc.config.get('speechrecognition','mic') + ' ! queue ! audioconvert ! audioresample ! vader name=vader auto-threshold=true ! pocketsphinx name=asr ! fakesink dump=1')
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
		logging.debug('pocketsphinx:' + hyp + ' erkannt')
		#start Alarmcascade
		if(self.cmdHelp in hyp):
			logging.info(self.cmdHelp.encode() + " detected")
			self.messageToAlarmCascade('HILFE')
			#send Alarm-message to socket
		#start test
		#if(self.cmdTest in hyp):
			#logging.info(self.cmdTest.encode() + " detected")
			#future project
		#interrupt alarmcascade in case of unexpected behavior
		if(self.cmdAlarmOff in hyp):
			logging.info(self.cmdAlarmOff.encode() + " detected")
			self.messageToAlarmCascade('ALARM AUS')
			#sends alarm aus
		#deactivate monitoring
		if(self.cmdBye in hyp):
			logging.info(self.cmdBye.encode() + " detected")
			mp3file = rc.config.get('general','seheiahPath') + rc.config.get('audiofiles','disableMonitoring')
			self.pa.playMp3(mp3file)
			self.presence.set(0)	

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
