#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Global parameters for PSX """

import os

# communication
#~ DATA = "DATA\r\n"
#~ SCENARIO = "SCENARIO\r\n"
CONTEXT = "CONTEXT"
#~ READY = "READY\r\n"
#~ DONE = "DONE\r\n"
#~ RESULTS = "RESULTS\r\n"
#~ STATS = "STATS\r\n"
#~ PROG = "PROGRESS"
STATUS = "STATUS"
RUNNING = "RUNNING"
PARAM = "PARAM"
MATRIX = "MATRIX"
RUN = "RUN\r\n"
#~ QUIT = "QUIT\r\n"

# files and paths
IPATH = 'data/input.xml'
PATH = os.path.dirname(os.path.realpath(__file__)) + "/"
