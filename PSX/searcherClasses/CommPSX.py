#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Socket client for PSX """

from SocketComm import SocketComm, timeoutErr
from global_param import *



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
		if command == READY:
			sys.stdout.write("\rProgress: 0%\r")
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
		elif command == DONE:
			self.send_to_server(RESULTS)
		elif command == RESULTS:
			print("Receiving results")
			strXmlEnd = "</table>\n"
			while strXmlEnd not in self.strBuffer:
				self.strBuffer += timeoutErr(self.socket.recv(4096))
			idxEnd = self.strBuffer.find(strXmlEnd) + len(strXmlEnd)
			xmlResults = xmlet.fromstring(self.strBuffer[:idxEnd])
			self.strBuffer = self.strBuffer[idxEnd:].lstrip("\r\n")
			print("Results received")
			self.results = xmlResults
			self.progressCount = 0
			self.eventGo.set()
		elif command == STATS:
			xmlStats = xmlet.fromstring(self.socket.recv(4096))
			print("Stats received")
			self.stats.append(xmlStats)
		elif command == SCENARIO:
			self.bReceived = True
			self.eventGo.set()
		elif command == MATRIX:
			self.bReceived = True
			self.eventGo.set()
		elif command == BYE:
			print("Connection closed by server")
		elif command == HELLO:
			print("Connection accepted by server")
		else:
			print("Unrecognized command")
	
	def process_client_instructions(self, tplInstructions):
		''' processing the instruction from the client '''
		command = lstInstructions[0]
		elif command == CONTEXT:
			self.send_context(tplInstructions[1])
			self.send_to_client(self.bReceived)
			self.bReceived = False
		elif command == PARAM:
			self.send_parameters(tplInstructions[1])
		elif command == MATRIX:
			self.send_to_server(lstInstructions[1])
			self.send_to_client(self.bReceived)
			self.bReceived = False
		elif command == RUN:
			# start run, wait for results and send them
			self.send_run_start()
			self.send_to_client(self.results)
		if command == STATUS:
			self.send_to_client(self.bSuccessDeploy)
		elif command == QUIT:
			self.send_quit()
		else:
			None

	#--------------#
	# Sending data #
	#--------------#

	@wait_clear_event(self.eventGo)
	def send_run_start(self):
		''' starting the run on the server '''
		self.send_to_server(RUN)
		self.eventGo.set()
		self.send_to_client(True)

	def send_context(self, strXmlContext):
		''' sending the xml context to the server '''
		self.send_to_server(SCENARIO)
		# send string size then string
		self.send_to_server("{}\r\n".format(len(strXmlContext)))
		self.send_to_server(strXmlContext + "\r\n")
	
	def send_parameters(self, strParam):
		''' sending the parameters of the run to the server '''
		self.send_to_server(DATA)
		self.maxProgress = float(len(xmlParam)-1)
		if "\r\n" not in strParam:
			strParam += "\r\n"
		self.send_to_server(strParam)

	def send_quit(self):
		''' sending termination signals '''
		self.send_to_server(QUIT)
		self.socket.close()
		self.bRunClient = False
		self.bRunServer = False