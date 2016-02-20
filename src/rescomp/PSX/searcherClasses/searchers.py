#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Phase-space explorer class """

import sys
from abc import ABCMeta, abstractmethod
from copy import deepcopy

from itertools import product
import numpy as np

from rescomp.netClasses import NetGen
from rescomp.ioClasses import XmlHandler
from rescomp.commonTools import mat_to_string, save_reservoir, save_connect
from rescomp.PSX.global_param import *




#-----------------------------------------------------------------------------#
# Explorer class
#-----------------------
#

class PhaseSpaceExplorer(object):

	__metaclass__  = ABCMeta

	di_instructions = { COMMAND: None, SIZE: None, DATA: None, ID: None }
	str_cid = "Context{}"
	str_pid = "ParamSet{}"
	
	#------#
	# Init #
	#------#
	
	def __init__(self, args, connection):
		self.connectionComm = connection
		# process input file
		self.args = args
		self.xmlHandler = XmlHandler()
		self.xmlHandler.process_input(INPUT, args.input)
		self.numAvg = self.xmlHandler.get_header_item("averages")
		self.args.path += "/" if self.args.path[-1] != "/" else ""
		# ids
		self.cid = 0 # number of contexts/scenarii sent
		self.pid = 0 # number of parameter sets sent
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
		# fill the dictionary
		di_context = self.di_instructions.copy()
		di_context[COMMAND] = C_S
		di_context[ID] = self.str_cid.format(self.cid)
		di_context[DATA] = self.xmlHandler.get_string_context()
		di_context[SIZE] = len(di_context[DATA])
		# check context/scenario, then send
		bContinue = False if di_context[DATA] is None else True
		self.connectionComm.send(di_context)
		bReceived = self.connectionComm.recv()
		self.cid += 1
		return bReceived*bContinue
	
	def send_next_matrices(self):
		''' send the next pair of matrices to the server '''
		self.reservoir, self.connect = self.netGenerator.next_pair()
		if self.reservoir is not None:
			# fill the dictionary for the reservoir
			di_reservoir = self.di_instructions.copy()
			di_reservoir[COMMAND] = C_M
			di_reservoir[ID] = self.reservoir.get_name()
			di_reservoir[DATA] = mat_to_string(
									self.reservoir.get_mat_adjacency(),
									self.reservoir.get_name() )
			di_reservoir[SIZE] = len(di_reservoir[DATA])
			# send reservoir
			self.connectionComm.send(di_reservoir)
			bPairReceived = self.connectionComm.recv()
			# fill the dictionary for the connectivity
			di_connect = self.di_instructions.copy()
			di_connect[COMMAND] = C_M
			di_connect[ID] = self.connect.get_name()
			di_connect[DATA] = mat_to_string( self.connect.as_csr(),
											  self.connect.get_name() )
			di_connect[SIZE] = len(di_connect[DATA])
			# send connectivity
			self.connectionComm.send(di_connect)
			bPairReceived *= self.connectionComm.recv()
			return bPairReceived
		else:
			return False

	def send_parameters(self):
		''' send the parameters to the server '''
		strNameReservoir, strNameConnect = self.current_names()
		# fill the dictionary
		di_param = self.di_instructions.copy()
		di_param[COMMAND] = C_P
		di_param[ID] = self.str_pid.format(self.pid)
		xmlParamList = self.xmlHandler.gen_xml_param( strNameConnect,
													  strNameReservoir,
													  self.lstParameterSet )
		di_param[DATA] = self.xmlHandler.to_string(xmlParamList)
		di_param[SIZE] = len(di_param[DATA])
		di_param[MAXPROG] = float(len(xmlParamList)-1)
		# send
		self.connectionComm.send(di_param)
		bReceived = self.connectionComm.recv()
		self.pid += 1
		return bReceived
		
	def get_results(self, lstParam):
		'''
		launch the run and wait for the results, then get the scores into an
		array of reals
		'''
		self.connectionComm.send({COMMAND: RUN})
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

	def make_dirs(self):
		pass

	def current_names(self):
		return self.reservoir.get_name(), self.connect.get_name()

	def save_networks(self, path):
		save_reservoir(self.reservoir, path)
		save_connect(self.connect, path, self.reservoir.get_name())


#-----------------------------------------------------------------------------#
# GridSearcher
#-----------------------
#

class GridSearcher(PhaseSpaceExplorer):

	'''
	Searcher class that performs a systematic exploration of phase space on a
	predefined grid.

	It uses a :class:`~rescomp.PSX.CommPSX` object to communicate with a server
	where the computations are performed.
	'''
	
	#------#
	# Init #
	#------#

	def __init__(self, args, connection):
		super(GridSearcher, self).__init__(args, connection)
		self.dicSaving = {}
		self.init_parameters()

	def init_parameters(self):
		self.lstParameterSet = self.xmlHandler.gen_grid_search_param()

	#-----#
	# Run #
	#-----#

	def run(self):
		'''
		Main function for :class:`rescomp.PSX.GridSearcher`.
		It sends networks associated to their parameter grid to the server,
		gets the results back and save both the networks and the results.
		'''
		bContinue = self.send_xml_context()
		if bContinue:
			print("run started")
			with open(self.args.path+"batch", "w") as fileBatchResult:
				bCrunchGraphs = True
				numRuns = 0
				while bCrunchGraphs:
					print("--- Run %d ---" % numRuns)
					bRecvd = self.send_next_matrices()
					if bRecvd:
						# save information
						strNameReservoir, strNameConnect = self.current_names()
						fileBatchResult.write("{}{}.txt\n".format(strNameConnect,strNameReservoir))
						fileBatchResult.flush()
						# process them
						sys.stdout.write("\rSending...")
						sys.stdout.flush()
						self.send_parameters()
						sys.stdout.write("\rParameters sent\n")
						sys.stdout.flush()
						# run and wait for results
						dicResults = self.get_results(self.lstParameterSet)
						# save results
						strResultName = strNameConnect + "_" + strNameReservoir
						self.dicSaving[strResultName] = self.xmlHandler.save_results("{}.txt".format(strResultName), dicResults, self.args.path)
						# save current reservoir and connectivity
						self.save_networks(self.args.path+MATRIX_SUBPATH)
					else:
						bCrunchGraphs = False
					numRuns += 1
				print("Run finished")


#-----------------------------------------------------------------------------#
# Metropolis
#-----------------------
#

class Metropolis(PhaseSpaceExplorer):
	
	#------#
	# Init #
	#------#

	def __init__(self, args, connection):
		super(Metropolis, self).__init__(args, connection)
		# temperature
		self.rTemperature = 1.0

	def init_parameters(self):
		''' generate the initial set of parameters:
		a grid that maps phase space uniformly '''
		# find number of varying parameters
		dicParam = self.xmlHandler.get_parameters()
		self.numVarParam = 0
		self.lstParam = []
		for key,val in dicParam.items():
			if val.__class__ == np.ndarray:
				self.lstParam.insert(0, key)
				self.numVarParam += 1
			else:
				self.lstParam.append(key)
		# generate dictionary describing these parameters
		self.dicVarParam = { self.lstParam[i]: {"start": dicParam[self.lstParam[i]][0],
												"step_size": dicParam[self.lstParam[i]][1]-dicParam[self.lstParam[i]][0],
												"num_steps": len(dicParam[self.lstParam[i]])-1
												} for i in range(self.numVarParam) }
		# samples' number per variable for roughly 100 walkers (key = numVarParam; val = samples' number)
		self.dicSteps = { 1: [100], 2: [10, 10], 3: [4,5,5], 4: [3,3,3,4], 5: [3,3,3,2,2], 6: [2,2,2,2,2,3] }
		# generate the initial parameter grid
		lstLstParam = []
		lstSteps = self.dicSteps[self.numVarParam]
		for i in range(self.numVarParam):
			strParamName = self.lstParam[i]
			originalStepSize = self.dicVarParam[strParamName]["step_size"]
			newStepSize =  originalStepSize * self.dicVarParam[strParamName]["num_steps"] / float(lstSteps[i])
			lstSamples = []
			for j in range(lstSteps[i]):
				idxEquivalentStep = int(np.around(newStepSize*j/float(originalStepSize)))
				lstSamples.append(self.dicVarParam[self.lstParam[i]]["start"] + originalStepSize * idxEquivalentStep)
			lstLstParam.append(lstSamples)
		if len(dicParam) > self.numVarParam:
			for i in range(self.numVarParam,len(dicParam)-1):
				lstLstParam.append((dicParam[self.lstParam[i]],))
		tplTplparam = tuple(product(*lstLstParam))
		return [ list(tpl) for tpl in tplTplparam ]

	#------------#
	# Processing #
	#------------#

	def next_parameter_set(self):
		''' generate the next set of parameters '''
		numSets = len(self.lstParameterSet)
		#~ self.lstParameterSet = []
		naParamToChange = np.random.randint(0,self.numVarParam,numSets)
		naStepValue = 2*np.random.randint(0,2,numSets)-1
		for idx,paramNumber in enumerate(naParamToChange):
			dicParam = self.dicVarParam[self.lstParam[paramNumber]]
			paramMaxValue = dicParam["start"] + dicParam["num_steps"] * dicParam["step_size"]
			if self.lstParameterSet[idx][paramNumber] == dicParam["start"]:
				self.lstParameterSet[idx][paramNumber] += dicParam["step_size"]
			elif self.lstParameterSet[idx][paramNumber] == paramMaxValue:
				self.lstParameterSet[idx][paramNumber] -= dicParam["step_size"]
			else:
				self.lstParameterSet[idx][paramNumber] += dicParam["step_size"] * naStepValue[idx]

	def get_score(self, xmlResults):
		''' return a numpy array of reals from the xml results '''
		#~ raScore = np.zeros(len(xmlResults))
		#~ for i,child in enumerate(xmlResults):
			#~ raScore[i] = float(child[-1].text)
		# tmp
		raScore = np.random.random(len(self.lstParameterSet))
		return raScore

	def update_scores(self):
		None

	#-----#
	# Run #
	#-----#

	def run(self):
		''' TODO: test the communication with comm process and Nico's server
			Take care of results saving '''
		bContinue = self.send_xml_context()
		if bContinue:
			print("run started")
			bCrunchGraphs = True
			numRuns = 0
			while bCrunchGraphs:
				print("--- Run %d ---" % numRuns)
				bRecvd = self.send_next_matrices()
				if bRecvd:
					# calculate score for initial grid
					self.lstParameterSet = self.init_parameters()
					#~ print(self.lstParameterSet.__class__)
					xmlParam = self.send_parameters()
					xmlResults = self.get_results(xmlParam)
					raScore = self.get_score(xmlResults)
					# proceed with Metropolis
					for i in range(500):
						# propose and evaluate new set of parameters
						lstOldParameters = deepcopy(self.lstParameterSet)
						self.next_parameter_set()
						xmlParam = self.send_parameters()
						xmlResults = self.get_results(xmlParam)
						raNewScore = self.get_score(xmlResults)
						# compare the scores and accept selected moves
						raCompare = np.exp((raScore-raNewScore)/self.rTemperature)
						raRandom = np.random.uniform(0,1)
						baSmaller = raCompare<raRandom
						for j,paramSet in enumerate(lstOldParameters):
							if baSmaller[j]:
								self.lstParameterSet[j] = paramSet
						# update scores and variances
						self.update_scores()
				else:
					bCrunchGraphs = False
				numRuns += 1
			print("Run finished")
