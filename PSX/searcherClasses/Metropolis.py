#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Metropolis searcher class """


import numpy as np
from itertools import product
from copy import deepcopy

from PhaseSpaceExplorer import PhaseSpaceExplorer
from global_param import *



#
#---
# Metropolis class
#-----------------------

class Metropolis(PhaseSpaceExplorer):
	
	#------#
	# Init #
	#------#

	def __init__(self, args, connection):
		super(Metropolis, self).__init__(args, connection)
		# temperature
		self.rTemperature = 0

	#------------#
	# Processing #
	#------------#

	def init_parameters(self):
		''' generate the initial set of parameters:
		a grid that maps phase space uniformly '''
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
				lstSamples.append(dicParam[self.lstParam[i]]["start"] + originalStepSize * idxEquivalentStep)
			lstLstParam.append(lstSamples)
		if len(dicParam) > self.numVarParam:
			for i in range(self.numVarParam,len(dicParam)-1):
				lstArrayParam.append(dicParam[self.lstParam[i]])
		return product(*lstLstParam)

	def next_parameter_set(self):
		''' generate the next set of parameters '''
		numSets = len(self.lstParameterSet)
		self.lstParameterSet = []
		naParamToChange = np.random.randint(0,self.numVarParam,numSets)
		naStepValue = 2*np.random.randint(0,2)-1
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
		None

	def update_scores(self):
		None

	#-----#
	# Run #
	#-----#

	def run(self):
		''' TODO: test the communication with comm process and Nico's server
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
				xmlResults = self.get_results()
				raScore = self.get_score(xmlResults)
				# proceed with Metropolis
				for i in range(500):
					# propose and evaluate new set of parameters
					lstOldParameters = deepcopy(self.lstParameterSet)
					self.next_parameter_set()
					self.send_parameters()
					xmlResults = self.get_results()
					raNewScore = self.get_score(xmlResults)
					# compare the scores and accept selected moves
					raCompare = np.exp((raScore-raNewScore)/self.rTemperature)
					raRandom = np.random.uniform(0,1)
					baSmaller = raCompare<raRandom
					for j,paramSet in enumerate(lstOldParameters):
						if baSmaller[i]:
							self.lstParameterSet[j] = paramSet
					# update scores and variances
					self.update_scores()
			else:
				bCrunchGraphs = False
			numRuns += 1
		print("Run finished")
