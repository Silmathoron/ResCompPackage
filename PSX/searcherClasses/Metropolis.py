#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Metropolis searcher class """


import numpy as np
from itertools import product

from NetGenerator import NetGen
from XmlHandler import XmlHandler

from network_io import mat_to_string



#
#---
# Metropolis class
#-----------------------

class Metropolis:
	
	#------#
	# Init #
	#------#

	def __init__(self, args, comm):
		self.comm = comm
		# process input file
		self.args = args
		self.xmlHandler = XmlHandler(args.input)
		self.numAvg = xmlHandler.get_header_item("averages")
		if self.args.path[-1] != "/": self.args.path += "/"
		# create children
		self.netGenerator = NetGen(args.path, self.xmlHandler)

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

	#-----#
	# Run #
	#-----#

	def run(self):
		None

	def init_parameters(self):
		# find number of varying parameters
		dicParam = self.xmlHandler.get_parameters()
		self.numVarParam = 0
		self.lstParam = []
		for key,val in dicParam:
			if val.__class__ == np.ndarray:
				self.lstParam.insert(0, key)
				self.numVarParam += 1
			else:
				self.lstParam.append(key)
		# get the number of steps per variable for 100 walkers
		numSteps = int(np.floor(np.power(100,1/float(self.numVarParam))))
		numStepsLastVar = 100 - numSteps * (self.numVarParam - 1)
		# generate the initial parameter grid
		lstArrayParam = []
		for i in range(self.numVarParam-1):
			key = self.lstParam[i]
			lstArrayParam.append(np.linspace(dicParam[key]['start'],dicParam[key]['stop'],num=numSteps))
		strLastParam = self.lstParam[self.numVarParam-1]
		lstArrayParam.append(np.linspace(dicParam[strLastParam]['start'],dicParam[strLastParam]['stop'],num=numStepsLastVar))
		if len(dicParam) > self.numVarParam:
			for i in range(self.numVarParam,len(dicParam)-1):
				lstArrayParam.append(dicParam[self.lstParam[i]])
		return product(*lstArrayParam)

	#----------------#
	# Tool functions #
	#----------------#
	
	def send_matrices(self):
		strReservoir = mat_to_string(self.reservoir.get_mat_adjacency(), self.reservoir.get_name())
		strConnect = mat_to_string(self.connect.as_csr(), self.connect.get_name())
		bPairReceived = self.comm.send_data(strReservoir)
		bPairReceived *= self.comm.send_data(strConnect)
		return bPairReceived

	def current_names(self):
		return self.reservoir.get_name(), self.connect.get_name()
