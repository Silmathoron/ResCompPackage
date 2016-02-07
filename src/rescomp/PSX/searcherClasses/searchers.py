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

	'''
	Abstract base class for phase space exploration.
	'''
	
	#------#
	# Init #
	#------#

	__metaclass__  = ABCMeta
	
	def __init__(self, args, connection, result_cols=[-1], weights=[1.]):
		'''
		Create an instance of :class:`~rescomp.PSX.PhaseSpaceExplorer`.

		Parameters
		----------
		args : container
			Arguments from a parser, which contain the exploration options as
			`args.input`, `args.path`...
		connection : :class:`multiprocessing.Pipe`
			Tunnel to interact with the :class:`~rescomp.PSX.CommPSX` object.
		result_cols : list of ints, optional (default: [-1])
			List of indices to the columns containing the results.
		weights : list of floats, optional (default: [1.])
			List of weights to compute the score as a weighted average of the
			results.
		'''
		self.connectionComm = connection
		# process input file
		self.args = args
		self.xmlHandler = XmlHandler()
		self.xmlHandler.process_input(INPUT, args.input)
		self.numAvg = self.xmlHandler.get_header_item("averages")
		self.args.path += "/" if self.args.path[-1] != "/" else ""
		# create children
		self.netGenerator = NetGen(args.path, self.xmlHandler)
		self.netGenerator.process_input_file(args.input)
		# set score computation
		self.result_cols = result_cols
		self.weights = weights
		if len(result_cols) == 1:
			def _score(result, cols, weights):
				return result[cols[0]]
			self.score = _score
		else:
			def _score(result, cols, weights):
				tmp = [ result[i] for i in cols ]
				return np.average(tmp, weights=weights)
			self.score = _score

	@abstractmethod
	def init_parameters(self):
		'''
		Initialize the parameters.
		.. note :
			This must be implemented in any subclass.
		'''
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
			strReservoir = mat_to_string(self.reservoir.adjacency_matrix(), self.reservoir.get_name())
			strConnect = mat_to_string(self.connect.as_csr(), self.connect.get_name())
			self.connectionComm.send((MATRIX,strReservoir))
			bPairReceived = self.connectionComm.recv()
			self.connectionComm.send((MATRIX,strConnect))
			bPairReceived *= self.connectionComm.recv()
			return bPairReceived
		else:
			return False

	@abstractmethod
	def send_parameters(self):
		'''
		Send the parameters.
		.. note :
			This must be implemented in any subclass.
		'''
		pass

	@abstractmethod
	def get_results(self, lstParam):
		pass

	#---------#
	# Running #
	#---------#

	@abstractmethod
	def run(self):
		'''
		Exploration algorithm.
		.. note :
			This must be implemented in any subclass as it is specific of each
			explorator.
		'''
		pass

	#----------------#
	# Tool functions #
	#----------------#

	def current_names(self):
		if None not in (self.reservoir, self.connect):
			return self.reservoir.get_name(), self.connect.get_name()
		else:
			return None, None

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

	def __init__(self, args, connection, **kwargs):
		super(GridSearcher, self).__init__(args, connection)
		self.diSaving = {}
		self.init_parameters()

	def get_results(self, lstParam):
		''' launch the run and wait for the results, then get the scores into an array of reals '''
		self.connectionComm.send((RUN,))
		strXmlResults = self.connectionComm.recv()
		results = self.xmlHandler.results_dic(strXmlResults, lstParam)
		return results

	def init_parameters(self):
		self.lstParameterSet = self.xmlHandler.gen_grid_search_param()

	def send_parameters(self):
		''' send the parameters to the server '''
		strNameReservoir, strNameConnect = self.current_names()
		xmlParamList = self.xmlHandler.gen_xml_param(strNameConnect,strNameReservoir,self.lstParameterSet)
		rMaxProgress = float(len(xmlParamList)-1)
		strParam = self.xmlHandler.to_string(xmlParamList)
		self.connectionComm.send((PARAM, strParam, rMaxProgress))
		bReceived = self.connectionComm.recv()

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
						self.diSaving[strResultName] = self.xmlHandler.save_results("{}.txt".format(strResultName), dicResults, path=self.args.path)
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

	def __init__(self, args, connection, **kwargs):
		super(Metropolis, self).__init__(args, connection)
		# temperature
		self.rTemperature = 0.02
		self.diSaving = {}
		self.diScores = {}
		self.diVisit = {}

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
		# update the order of the parameters for the XmlHandler
		self.xmlHandler.lstParamNames = deepcopy(self.lstParam)
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
		return [ tpl for tpl in tplTplparam ]

	#------------#
	# Processing #
	#------------#

	def next_parameter_set(self):
		''' generate the next set of parameters '''
		numSets = len(self.lstParameterSet)
		# randomly select a parameter and a stride in [-2, 2]
		arrParamToChange = np.random.randint(0,self.numVarParam,numSets)
		arrStepValue = (2*np.random.randint(0,2,numSets)-1)*np.random.randint(1,3,numSets)
		# apply
		for idx,paramNumber in enumerate(arrParamToChange):
			dicParam = self.dicVarParam[self.lstParam[paramNumber]]
			paramMaxValue = dicParam["start"] + dicParam["num_steps"] * dicParam["step_size"]
			lstParams = list(self.lstParameterSet[idx])
			# try the step
			step = dicParam["step_size"] * arrStepValue[idx]
			new = lstParams[paramNumber] + step
			# correct if out of grid, else accept
			if new <= dicParam["start"] or new >= paramMaxValue:
				lstParams[paramNumber] -= step
			else:
				lstParams[paramNumber] += step
			self.lstParameterSet[idx] = tuple(lstParams)

	def get_results(self, lstParam):
		''' launch the run and wait for the results, then get the scores into an array of reals '''
		self.connectionComm.send((RUN,))
		strXmlResults = self.connectionComm.recv()
		results = self.xmlHandler.results_dic(strXmlResults, lstParam, search='metropolis')
		return results

	def send_parameters(self):
		''' send the parameters to the server '''
		strNameReservoir, strNameConnect = self.current_names()
		xmlParamList = self.xmlHandler.gen_xml_param(strNameConnect, strNameReservoir, self.lstParameterSet)
		rMaxProgress = float(len(xmlParamList)-1)
		strParam = self.xmlHandler.to_string(xmlParamList)
		self.connectionComm.send((PARAM, strParam, rMaxProgress))
		bReceived = self.connectionComm.recv()

	def get_score(self, dicResults):
		''' return a numpy array of reals from the xml results '''
		del dicResults["results_names"]
		raScore = np.zeros(len(self.lstParameterSet))
		for i,params in enumerate(self.lstParameterSet):
			result = dicResults[params].pop()
			raScore[i] = self.score(result, self.result_cols, self.weights)
		return raScore

	def update_scores(self, array_score):
		for params,score in zip(self.lstParameterSet, array_score):
			if params in self.diScores:
				#~ print(np.sum(params), self.diScores[params], score)
				w = self.diVisit[params]
				self.diScores[params] = (self.diScores[params]*w + score)/(w+1)
				self.diVisit[params] += 1
			else:
				#~ print(np.sum(params))
				self.diScores[params] = score
				self.diVisit[params] = 1			

	#-----#
	# Run #
	#-----#

	def run(self):
		''' TODO: test the communication with comm process and Nico's server
			Take care of results saving '''
		bContinue = self.send_xml_context()
		import matplotlib.pyplot as plt
		if bContinue:
			print("run started")
			bCrunchGraphs = True
			numRuns = 0
			while bCrunchGraphs:
				print("--- Run %d ---" % numRuns)
				bRecvd = self.send_next_matrices()
				# save information
				strNameReservoir, strNameConnect = self.current_names()
				if bRecvd:
					# calculate score for initial grid
					self.lstParameterSet = self.init_parameters()
					#~ print(self.lstParameterSet.__class__)
					sys.stdout.write("\rSending...")
					sys.stdout.flush()
					self.send_parameters()
					sys.stdout.write("\rParameters sent\n")
					sys.stdout.flush()
					dicResults = self.get_results(self.lstParameterSet) # 12/27/15: the results are indeed the sumof the parameters
					self.diScores["results_names"] = dicResults["results_names"]
					raScore = self.get_score(dicResults)
					self.update_scores(raScore)
					# proceed with Metropolis
					for i in range(50):
						# propose and evaluate new set of parameters
						lstOldParameters = deepcopy(self.lstParameterSet)
						self.next_parameter_set()
						self.send_parameters()
						""" @todo: check code up to here """
						dicResults = self.get_results(self.lstParameterSet)
						raNewScore = self.get_score(dicResults)
						# compare the scores and accept selected moves
						raCompare = np.exp((raScore-raNewScore)/self.rTemperature)
						raRandom = np.random.uniform(0,1)
						baSmaller = raCompare<raRandom
						for j,paramSet in enumerate(lstOldParameters):
							if baSmaller[j]:
								self.lstParameterSet[j] = paramSet
							else:
								raScore[j] = raNewScore[j]
						# update scores and variances
						self.update_scores(raScore)
					plt.scatter([ np.sum(t) for t in self.diVisit.keys() ], [ v for v in self.diVisit.values() ])
					plt.show()
					# save
					strResultName = strNameConnect + "_" + strNameReservoir
					self.diSaving[strResultName] = self.xmlHandler.save_results("{}.txt".format(strResultName), self.diScores, self.diVisit, self.args.path)
				else:
					bCrunchGraphs = False
				numRuns += 1
			print("Run finished")
