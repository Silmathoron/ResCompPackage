#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Socket client for PSX """


import sys

from rescomp.ioClasses import *
from rescomp.PSX.global_param import *



#
#---
# Socket communicator
#------------------------

class CommPSX(SocketComm):

	diConvert = {C_M: MATRIX, C_P: PARAMETERS, C_S: SCENARIO }

	def __init__(self,lstSrvHost,timeout):
		super(CommPSX, self).__init__(lstSrvHost,timeout)
		self.bReceived = False

	#--------------------#
	# Command processing #
	#--------------------#

	def process_server_data(self, command):
		''' processing the data received from the server '''
		bSetEventGo = True
		print("server command", command)
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
		elif command == "SCENARIO\r\n":
			self.bReceived = True
		elif command == "MATRIX\r\n":
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

	def process_client_instructions(self, diInstructions):
		''' processing the instruction from the client '''
		command = diInstructions[COMMAND]
		if command == RUN:
			self.send_run_start()
		elif command == STATUS:
			self.send_to_client(self.bSuccessDeploy)
		elif command == QUIT:
			self.send_quit()
		else:
			# get command informations
			server_command = self.diConvert[command]
			size = diInstructions[SIZE]
			id_command = diInstructions[ID]
			# send
			self.send_to_server(server_command.format(size, id_command))
			self.send_to_server(diInstructions[DATA])
			print("waiting for eventGo")
			self.eventGo.wait()
			self.send_to_client(self.bReceived)
		# set maxProgress
		if command == C_P:
			self.maxProgress = diInstructions[MAXPROG]
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
		strContext = SCENARIO.format(len(strXmlContext))
		self.send_to_server(strContext)
		print(strContext)
		self.send_to_server(strXmlContext)

	def send_parameters(self, tplParam):
		''' sending the parameters of the run to the server '''
		strParam = PARAMETERS.format(len(tplParam[0]), "P" + str(tplParam[1]))
		self.send_to_server(strParam)
		self.maxProgress = tplParam[1]
		strParam = tplParam[0]
		if "\r\n" not in strParam:
			strParam += "\r\n"
		self.send_to_server(strParam)

	def send_quit(self):
		''' sending termination signals '''
		self.send_to_server(QUIT)
		self.socket.close()
		self.bRunClient = False
		self.bRunServer = False
