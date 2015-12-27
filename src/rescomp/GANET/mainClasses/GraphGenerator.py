#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Graph generator class for NetGen """

import numpy as np
import subprocess
import sys
import multiprocessing
import time

from ... import GraphClass



#
#---
# Graph generator class
#--------------------------

class GraphGenerator:
	def __init__(self, parent):
		self.parent = parent
		# la base (les attributs de l'instance)
		self.dicProperties = {}
		self.dicWProp = {}
	
	#######################
	# set functions
	
	def setDicPropGraph(self):
		self.reset_dic_properties()
		self.dicProperties["Type"] = self.parent.gui.cbNetType.currentText()
		self.dicProperties["InhibFrac"] = self.parent.gui.dsbInhibFrac.value()
		if self.parent.gui.wBoxWeights.isChecked():
			self.dicProperties["Weighted"] = True
			self.dicWProp = self.parent.weightsManager.generateWeightsDictionnary()
			self.dicProperties.update(self.dicWProp)
		else:
			self.dicProperties["Weighted"] = False
		if self.parent.gui.checkBoxNodes.isChecked():
			self.dicProperties["Nodes"] = self.parent.gui.sbNodes.value()
		if self.parent.gui.checkBoxEdges.isChecked():
			self.dicProperties["Edges"] = self.parent.gui.sbEdges.value()
		if self.parent.gui.checkBoxDensity.isChecked():
			self.dicProperties["Density"] = self.parent.gui.dsbDensity.value()
		if self.parent.gui.cbNetType.currentText() == "Free-scale":
			self.dicProperties["InDeg"] = self.parent.gui.dsbInDegExp.value()
			self.dicProperties["OutDeg"] = self.parent.gui.dsbOutDegExp.value()
			self.dicProperties["Reciprocity"] = self.parent.gui.dsbRecip.value()
		if self.parent.gui.cbNetType.currentText() == "EDR":
			self.dicProperties["Lambda"] = self.parent.gui.dsbLambda.value()
			self.dicProperties["Rho"] = self.parent.gui.sbNeuronDens.value()
		if self.parent.gui.gbGraphName.isChecked():
			self.dicProperties["Name"] = self.parent.gui.lineEditNameGraph.text()
		else:
			strName = self.dicProperties["Type"] + "_"
			for string in self.dicProperties.keys():
				if (string != "Type") and (string != "Weighted"):
					strName += string[0] + str(self.dicProperties[string])
			rWeights1 = 0.
			rWeights2 = 0.
			strWeights = ""
			if self.dicProperties["Weighted"]:
				strWeights = self.dicProperties["Distribution"]
				if strWeights == "Betweenness":
					rWeights1 = self.dicProperties["Min"]
					rWeights2 = self.dicProperties["Max"]
				elif strWeights == "Gaussian":
					rWeights1 = self.dicProperties["MeanExc"]
					rWeights2 = self.dicProperties["VarExc"]
				else:
					rWeights1 = self.dicProperties["LocationExc"]
					rWeights2 = self.dicProperties["ScaleExc"]
			strName += "_{}{}-{}".format(strWeights,rWeights1,rWeights2)
			self.dicProperties["Name"] = strName

	def set_property(self,strProp,valProp):
		self.dicProperties[strProp] = valProp
	
	#######################
	# Actions
		
	def generate_graph(self):
		dicVarQuantities = {}
		lstGraphShared = multiprocessing.Manager().list()
		self.parent.lstProcessesGraphGen.append([])
		# check how many clones should be generated
		nClones = 1
		if self.parent.gui.gbDuplicates.isChecked():
			nClones = self.parent.gui.sbDuplicates.value()
		if self.numVarQuantities() != 0:
			dicVarQuantities = self.getVarQuantities()
			for strVarQuantity,lstValues in dicVarQuantities.items():
				for val in lstValues:
					self.setDicPropGraph()
					for i in range(nClones):
						# set properties
						self.set_property(strVarQuantity,val)
						strName = self.dicProperties["Name"]
						strName += "_Var{}-{}".format(strVarQuantity[:4],val)
						self.set_property("Name",strName)
						# generate graph
						strProcName = "{}{}_{}".format(strVarQuantity,val,i)
						self.parent.lstProcessesGraphGen[-1].append(multiprocessing.Process(name=strProcName, target=self.make_graph, args=(lstGraphShared, self.dicProperties, strVarQuantity, val)))
						self.parent.lstProcessesGraphGen[-1][-1].start()
						if i+1 % 5 == 0:
							time.sleep(2) # to spare systems with not to much ram
		else:
			# on crée un dictionnaire contenant les propriétés du graphe
			self.setDicPropGraph()
			for i in range(nClones):
				strProcName = "proc_{}".format(i)
				self.parent.lstProcessesGraphGen[-1].append(multiprocessing.Process(name=strProcName, target=self.make_graph, args=(lstGraphShared, self.dicProperties)))
				self.parent.lstProcessesGraphGen[-1][-1].start()
				if i+1 % 5 == 0:
					time.sleep(2) # to spare systems with not to much ram
		# on reset les dictionnaires
		self.reset_dic_properties()
		# remove the processes from the list
		for proc in self.parent.lstProcessesGraphGen[-1]:
			proc.join()
		if self.parent.lstProcessesGraphGen and not self.parent.bProcKilled:
			self.parent.lstProcessesGraphGen.pop()
			if not self.parent.lstProcessesGraphGen:
				self.parent.gui.pbCancelGraphGen.setEnabled(False)
		else:
			self.parent.bProcKilled = False
		# update main interface
		self.parent.new_graph_added(lstGraphShared)

	def make_graph(self, lstGraphShared, strVarQuantity="", val=None):
		if strVarQuantity:
			lstGraphShared.append(GraphClass(self.dicProperties))
			if self.parent.gui.checkBoxSaveGenGraphs.isChecked(): # save if needed
				self.parent.fileManager.saveNeighbourList(lstGraphShared[-1])
		else:
			graph = GraphClass(self.dicProperties)
			lstGraphShared.append(graph) # on construit l'objet GraphClass
			if self.parent.gui.checkBoxSaveGenGraphs.isChecked(): # save if needed
				self.parent.fileManager.saveNeighbourList(lstGraphShared[-1])

	def reset_dic_properties(self):
		self.dicProperties = {}
	
	#######################
	# Utils
	
	def numVarQuantities(self):
		n = 0
		for child in self.parent.gui.gbGenSeries.children():
			if child != self.parent.gui.gbGenSeries.layout():
				if child.isChecked():
					n+=1
		return n
	
	def getVarQuantities(self):
		dicVaryingQuantities = {}
		for child in self.parent.gui.gbGenSeries.children():
			if child != self.parent.gui.gbGenSeries.layout():
				# on parcours toutes les groupBox des quantités pouvant varier
				if child.isChecked():
					strQuantity = child.title()
					rStart,rStop,rStep = 0,0,0
					for child in child.children():
						# on cherche les dsb et sb des Start, Stop, Step
						nLen = len(child.objectName())
						if "Start" in child.objectName():
							rStart = child.value()
						if "Stop" in child.objectName():
							rStop = child.value()
						if "Step" in child.objectName():
							rStep = child.value()
					dicVaryingQuantities[strQuantity] = np.arange(rStart,rStop,rStep)
		return dicVaryingQuantities

	def __del__(self):
		print("GraphGenerator died")
