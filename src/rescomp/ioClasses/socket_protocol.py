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
	''' thread event communication management '''
	def wrapper(*args, **kw):
		args[0].eventGo.wait()
		return f(*args, **kw)
		args[0].eventGo.clear()
	return wrapper

def sending_event(f):
	''' thread event communication management '''
	def wrapper(*args, **kw):
		print("sending data to server")
		args[0].eventCanSend.wait()
		print("waiting for eventCanSend")
		args[0].eventCanSend.clear()
		print("clear")
		f(*args, **kw)
		print("done")
		args[0].eventCanSend.set()
		print("setting eventCanSend")
	return wrapper


#
#---
# Parameters
#------------------------

PARAMETERS = "DATA PARAMETERS {} {}\r\n" # size and parameters id
SCENARIO = "DATA SCENARIO {}\r\n" # size
READY = "READY\r\n"
DONE = "DONE\r\n"
RESULTS = "RESULTS\r\n"
STATS = "STATS\r\n"
PROG = "PROGRESS"
RUN = "RUN\r\n"
QUIT = "QUIT\r\n"
HELLO = "HELLO\r\n"
MATRIX = "DATA MATRIX {} {}\r\n" # size then identifier
BYE = "BYE\r\n"
