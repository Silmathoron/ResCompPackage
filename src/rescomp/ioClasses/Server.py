#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Server """

import socket, sys, time
from copy import deepcopy

from socket_protocol import *
import xml.etree.ElementTree as xmlet




#
#---
# Server
#-----------------

HOST, PORT = '127.0.0.1', 4243

class Server:
	
	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.strBuffer = ""
		self.data = ""
		# Bind socket to local host and port
		try:
			self.s.bind((HOST, PORT))
		except socket.error as msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()

	def run(self):
		self.s.listen(50)
		self.conn, addr = self.s.accept()
		self.conn.send(HELLO)
		print("accepted")
		while True:
			self.strBuffer += self.conn.recv(4096)
			bContinue = self.process()
			if not bContinue:
				print("stopping")
				break
		self.conn.close()

	def process(self):
		idxCommandEnd = self.strBuffer.find(",")
		if idxCommandEnd == -1:
			idxCommandEnd = self.strBuffer.find("\r\n")
		command = self.strBuffer[:idxCommandEnd]
		self.strBuffer = self.strBuffer[idxCommandEnd:].lstrip("\r\n")
		print(command)
		if command[:4] == "DATA":
			command = command[5:]
			idx_dt = command.find(" ")
			datatype = command[:idx_dt]
			print(datatype)
			if datatype == "SCENARIO":
				while command[0].isalpha():
					command = command[1:]
				nScenarioSize = int(command)
				while len(self.strBuffer) != nScenarioSize:
					self.strBuffer += self.conn.recv(nScenarioSize-len(self.strBuffer))
				scenario = self.strBuffer
				self.strBuffer = ""
				self.conn.send("SCENARIO\r\n")
				print("scenario sent back")
				return True
			elif datatype == "MATRIX":
				while "\r\n" not in self.strBuffer:
					self.strBuffer += self.conn.recv(4096)
				self.conn.send("MATRIX\r\n")
				print("matrix sent back")
				idxEnd = self.strBuffer.find("\r\n")
				self.strBuffer = self.strBuffer[idxEnd:].lstrip("\r\n")
				return True
		elif command == "RUN":
			time.sleep(0.5)
			self.conn.send("PROGRESS 50\r\n")
			time.sleep(0.5)
			self.conn.send(DONE)
			return True
		elif command == "RESULTS":
			nResults = 100
			self.conn.send(RESULTS)
			results = deepcopy(self.data)
			for old,child in zip(self.data[1:], results[1:]):
				res = 0.
				child.clear()
				item = child.makeelement("item", {"name": "res"})
				for subchild in old:
					try:
						res += float(subchild.text)
					except:
						pass
				item.text = str(res)
				child.append(item)
			self.conn.send(xmlet.tostring(results)+"\r\n")
			print("results sent")
			return True
		else:
			return False


#
#---
# Main
#-----------------

if __name__ == "__main__":
	server = Server()
	print("running")
	server.run()
