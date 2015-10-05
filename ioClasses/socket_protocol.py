#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Protocol wrappers and parameters for SocketComm """

import socket


#
#---
# Wrappers
#------------------------

def timeoutErr(f):
	''' socket timeout management '''
	def wrapper(*args, **kw):
		try:
			return f(*args, **kw)
		except socket.timeout as msg:
			print("socket message: {}".format(msg))
	return wrapper

def go_event(f):
	#~ print("sending to client...")
	''' thread event communication management '''
	def wrapper(*args, **kw):
		args[0].eventGo.wait()
		return f(*args, **kw)
		args[0].eventGo.clear()
	return wrapper

def sending_event(f):
	#~ print("sending data to server")
	''' thread event communication management '''
	def wrapper(*args, **kw):
		args[0].eventCanSend.wait()
		args[0].eventCanSend.clear()
		return f(*args, **kw)
		args[0].eventCanSend.set()
	return wrapper


#
#---
# Parameters
#------------------------

DATA = "DATA\r\n"
SCENARIO = "SCENARIO\r\n"
READY = "READY\r\n"
DONE = "DONE\r\n"
RESULTS = "RESULTS\r\n"
STATS = "STATS\r\n"
PROG = "PROGRESS"
RUN = "RUN\r\n"
QUIT = "QUIT\r\n"
HELLO = "HELLO\r\n"
MATRIX = "MATRIX"
BYE = "BYE\r\n"
