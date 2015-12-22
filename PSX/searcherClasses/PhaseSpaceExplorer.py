#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Phase-space explorer class """


import numpy as np
from itertools import product
from copy import deepcopy
from abc import ABCMeta, abstractmethod

from ...netClasses import NetGen
from ...ioClasses import XmlHandler

from ...commonTools import mat_to_string
from ..global_param import *



#
#---
# Explorer class
#-----------------------

class PhaseSpaceExplorer(object):
	
	#------#
	# Init #
	#------#

	__metaclass__  = ABCMeta
	
	def __init__(self, args, connection):
		self.connectionComm = connection
		# process input file
		self.args = args
		self.xmlHandler = XmlHandler()
		self.xmlHandler.process_input(args.input, args.path)
		self.numAvg = self.xmlHandler.get_header_item("averages")
		self.args.path += "/" if self.args.path[-1] != "/" else ""
		# create children
		self.netGenerator = NetGen(args.path, self.xmlHandler)
		self.netGenerator.process_input_file(args.input)

	@abstractmethod
	def init_parameters(self):
		''' initialize the parameters '''
		pass

	#------------------------#
	# sending/receiving data #
	#------------------------#

	def send_xml_context(self):
		''' send the xml context to the server '''
		bContinue = False
		strContext = self.xmlHandler.get_string_context()
		bContinue = False if strContext is None else True
		self.connectionComm.send((CONTEXT, strContext))
		bReceived = self.connectionComm.recv()
		return bReceived*bContinue
	
	def send_next_matrices(self):
		''' send the next pair of matrices to the server '''
		self.reservoir, self.connect = self.netGenerator.next_pair()
		if self.reservoir is not None:
			strReservoir = mat_to_string(self.reservoir.get_mat_adjacency(), self.reservoir.get_name())
			strConnect = mat_to_string(self.connect.as_csr(), self.connect.get_name())
			self.connectionComm.send((MATRIX,strReservoir))
			bPairReceived = self.connectionComm.recv()
			self.connectionComm.send((MATRIX,strConnect))
			bPairReceived *= self.connectionComm.recv()
			return bPairReceived
		else:
			return False

	@abstractmethod
	def send_parameters(self): pass
		
	def get_results(self, lstParam):
		''' launch the run and wait for the results, then get the scores into an array of reals '''
		self.connectionComm.send((RUN,))
		strXmlResults = self.connectionComm.recv()
		results = self.xmlHandler.results_dic(strXmlResults, lstParam)
		return results

	#---------#
	# Running #
	#---------#

	@abstractmethod
	def run(self): pass

	#----------------#
	# Tool functions #
	#----------------#

	def current_names(self):
		return self.reservoir.get_name(), self.connect.get_name()
