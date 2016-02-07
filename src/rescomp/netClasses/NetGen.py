#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Networks generator """

from copy import deepcopy

import numpy as np

import nngt.generation as ng

from InputConnect import InputConnect
from rescomp.commonTools import mat_to_string
from rescomp.ioClasses import tensor_product



#
#---
# Network generator
#------------------------

class NetGen:

	__make_reservoir = {
		"distance_rule": ng.distance_rule,
		"erdos_renyi": ng.erdos_renyi,
		"fixed_degree": ng.fixed_degree,
		"newman_watts": ng.newman_watts,
		"random_scale_free": ng.random_scale_free }
	
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

	def generate_from_xml(self, xmlRoot):
		"""
		Funnction that generates a list of dicts containing all the properties 
		of the graphs that will be created.

		Parameters
		----------
		xmlRoot : :class:`xml.etree.ElementTree.Element`
			Xml element containing the graph properties (parsed from the .xml
			input)
		"""
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
	
	def next_pair(self):
		"""
		Function that returns the reservoir/input pairs one after the others.
		The first call generates the full list of the parameters necessary to
		generate all the graphs.
		Returns (None, None) once all pairs have been returned.
		"""
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
				gtype = dicCurrent["type"]
				reservoir = self.__make_reservoir[gtype](**dicCurrent)
				reservoir.set_types(-1,fraction=dicCurrent["ifrac"])
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
		''' generates missing entry between "nodes", "edges" and "density" '''
		lstMissingEntry = ["edges", "nodes", "density"]
		for tplKey in dicIter.keys():
			key = tplKey[0]
			if key in lstMissingEntry:
				idxKey = lstMissingEntry.index(key)
				del lstMissingEntry[idxKey]
		keyMissing = lstMissingEntry[0]
		if keyMissing == "edges":
			dicIter["edges"] = np.square(dicIter["nodes"][0]) * dicIter["density"][0],
		elif keyMissing == "nodes":
			dicIter["nodes"] = int(np.floor(dicIter["edges"][0] / dicIter["density"][0])),
		else:
			dicIter["density"] = dicIter["edges"][0] / np.square(float(dicIter["nodes"][0])),
	
	def setPath(self, strPath):
		if strPath[-1] == "/":
			self.strPath = strPath
		else:
			self.strPath = strPath + "/"
	
	def num_nodes(self, dico):
		try:
			return dico["nodes"][0]
		except:
			return int(np.floor(np.sqrt(dico["edges"]/dico["density"])))
	
	def reset(self):
		self.currentNetLine = 0
		self.currentStep = 0
