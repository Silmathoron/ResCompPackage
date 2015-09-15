#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Phase-space explorer class """


import numpy as np
from itertools import product
from copy import deepcopy

from NetGen import NetGen
from XmlHandler import XmlHandler

from network_io import mat_to_string
from global_param import *



#
#---
# Explorer class
#-----------------------

class PhaseSpaceExplorer(object):
	
	#------#
	# Init #
	#------#

	def __init__(self, args, connection):
		self.connectionComm = connection
		# process input file
		self.args = args
		self.xmlHandler = XmlHandler()
		self.xmlHandler.process_input(args.input)
		self.numAvg = self.xmlHandler.get_header_item("averages")
		if self.args.path[-1] != "/": self.args.path += "/"
		# create children
		self.netGenerator = NetGen(args.path, self.xmlHandler)

	#------------------------#
	# sending/receiving data #
	#------------------------#

	def send_xml_context(self):
		''' send the xml context to the server '''
		bContinue = False
		strContext = self.xmlHandler.get_string_context()
		bContinue = False if strContext is None else True
		self.connectionComm.send([CONTEXT, strContext])
	
	def send_next_matrices(self):
		''' send the next pair of matrices to the server '''
		self.reservoir, self.connect = self.netGenerator.next_pair()
		if reservoir is not None:
			strReservoir = mat_to_string(self.reservoir.get_mat_adjacency(), self.reservoir.get_name())
			strConnect = mat_to_string(self.connect.as_csr(), self.connect.get_name())
			self.connectionComm.send([MATRIX,strReservoir])
			bPairReceived = self.connectionComm.recv()
			self.connectionComm.send([MATRIX,strConnect])
			bPairReceived *= self.connectionComm.recv()
			return bPairReceived
		else:
			return False

	def send_parameters(self):
		''' send the parameters to the server '''
		strNameReservoir, strNameConnect = self.current_names()
		xmlParamList = self.xmlHandler.gen_xml_param(strNameConnect,strNameReservoir,self.lstParameterSet)
		strParam = self.xmlHandler.to_string(xmlParamList)
		self.connectionComm.send([PARAM, strParam])
		
	def get_results(self):
		''' launch the run and wait for the results, then get the scores into an array of reals '''
		self.connectionComm.send(RUN,)
		xmlResults = self.connectionComm.recv()
		return xmlResults

	#----------------#
	# Tool functions #
	#----------------#

	def current_names(self):
		return self.reservoir.get_name(), self.connect.get_name()