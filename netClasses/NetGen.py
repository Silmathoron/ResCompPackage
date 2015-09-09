#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Networks generator """


from GraphClass import GraphClass
from InputConnect import InputConnect

import xml.etree.ElementTree as xmlet
import numpy as np



#
#---
# Network generator
#------------------------

class NetGen:
	def __init__(self):
		# xml handler
		self.xmlHandler = XmlHandler()
		# parameters
		self.strPath = PATH_RES_CONNECT
		self.tplIgnore = ("Distribution", "Input")
		self.dicTypes = {	"Nodes": int, "Density": float,
							"Weighted": bool, "InhibFrac": float,
							"Distribution": str, "MeanExc": float,
							"MeanInhib": float, "VarExc": float,
							"VarInhib": float, "Type": str,
							"AntiCorr": boolFromString, "Edges": int,
							"Lambda": float, "Rho": int,
							"InDeg": float, "OutDeg": float,
							"Reciprocity": float,
							"Min": float,
							"Max": float
						}
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
	
	def fromInputFile(self, strInputFile):
		self.xmlHandler.processInputFile(strInputFile)
		self.numAvg = self.xmlHandler.nAvg
		# get info
		self.strGenerationType, self.nIODim, netInfo = self.xmlHandler.getNetData()
		if self.strGenerationType == "xml":
			# list of dicts
			self.lstGraphs = self.generateFromXml(netInfo)
		else:
			# list of filenames or xmlElt
			self.lstGraphs = netInfo

	#---------------------#
	# Networks generation #
	#---------------------#

	## generate networks dictionaries

	def generateFromXml(self, xmlRoot):
		# generate the grahs dictionaries
		for xmlElt in xmlRoot:
			dicGenerator = xmlToIterDict(xmlElt,self.dicTypes)
			dicGenerator["Type"] = xmlElt.tag,
			# test for weight distribution
			if "Weights" in dicGenerator.keys():
				dicGenerator.update(dicGenerator["Weights"][0])
				del dicGenerator["Weights"]
			# set input connectivity parameters
			dicGenerator["Input"][0]["ReservoirDim"] = self.numNodes(dicGenerator),
			dicGenerator["Input"][0]["IODim"] = self.nIODim,
			# generate list of individual graph dictionaries
			lstKeys = dicGenerator.keys()
			lstValues = dicGenerator.values()
			self.lstDicGraphs += dicTensorProduct(lstKeys, lstValues)
		self.numNet = len(self.lstDicGraphs)
	
	## generate and save networks
	
	def nextPair(self):
		idx = self.currentNetLine
		if self.strGenerationType == "xml":
			if idx < self.numNet: # why not just pop??
				# generate dictionaries
				dicCurrent = self.lstDicGraphs[idx]
				if not self.lstDicConnects:
					self.lstDicConnects = dicTensorProduct(dicCurrent["Input"].keys(), dicCurrent["Input"].values())
					self.numConnect = len(self.lstDicConnects)
				dicConnect = self.lstDicConnects.pop()
				# count the steps
				self.currentStep += 1
				self.currentNetLine += int(self.currentStep / (self.numAvg*self.numConnect))
				self.currentStep = self.currentStep % (self.numAvg*self.numConnect)
				# generate
				idxTot = idx + self.currentStep
				reservoir = GraphClass(idxTot, dicCurrent)
				connect = Connectivity(reservoir, dicConnect)
				strGraphFile = graphToString(reservoir, reservoir.getName())
				strConnectFile = matConnectToString(connect.getMatConnect(), connect.getName())
				return { "connectAsString":strConnectFile,"reservoirAsString":strGraphFile, "connect":connect, "reservoir":reservoir }
			else:
				return None
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
				strGraphFile = graphToString(reservoir, reservoir.getName())
				strConnectFile = matConnectToString(connect.getMatConnect(), connect.getName())
				return { "connectAsString":strConnectFile,"reservoirAsString":strGraphFile, "connect":connect, "reservoir":reservoir }
			else:
				return None
		else:
			if idx < self.numNet:
				self.currentNetLine += 1
				lstStr = self.lstGraphs[idx].split(" ")
			else:
				return None
	
	#-------#
	# Utils #
	#-------#
	
	def setPath(self, strPath):
		if strPath[-1] == "/":
			self.strPath = strPath
		else:
			self.strPath = strPath + "/"
	
	def numNodes(self, dico):
		try:
			return dico["Nodes"][0]
		except:
			return int(np.floor(np.sqrt(dico["Edges"]/dico["Density"])))
	
	def reset(self):
		self.currentNetLine = 0
		self.currentStep = 0
