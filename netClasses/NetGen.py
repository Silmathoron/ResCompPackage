#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Networks generator """


from GraphClass import GraphClass
from InputConnect import InputConnect
from ..commonTools import mat_to_string
from ..ioClasses import tensor_product

import numpy as np
from copy import deepcopy



#
#---
# Network generator
#------------------------

class NetGen:
	
	def __init__(self, strPath, xmlHandler):
		# xml handler
		self.xmlHandler = deepcopy(xmlHandler)
		# parameters
		self.strPath = strPath
		# network-generation-related
		self.bGenNetworks = False
		self.lstGraphs = []
		self.lstDicGraphs = []
		self.numNet = 0
		self.nIODim = 0
		# iterating and averaging
		self.currentNetLine = 0
		self.lstDicConnects = []
		self.numConnect = 0
		self.numAvg = 0
		self.currentStep = 0
	
	#---------------#
	# Process imput #
	#---------------#
	
	def process_input_file(self, strInputFile):
		''' get the networks and relevant information from the input file '''
		self.xmlHandler.process_input(strInputFile)
		# get info
		self.numAvg = self.xmlHandler.get_header_item("averages")
		self.strGenerationType, netInfo = self.xmlHandler.get_networks()
		self.nIODim = self.xmlHandler.get_header_item("IODim")
		if self.strGenerationType == "xml":
			# list of dicts
			self.lstGraphs = self.generate_from_xml(netInfo)
		else:
			# list of filenames or xmlElt
			self.lstGraphs = netInfo

	#---------------------#
	# Networks generation #
	#---------------------#

	## generate networks dictionaries

	def generate_from_xml(self, xmlRoot):
		# generate the grahs dictionaries
		for xmlElt in xmlRoot:
			dicGenerator = self.xmlHandler.convert_xml_to_dict(xmlElt, True)
			# test for weight distribution
			if "weights" in dicGenerator.keys():
				dicGenerator.update(dicGenerator["weights"][0])
				del dicGenerator["weights"]
			#~ self.gen_ned(dicGenerator)
			# set input connectivity parameters
			dicGenerator["Input"][0]["ReservoirDim"] = self.num_nodes(dicGenerator),
			dicGenerator["Input"][0]["IODim"] = self.nIODim,
			# generate list of individual graph dictionaries
			lstKeys = dicGenerator.keys()
			lstValues = dicGenerator.values()
			self.lstDicGraphs += tensor_product(lstKeys, lstValues)
		self.numNet = len(self.lstDicGraphs)
	
	## generate and save networks
	
	def next_pair(self):
		idx = self.currentNetLine
		if self.strGenerationType == "xml":
			if idx < self.numNet: # why not just pop??
				# generate dictionaries
				dicCurrent = self.lstDicGraphs[idx]
				if not self.lstDicConnects:
					self.lstDicConnects = tensor_product(dicCurrent["Input"].keys(), dicCurrent["Input"].values())
					self.numConnect = len(self.lstDicConnects)
				dicConnect = self.lstDicConnects.pop()
				# count the steps
				self.currentStep += 1
				self.currentNetLine += int(self.currentStep / (self.numAvg*self.numConnect))
				self.currentStep = self.currentStep % (self.numAvg*self.numConnect)
				# generate
				idxTot = idx + self.currentStep
				reservoir = GraphClass(dicCurrent)
				connect = InputConnect(network=reservoir, dicProp=dicConnect)
				return reservoir, connect
			else:
				return None, None
		elif self.strGenerationType == "filesFromXml":
			# check whether we have generated all subgraphs for a given row
			if self.currentStep == self.numAvg-1:
				self.lstGraphs.pop()
			if self.lstGraphs:
				eltPair = self.lstGraphs[-1]
				eltGraphFileNames = eltPair.find('./string[@name="reservoirFiles"]')
				eltConnectFileNames = eltPair.find('./string[@name="connectFiles"]')
				eltParamFileNames = eltPair.find('./string[@name="paramFiles"]')
				# get file names
				strGraphFileName = eltGraphFileNames[self.currentStep]
				strConnectFileName = eltConnectFileNames[self.currentStep]
				strParamFileName = eltParamFileNames[self.currentStep]
				# tell the xmlHandler to get the next parameters
				self.xmlHandler.nextParam(strParamFileName) #""" todo: implement it on the xmlHandler """
				self.currentStep += 1
				# generate matrices
				reservoir = genGraphFromFile(strGraphFileName)
				connect = genConnectFromFile(strConnectFileName)
				return reservoir, connect
			else:
				return None,None
		else:
			if idx < self.numNet:
				self.currentNetLine += 1
				lstStr = self.lstGraphs[idx].split(" ")
			else:
				return None,None
	
	#-------#
	# Utils #
	#-------#

	def gen_ned(self, dicIter):
		''' generates missing entry between "Nodes", "Edges" and "Density" '''
		lstMissingEntry = ["Edges", "Nodes", "Density"]
		for tplKey in dicIter.keys():
			key = tplKey[0]
			if key in lstMissingEntry:
				idxKey = lstMissingEntry.index(key)
				del lstMissingEntry[idxKey]
		keyMissing = lstMissingEntry[0]
		if keyMissing == "Edges":
			dicIter["Edges"] = np.square(dicIter["Nodes"][0]) * dicIter["Density"][0],
		elif keyMissing == "Nodes":
			dicIter["Nodes"] = int(np.floor(dicIter["Edges"][0] / dicIter["Density"][0])),
		else:
			dicIter["Density"] = dicIter["Edges"][0] / np.square(float(dicIter["Nodes"][0])),
	
	def setPath(self, strPath):
		if strPath[-1] == "/":
			self.strPath = strPath
		else:
			self.strPath = strPath + "/"
	
	def num_nodes(self, dico):
		try:
			return dico["Nodes"][0]
		except:
			return int(np.floor(np.sqrt(dico["Edges"]/dico["Density"])))
	
	def reset(self):
		self.currentNetLine = 0
		self.currentStep = 0
