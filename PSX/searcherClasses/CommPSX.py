#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Socket client for PSX """


import sys

from ...ioClasses import *
from ..global_param import *



#
#---
# Socket communicator
#------------------------

class CommPSX(SocketComm):

	def __init__(self,lstSrvHost,timeout):
		super(CommPSX, self).__init__(lstSrvHost,timeout)
		self.bReceived = False

	#--------------------#
	# Command processing #
	#--------------------#

	def process_server_data(self, command):
		''' processing the data received from the server '''
		bSetEventGo = True
		#~ print("server command", command)
		if command == READY:
			sys.stdout.write("\rProgress: 0%\r")
			self.bReceived = True
		elif command == PROG:
			idxEnd = self.strBuffer.find("\r\n")
			self.progressCount += int(self.strBuffer[:idxEnd])
			if self.maxProgress - self.progressCount < 0.1:
				sys.stdout.write("\rProgress: 100%\n")
				sys.stdout.flush()
			else:
				sys.stdout.write("\rProgress: {}%\r".format(int(100*self.progressCount/self.maxProgress)))
				sys.stdout.flush()
			self.strBuffer = self.strBuffer[idxEnd:].lstrip("\r\n")
			bSetEventGo = False
		elif command == DONE:
			self.send_to_server(RESULTS)
			bSetEventGo = False
		elif command == RESULTS:
			print("Receiving results")
			strXmlEnd = "</table>\r\n"
			while strXmlEnd not in self.strBuffer:
				self.strBuffer += self.socket.recv(4096)
			idxEnd = self.strBuffer.find(strXmlEnd) + len(strXmlEnd)
			strXmlResults = self.strBuffer[:idxEnd]
			self.strBuffer = self.strBuffer[idxEnd:].lstrip("\r\n")
			print("Results received")
			self.results = strXmlResults
			self.progressCount = 0
		elif command == STATS:
			xmlStats = xmlet.fromstring(self.socket.recv(4096))
			print("Stats received")
			self.stats.append(xmlStats)
		elif command == SCENARIO:
			self.bReceived = True
		elif command == MATRIX:
			self.bReceived = True
		elif command == BYE:
			print("Connection closed by server")
		elif command == HELLO:
			print("Connection accepted by server")
			bSetEventGo = False
		else:
			print("Unrecognized command")
		if bSetEventGo:
			self.eventGo.set()

	def process_client_instructions(self, tplInstructions):
		''' processing the instruction from the client '''
		command = tplInstructions[0]
		#~ print("client command", command)
		if command == CONTEXT:
			self.send_context(tplInstructions[1])
			self.eventGo.wait()
			self.send_to_client(self.bReceived)
		elif command == PARAM:
			self.send_parameters(tplInstructions[1:])
			self.eventGo.wait()
			self.send_to_client(self.bReceived)
		elif command == MATRIX:
			self.send_to_server(tplInstructions[1])
			print("matrix sent, waiting for eventGo")
			self.eventGo.wait()
			self.send_to_client(self.bReceived)
		elif command == RUN:
			# start run, wait for results and send them
			self.send_run_start()
		elif command == STATUS:
			self.send_to_client(self.bSuccessDeploy)
		elif command == QUIT:
			self.send_quit()
		self.eventGo.clear()
		self.bReceived = False


	#--------------#
	# Sending data #
	#--------------#

	def send_run_start(self):
		''' starting the run on the server '''
		self.send_to_server(RUN)
		self.eventGo.wait()
		self.send_to_client(self.results)

	def send_context(self, strXmlContext):
		''' sending the xml context to the server '''
		self.send_to_server(SCENARIO)
		# send string size then string
		self.eventCanSend.set()
		self.send_to_server("{}\r\n".format(len(strXmlContext)))
		self.eventCanSend.set()
		self.send_to_server(strXmlContext)

	def send_parameters(self, tplParam):
		''' sending the parameters of the run to the server '''
		self.send_to_server(DATA)
		self.maxProgress = tplParam[1]
		strParam = tplParam[0]
		if "\r\n" not in strParam:
			strParam += "\r\n"
		self.eventCanSend.set()
		self.send_to_server(strParam)

	def send_quit(self):
		''' sending termination signals '''
		self.send_to_server(QUIT)
		self.socket.close()
		self.bRunClient = False
		self.bRunServer = False
