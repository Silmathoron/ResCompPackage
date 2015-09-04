#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" GridSearcher class """

import sys

from NetGenerator import NetGen

sys.path.append("../ioClasses/")
from SocketComm import SocketComm
from XmlHandler import XmlHandler

sys.path.append("../commonTools")
from network_io import mat_to_string



#
#---
# GridSearcher
#-----------------------

class GridSearcher:
	
	#------#
	# Init #
	#------#

	def __init__(self, args):
		# process input file
		self.xmlHandler = XmlHandler(args.context)
		self.numAvg = xmlHandler.get_num_avg()
		# create children
		self.netGenerator = NetGen(args.destination, args.networks, self.xmlHandler)
		self.resultsAverager = Averager(args.destination, args.runtype, self.xmlHandler)
		self.comm = SocketComm(args.server.split(":"))

	#------------#
	# Processing #
	#------------#

	## setting context

	def xml_context(self):
		bContinue = self.comm.open_socket()
		strContext = self.xmlHandler.get_string_context()
		bContinue = False if strContext is None else True
		bContinue *= self.comm.send_context(strContext)
		return bContinue

	## generate and send next reservoir/connectivity pair
	
	def send_next(self):
		self.reservoir, self.connect = self.netGenerator.next_pair()
		if reservoir is not None:
			return self.send_matrices()
		else:
			return False

	## generate and send parameters

	def send_parameters(self):
		strNameReservoir, strNameConnect = self.current_names()
		xmlParamList = self.xmlHandler.genParamList(strNameConnect,strNameReservoir)
		self.comm.send_parameters(xmlParamList)

	#----------------#
	# Tool functions #
	#----------------#
	
	def send_matrices(self, reservoir, connect):
		strReservoir = mat_to_string(self.reservoir.get_mat_adjacency(), self.reservoir.get_name())
		strConnect = mat_to_string(self.connect.as_csr(), self.connect.get_name())
		bPairReceived = self.comm.sendData(strReservoir)
		bPairReceived *= self.comm.sendData(strConnect)
		return bPairReceived

	def current_names(self):
		return self.reservoir.get_name(), self.connect.get_name()
		
