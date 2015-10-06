#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Socket communicator """

import socket
import time
import threading
from abc import ABCMeta, abstractmethod

from socket_protocol import *



#
#---
# Socket communicator
#------------------------

class SocketComm(object):

	__metaclass__  = ABCMeta
	
	def __init__(self,lstSrvHost,timeout):
		''' init the required attributes '''
		# socket
		self.socket = None
		self.timeout = timeout
		self.tcpHost, self.tcpPort = lstSrvHost[0], int(lstSrvHost[1])
		# data
		self.strBuffer = ""
		self.results = None
		self.stats = []
		self.maxProgress = 0
		self.progressCount = 0
		self.bRunClient = True
		self.bRunServer = True
		self.lastCommand = HELLO
		# threads and processes communication
		self.connectionClient = None
		self.threadClient = threading.Thread(target=self.thread_client)
		self.threadServer = threading.Thread(target=self.thread_server)
		self.bSuccessDeploy = False
		self.bContextReceived = False
		self.eventGo = threading.Event()
		self.eventCanSend = threading.Event()
		self.eventCanSend.set()

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
			print("Socket connected", self.recv_from_server())
			return True
		return True

	def connect_to_client(self):
		if self.connectionClient is not None:
			return True
		else:
			return False

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
			tplInstructions = self.recv_from_client()
			self.process_client_instructions(tplInstructions)

	def thread_server(self):
		while self.bRunServer:
			command = self.recv_from_server()
			self.process_server_data(command)

	#---------#
	# Process #
	#---------#

	@abstractmethod
	def process_client_instructions(self, tplInstructions): pass

	@abstractmethod
	def process_server_data(self, command): pass
			
	#-------------#
	# Communicate #
	#-------------#

	#~ @sending_event
	@timeoutErr
	def send_to_server(self,strData):
		self.socket.sendall(strData)

	def send_to_client(self, obj):
		''' sending information to the client '''
		self.connectionClient.send(obj)

	@timeoutErr
	def recv_from_server(self):
		while "\r\n" not in self.strBuffer:
			self.strBuffer += self.socket.recv(4096)
		idxReturn = self.strBuffer.find("\r\n")
		idxSpace = self.strBuffer.find(" ")
		idxComma = self.strBuffer.find(",")
		command = ""
		if idxComma != -1:
			if idxComma < idxReturn:
				command =  self.strBuffer[:idxComma]
				self.strBuffer = self.strBuffer[idxComma+1:]
			else:
				command = self.strBuffer[:idxReturn] + "\r\n"
				self.strBuffer = self.strBuffer[idxReturn:].lstrip("\r\n")
		elif idxSpace != -1:
			if idxSpace < idxReturn:
				command =  self.strBuffer[:idxSpace]
				self.strBuffer = self.strBuffer[idxSpace+1:]
			else:
				command = self.strBuffer[:idxReturn] + "\r\n"
				self.strBuffer = self.strBuffer[idxReturn:].lstrip("\r\n")
		else:
			command = self.strBuffer[:idxReturn]
			if command != MATRIX:
				 command += "\r\n"
			self.strBuffer = self.strBuffer[idxReturn:].lstrip("\r\n")
		#~ print("command from server", command)
		return command

	def recv_from_client(self):
		tplInstructions = self.connectionClient.recv()
		return tplInstructions
