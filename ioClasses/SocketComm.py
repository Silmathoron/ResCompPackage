#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Socket client """

import socket
import time
import sys
import xml.etree.ElementTree as xmlet
import threading

from globalParam import *



#
#---
# Tools
#------------------------

## wrapper
def timeoutErr(f):
	def wrapper(*args, **kw):
		try:
			return f(*args, **kw)
		except socket.timeout as msg:
			print("socket message: {}".format(msg))
	return wrapper

## Communication
DATA = "DATA\r\n"
QUIT = "QUIT\r\n"
SCENARIO = "SCENARIO\r\n"
READY = "READY\r\n"
RUN = "RUN\r\n"
DONE = "DONE\r\n"
RESULTS = "RESULTS\r\n"
MATRIX = "MATRIX\r\n"
STATS = "STATS\r\n"
BYE = "BYE\r\n"
HELLO = "HELLO\r\n"
PROGRESS = "PROGRESS\r\n"
	

#
#---
# Socket communicator
#------------------------

class SocketComm:
	def __init__(self, lstSrvHost, nTimeout):
		self.socket = None
		self.socketProgress = None
		self.strBuffer = ""
		self.results = None
		self.stats = []
		self.isValid = False
		self.strLatestResult = ""
		self.progressCount = 0
		self.maxProgress = 0
		self.timeout = nTimeout
		self.tcpHost, self.tcpPort = lstSrvHost[0], lstSrvHost[1]

	def open_socket(self):
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.settimeout(self.timeout)
			#~ self.socketProgress = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error as msg:
			print(msg, "could not open socket.")
			self.socket = None
		try:
			self.socket.connect((self.tcpHost, self.tcpPort))
			#~ self.socketProgress.bind(("", 42424))
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
	
	@timeoutErr
	def send_data(self,strData):
		self.socket.sendall(strData)
		return self.receive()[0]
	
	@timeoutErr
	def send_parameters(self, xmlParam):
		self.socket.send(DATA)
		self.maxProgress = float(len(xmlParam)-1)
		strParam = xmlet.tostring(xmlParam) + "\r\n"
		self.socket.sendall(strParam)

	@timeoutErr
	def send_quit(self):
		timeoutErr(self.socket.send(QUIT))
		self.socket.close()

	@timeoutErr
	def send_context(self, strXmlContext):
		self.socket.send(SCENARIO)
		# send string size
		self.socket.send("{}\r\n".format(len(strXmlContext)))
		self.socket.sendall(strXmlContext + "\r\n")

	@timeoutErr
	def send_run_start(self):
		self.socket.send(RUN)

	@timeoutErr
	def receive(self):
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
		if command != "PROGRESS":
			print(command.strip("\r\n"))
		if command == READY:
			#~ self.threadUDP = threading.Thread(target=self.recvProg, args=())
			#~ self.threadUDP.start()
			self.send_run_start()
			sys.stdout.write("\rProgress: 0%\r")
			return True, "Running"
		elif command == "PROGRESS":
			idxEnd = self.strBuffer.find("\r\n")
			self.progressCount += int(self.strBuffer[:idxEnd])
			if self.maxProgress - self.progressCount < 0.1:
				sys.stdout.write("\rProgress: 100%\n")
				sys.stdout.flush()
			else:
				sys.stdout.write("\rProgress: {}%\r".format(int(100*self.progressCount/self.maxProgress)))
				sys.stdout.flush()
			self.strBuffer = self.strBuffer[idxEnd:].lstrip("\r\n")
			return True, "Progressing"
		elif command == DONE:
			self.socket.send(RESULTS)
			return True, "Done"
		elif command == RESULTS:
			print("Receiving results")
			strXmlEnd = "</table>\n"
			while strXmlEnd not in self.strBuffer:
				self.strBuffer += self.socket.recv(4096)
			idxEnd = self.strBuffer.find(strXmlEnd) + len(strXmlEnd)
			xmlResults = xmlet.fromstring(self.strBuffer[:idxEnd])
			self.strBuffer = self.strBuffer[idxEnd:].lstrip("\r\n")
			print("Results received")
			self.results = xmlResults
			self.progressCount = 0
			return False, "Results"
		elif command == STATS:
			xmlStats = xmlet.fromstring(self.socket.recv(4096))
			print("Stats received")
			self.stats.append(xmlStats)
			return True, "Stats"
		elif command == SCENARIO:
			return True, "Scenario"
		elif command == MATRIX:
			return True, "Matrix"
		elif command == BYE:
			print("Connection closed by server")
			return False, "Bye"
		elif command == HELLO:
			print("Connection accepted by server")
			return True, "Hello"
		else:
			print("Unrecognized command")
			return True, "Error"
