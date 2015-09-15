#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Socket client """

import socket
import time
import threading



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

def wait_clear_event(event):
	''' thread event communication management '''
	def decorator(func):
		def wrapper(*args, **kw):
			event.wait()
			return f(*args, **kw)
			event.clear()
		return wrapper
	return decorator

def wait_clear_set_event(event):
	''' thread event communication management '''
	def decorator(func):
		def wrapper(*args, **kw):
			event.wait()
			even.clear()
			return f(*args, **kw)
			event.set()
		return wrapper
	return decorator


#
#---
# Socket communicator
#------------------------

class SocketComm(object):
	
	def __init__(self, lstSrvHost, nTimeout):
		# socket
		self.socket = None
		self.timeout = nTimeout
		self.tcpHost, self.tcpPort = lstSrvHost[0], lstSrvHost[1]
		# data
		self.strBuffer = ""
		self.results = None
		self.stats = []
		self.maxProgress = 0
		self.bRunClient = True
		self.bRunServer = True
		# threads and processes communication
		self.connectionClient = None
		self.threadClient = threading.Thread(target=self.thread_client)
		self.threadServer = threading.Thread(target=self.thread_server)
		self.bSuccessDeploy = False
		self.bContextReceived = False
		self.eventGo = threading.Event()
		self.eventCanSend = threading.Event()
		self.eventCanSend.set()

	#---------#
	# Running #
	#---------#

	def deploy(self):
		''' connect then try to receive instructions from client/server '''
		self.bSuccessDeploy *= self.connect_to_server()
		self.bSuccessDeploy = self.connect_to_client()
		self.threadServer.start()
		self.threadClient.start()
		
	def thread_client(self):
		while self.bRunClient:
			lstInstructions = self.recv_from_client()
			self.process_client_instructions(lstInstructions)

	def thread_server(self):
		while self.bRunServer:
			command = self.receive()
			self.process_server_data(command)

	#----------------------#
	# Initiate connections #
	#----------------------#

	def connect_to_server(self):
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.settimeout(self.timeout)
		except socket.error as msg:
			print(msg, "could not open socket.")
			self.socket = None
		try:
			self.socket.connect((self.tcpHost, self.tcpPort))
		except socket.error as msg:
			self.socket.close()
			print(msg, "could not open socket.")
			self.socket = None
		if self.socket is None:
			print("Cannot proceed without socket, exiting in 3s")
			time.sleep(3)
			return False
		else:
			print("Socket connected", self.receive())
			return True
		return True

	def connect_to_client(self):
		if self.connectionClient is not None:
			return True
		else:
			return False

	#---------------------#
	# Run and communicate #
	#---------------------#

	@wait_clear_set_event(self.eventCanSend)
	@timeoutErr
	def send_to_server(self,strData):
		self.socket.sendall(strData)
	
	@wait_clear_event(self.eventGo)
	def send_to_client(self, obj):
		''' sending information to the client '''
		self.connectionClient.send(obj)

	@timeoutErr
	def recv_from_server(self):
		while "\n" not in self.strBuffer:
			self.strBuffer += self.socket.recv(4096)
		idxReturn = self.strBuffer.find("\r\n")
		idxSpace = self.strBuffer.find(" ")
		command = ""
		if idxSpace != -1:
			if idxSpace < idxReturn:
				command =  self.strBuffer[:idxSpace]
				self.strBuffer = self.strBuffer[idxSpace+1:]
			else:
				command = self.strBuffer[:idxReturn] + "\r\n"
				self.strBuffer = self.strBuffer[idxReturn:].lstrip("\r\n")
		else:
			command = self.strBuffer[:idxReturn] + "\r\n"
			self.strBuffer = self.strBuffer[idxReturn:].lstrip("\r\n")
		return command, self.strBuffer

	def recv_from_client(self):
		lstInstructions = self.connectionClient.recv()
		return lstInstructions
