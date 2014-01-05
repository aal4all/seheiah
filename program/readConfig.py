#readConfig.py
# -*- coding: utf-8 -*-

"""
@author Falko Benthin
@Date 05.01.2014
@brief reads varaibles from config file
"""

from ConfigParser import SafeConfigParser

#read variables
CONFIGFILE = "seheiah.cfg"
config = SafeConfigParser()
config.read(CONFIGFILE)
