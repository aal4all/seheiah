#playAudio.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 04.10.2014
@brief plays audiofiles
"""

import pygame
import sys
import logging

class playAudio():
	def __init__(self):
		pygame.mixer.pre_init(16000,-16,1,1024)
		pygame.mixer.init()
		pygame.mixer.music.set_volume(1.0)
	
	def __del__(self):
		pygame.mixer.quit()
	
	def playMp3(self,file):
		try:
			pygame.mixer.music.load(file)
		except Exception, e:
			logging.error("playAudio error %s" % e)
		try:
			pygame.mixer.music.play(0)
			while pygame.mixer.music.get_busy():
				pygame.time.Clock().tick(10)
		except Exception, e:
			logging.error("playAudio error %s" % e)

if __name__ == "__main__":
	pa = playAudio()
	fileName = sys.argv[1]
	pa.playMp3(fileName)
