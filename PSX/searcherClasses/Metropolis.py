#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Metropolis searcher class """


import numpy as np
from itertools import product
from copy import deepcopy

from NetGen import NetGen
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
		self.xmlHandler = XmlHandler()
		self.xmlHandler.process_input(args.input)
		self.numAvg = self.xmlHandler.get_header_item("averages")
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
	
	def send_next_matrices(self):
		self.reservoir, self.connect = self.netGenerator.next_pair()
		if reservoir is not None:
			return self.send_matrices()
		else:
			return False

	## generate parameters

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
		# generate dictionary describing these parameters
		self.dicVarParam = { self.lstParam[i]: {"start": dicParam[self.lstParam[i]]["start"],
												"step_size": dicParam[self.lstParam[i]]["step"],
												"num_steps": int(np.ceil(
													(dicParam[self.lstParam[i]]["stop"]-dicParam[self.lstParam[i]]["start"]) /
													float(dicParam[self.lstParam[i]]["step"]))-1)
												} for i in range(self.numVarParam) }
		# samples' number per variable for roughly 100 walkers (key = numVarParam; val = samples' number)
		dicSteps = { 1: [100], 2: [10, 10], 3: [4,5,5], 4: [3,3,3,4], 5: [3,3,3,2,2], 6: [2,2,2,2,2,3] }
		# generate the initial parameter grid
		lstLstParam = []
		lstSteps = dicSteps[self.numVarParam]
		for i in range(self.numVarParam):
			strParamName = self.lstParam[i]
			originalStepSize = self.dicVarParam[strParamName]["step_size"]
			newStepSize =  originalStepSize * self.dicVarParam[strParamName]["num_steps"] / float(lstSteps[i])
			lstSamples = []
			for j in range(lstSteps[i]):
				idxEquivalentStep = int(np.around(newStepSize*j/float(originalStepSize)))
				lstSamples.append(dicParam[self.lstParam[i]]["start"] + originalStepSize * idxEquivalentStep)
			lstLstParam.append(lstSamples)
		if len(dicParam) > self.numVarParam:
			for i in range(self.numVarParam,len(dicParam)-1):
				lstArrayParam.append(dicParam[self.lstParam[i]])
		return product(*lstLstParam)

	def next_parameter_set(self):
		numSets = len(self.lstParameterSet)
		self.lstParameterSet = []
		naParamToChange = np.random.randint(0,self.numVarParam,numSets)
		for idx,paramNumber in enumerate(naParamToChange):
			dicParam = self.dicVarParam[self.lstParam[paramNumber]]
			idxStep = np.random.randint(0,dicParam["num_steps"])
			self.lstParameterSet[idx][paramNumber] = dicParam["start"] + dicParam["step_size"] * idxStep

	## send and get results
	
	def send_parameters(self):
		strNameReservoir, strNameConnect = self.current_names()
		xmlParamList = self.xmlHandler.gen_xml_param(strNameConnect,strNameReservoir,self.lstParameterSet)
		self.comm.send_parameters(xmlParamList)
		
	def get_results(self):
		bRecv = True
		while bRecv:
			bRecv, strStep = self.comm.receive()
		return self.comm.results

	#-----#
	# Run #
	#-----#

	def run(self):
		''' TODO: insert the communication with Nico's server
			Take care of results saving '''
		bCrunchGraphs = True
		numRuns = 0
		while bCrunchGraphs:
			print("--- Run %d ---" % numRuns)
			bRecvd = self.send_next_matrices()
			if bRecvd:
				# calculate score for initial grid
				self.lstParameterSet = self.init_parameters()
				self.send_parameters()
				raScore = self.get_results()
				# proceed with Metropolis
				for i in range(500):
					# propose and evaluate new set of parameters
					lstOldParameters = deepcopy(self.lstParameterSet)
					self.next_parameter_set()
					self.send_parameters()
					raNewScore = self.get_results()
					# compare the scores and accept selected moves
					# update scores and variances
			else:
				bCrunchGraphs = False
			numRuns += 1
		print("Run finished")

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
