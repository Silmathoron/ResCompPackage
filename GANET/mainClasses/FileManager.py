#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" FileManager class for NetGen """

import numpy as np
from graph_tool.stats import remove_self_loops
import os, sys, gc

from PySide import QtCore
from PySide.QtGui import QFileDialog

from GraphClass import GraphClass
from InputConnect import InputConnect


class FileManager:
	def __init__(self,parent):
		self.parent = parent
		# create the required folders
		lstPaths = ["data","data/graphs","data/NeighbourList"]
		for path in lstPaths:
			try: 
				os.makedirs(path)
			except OSError:
				if not os.path.isdir(path):
					raise


	#--------#
	# Dialog #
	#--------#
	
	def dialogFileName(self,strAction):
		strFileName = QFileDialog.getOpenFileName(self.parent, self.parent.tr(strAction), QtCore.QDir.currentPath())[0]
		return strFileName


	#--------#
	# Saving #
	#--------#

	def setNeighbourListFile(self):
		fileName = self.dialogFileName("Save graph")
		self.parent.lineEditFileName.setText(fileName)

	def saveNeighbourList(self, graph=None):
		if graph == None:
			graph = self.parent.comboBoxSaveNetw.itemData(self.parent.comboBoxSaveNetw.currentIndex())
		nNodes = graph.getGraph().num_vertices()
		strList = ""
		dicProp = graph.getDicProp()
		for strName, value in dicProp.items():
			strList += "# {} {}\n".format(strName,value)
		for v1 in graph.getGraph().vertices():
			strList += "{}".format(graph.getGraph().vertex_index[v1])
			for e in v1.out_edges():
				rWeight = graph.getGraph().edge_properties["type"][e]
				if "weight" in graph.getGraph().edge_properties.keys():
					# on multiplie les poids du graphe pour avoir les arcs négatifs
					rWeight *= graph.getGraph().edge_properties["weight"][e]
				strList += " {};{}".format(graph.getGraph().vertex_index[e.target()],rWeight)
			strList += "\n"
		strName = ""
		if self.parent.lineEditFileName.isEnabled():
			strName = self.parent.lineEditFileName.text()
		if strName == "":
			strName = "data/NeighbourList/" + graph.getName()
		with open(strName,"w") as fileNeighbourList:
			fileNeighbourList.write(strList)

	#----------------#
	# Loading graphs #
	#----------------#

	''' NB: neighbour lists are suppose to be of the form:
	vert1 neighbour1_1;weight1_1 neighbour1_2;weight1_2 ... neighbour1_N;weight1_N
	vert2 neighbour2_1;weight2_1 ...'''
	def loadGraph(self):
		fileName = self.dialogFileName("Load graph")
		if fileName != "":
			graph = self.genGraphFromFile(fileName)
			self.parent.newGraphAdded([graph])

	def genGraphFromFile(self,fileName):
		lstFileStrings = [line.strip().rstrip(' ') for line in open(fileName)]
		# dic where will store the graph's properties
		lstStringProp = ["Name", "Distribution", "Type"]
		lstIntProp = ["Nodes", "Edges"]
		dicProp = {}
		graph = GraphClass()
		i = 0 # count lines before neighbour list
		# load graph properties
		while lstFileStrings[i][0] == "#":
			# end of the prop. name
			idxPropNameStart = 2 if lstFileStrings[i][1] == " " else 1
			nIdxEndPropName = lstFileStrings[i].find(" ",idxPropNameStart)
			strProp = lstFileStrings[i][idxPropNameStart:nIdxEndPropName]
			# prop. value
			strValue = lstFileStrings[i][nIdxEndPropName + 1:]
			if strProp == "Weighted":
				dicProp[strProp] = True if (strValue == "True") else False
			elif strProp == "Input":
				None
			elif not (strProp in lstStringProp):
				if strProp in lstIntProp:
					dicProp[strProp] = int(strValue)
				else:
					dicProp[strProp] = float(strValue)
			else:
				dicProp[strProp] = strValue
			i+=1
		# if there was no header, patch up:
		if i ==0:
			nNodes = len(lstFileStrings)
			dicProp["Nodes"] = nNodes
			dicProp["Edges"] = nNodes*(nNodes-1)
			dicProp["Density"] = (nNodes-1)/float(nNodes)
			dicProp["Name"] = "Graph_{}".format(len(self.parent.lstGraphs))
		graph.setDicProp(dicProp)
		graph.getGraph().add_vertex(dicProp["Nodes"])
		lstEdges = np.zeros((2,dicProp["Edges"]))
		lstWeights = np.zeros(dicProp["Edges"])
		# load graph
		idxEdge = 0
		for j in range(i,len(lstFileStrings)):
			strLine = lstFileStrings[j]
			idxNextSpace = strLine.find(" ",0)
			# get all neighbours and connections strength for current vertex i
			while idxNextSpace != -1:
				# put the vertices in the edges list
				lstEdges[0,idxEdge] = j-i
				idxEndVertNumber = strLine.find(";",idxNextSpace+1)
				lstEdges[1,idxEdge] = strLine[idxNextSpace+1:idxEndVertNumber]
				# get the connection's weight
				idxNextSpace = strLine.find(" ",idxEndVertNumber)
				if idxNextSpace == -1:
					lstWeights[idxEdge] = float(strLine[idxEndVertNumber+1:len(strLine)])
				else:
					lstWeights[idxEdge] = float(strLine[idxEndVertNumber+1:idxNextSpace])
				idxEdge += 1
		graph.getGraph().add_edge_list(np.transpose(lstEdges.astype(int)))
		# add the edges' properties
		lstTypes = np.sign(lstWeights)
		lstWeights = np.absolute(lstWeights)
		epropType = graph.getGraph().new_edge_property("int",lstTypes)
		graph.getGraph().edge_properties["type"] = epropType
		try:
			if dicProp["Weighted"]:
				epropWeights = graph.getGraph().new_edge_property("double",lstWeights)
				graph.getGraph().edge_properties["weight"] = epropWeights
		except:
			if np.ma.allequal(np.trunc(lstWeights), lstWeights):
				graph.setProp("Weighted",False)
			else:
				graph.setProp("Weighted",True)
				epropWeights = graph.getGraph().new_edge_property("double",lstWeights)
				graph.getGraph().edge_properties["weight"] = epropWeights
		# put the graph inside the list and update comboBox
		remove_self_loops(graph.getGraph())
		return graph

	#----------------------#
	# Connectivity loading #
	#----------------------#

	def loadConnect(self,strType):
		# get the file and put it into a list of strings
		fileName = self.dialogFileName("Load connectivity")
		if fileName != "":
			self.parent.lstConnect.append(self.genConnectFromFile(fileName,strType))
			self.parent.newConnectivityAdded()

	def genConnectFromFile(self,fileName,strType):
		lstFileStrings = [line.strip().rstrip(' ') for line in open(fileName)]
		idxConnectNameStart = max(fileName.rfind("/"),fileName.rfind("\\"))+1
		strConnectName = fileName[idxConnectNameStart:]
		# get the dimension of the input/output and of the reservoir: first line must be #(nIOSize,nReservoirSize)
		i = 0
		strLine = lstFileStrings[0]
		nReservoirDim, nIODim = 0,0
		while "#" in strLine:
			if "(" in strLine:
				idxIODimStart = strLine.find("(")+1
				idxIODimStop = max(strLine.find(";"),strLine.find(","))
				nIODim = int(strLine[idxIODimStart:idxIODimStop])
				idxReservoirDimStop = strLine.find(")")
				nReservoirDim = int(strLine[idxIODimStop+1:idxReservoirDimStop])
			i+=1
			strLine = lstFileStrings[i]
		# create the connectivity matrix
		matConnect = np.zeros((nIODim,nReservoirDim))
		for j in range(i,len(lstFileStrings)):
			strLine = lstFileStrings[j]
			idxNextSpace = strLine.find(" ",0)
			idxIO = int(strLine[0:idxNextSpace]) #if for some reason the IO neurons are not in the right order
			# get all neighbours and connections strength for current vertex idxIO
			while idxNextSpace != -1:
				# get reservoir node number
				idxEndVertNumber = strLine.find(";",idxNextSpace+1)
				nReservoirNode = int(strLine[idxNextSpace+1:idxEndVertNumber])
				# get the connection's weight
				idxNextSpace = strLine.find(" ",idxEndVertNumber)
				rWeight = 0
				if idxNextSpace == -1:
					rWeight = float(strLine[idxEndVertNumber+1:len(strLine)])
				else:
					rWeight = float(strLine[idxEndVertNumber+1:idxNextSpace])
				# write the weight at the right node number inside the matrix
				matConnect[idxIO,nReservoirNode] = rWeight
		# save the connectivity
		dicProp = {	"Name": strConnectName,
					"IODim": nIODim,
					"ReservoirDim": nReservoirDim,
					"Type": strType }
		connectivity = InputConnect(matConnect,dicProp)
		return connectivity

	def saveConnect(self,strCorrel="",connectivity=None):
		fileName = ""
		currentConnect = connectivity
		if currentConnect == None:
			idxCurrent = self.parent.comboBoxSelectConnect.currentIndex()
			currentConnect = self.parent.comboBoxSelectConnect.itemData(idxCurrent)
		if self.parent.checkBoxAutoNameConnect.isChecked():
			fileName = "data/NeighbourList/{}".format(currentConnect.getName(),self.parent.comboBoxConnectBaseReservoir.currentText())
		else:
			fileName = self.parent.fileManager.dialogFileName("Save connectivity")
		if fileName != "":
			#connectivity.savetxt(fileName)
			strHeader = "# InhibFrac {}\n".format(self.parent.dsbFracInhibConnect.value())
			strHeader += "# Density {}\n".format(self.parent.dsbConnectivityDensity.value())
			with open(fileName,"w") as fileConnect:
				fileConnect.write(strHeader)
				fileConnect.write(currentConnect.getListNeighbours())

	#---------------#
	# Batch loading #
	#---------------#

	def loadBatch(self):
		fileName = self.dialogFileName("Load batch")
		if fileName != "":
			lstFileStrings = [line.strip().rstrip(' ') for line in open(fileName)]
			idxDirEnd = max(fileName.rfind("/"), fileName.rfind("\\"))+1
			strDirectory = fileName[:idxDirEnd]
			self.parent.resComputer.setBatch(lstFileStrings,strDirectory)

	#----------#
	# Removing #
	#----------#

	def removeData(self):
		lstComboBoxesGraph = [self.parent.comboBoxSaveNetw,self.parent.comboBoxSelectGraph,self.parent.comboBoxReservoir,self.parent.comboBoxConnectBaseReservoir]
		for item in self.parent.listWGraphs.selectedItems():
			graph = item.data(1)
			self.parent.listWGraphs.takeItem(self.parent.listWGraphs.row(item))
			for comboBox in lstComboBoxesGraph:
				idxItem = comboBox.findText(graph.getName())
				comboBox.removeItem(idxItem)
			idxGraph = self.parent.lstGraphs.index(graph)
			del self.parent.lstGraphs[idxGraph]
		for item in self.parent.listWConnect.selectedItems():
			connectivity = item.data(1)
			self.parent.listWConnect.takeItem(self.parent.listWConnect.row(item))
			idxItem = self.parent.comboBoxSelectConnect.findText(connectivity.get_name())
			self.parent.comboBoxSelectConnect.removeItem(idxItem)
			idxConnect = self.parent.lstConnect.index(connectivity)
			del self.parent.lstConnect[idxConnect]
		
	def __del__(self):
		print("FileManager died")
