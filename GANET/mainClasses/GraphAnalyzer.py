#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Graph analysis class for NetGen """

import numpy as np
import subprocess
from copy import deepcopy
import multiprocessing

from PySide import QtGui

from GraphClass import GraphClass
from graph_measure import *
from plotWidget import PlotWidget


#
#---
# GraphAnalysis class
#-----------------------

class GraphAnalyzer:
	def __init__(self, parent):
		self.parent = parent
		# dictionnary linking checkBox to measuring function
		self.dicNetAnalysis = { self.parent.gui.gbAssort.title(): get_assortativity,
								self.parent.gui.gbClustering.title(): get_clustering,
								self.parent.gui.gbReciprocity.title(): get_reciprocity,
								self.parent.gui.gbConnectComp.title(): get_num_scc,
								"Weak CC": get_num_wcc,
								self.parent.gui.gbDiameter.title(): get_diameter,
								self.parent.gui.gbSpectrum.title(): get_spectral_radius}
		'''# dic linking the weight generator
		self.dicWeightsType = {	"Gaussian": self.setGaussWeights,
								"Lognormal": self.setLogNormWeights}'''
		# la base (les attributs de l'instance)
		self.dicProperties = {}
		self.dicWProp = {}
		self.plottingWidget = PlotWidget()
		#~ self.updateProgress = QtCore.Signal(int)

	#---------------#
	# set functions #
	#---------------#

	def setDicPropGraphEvol(self,strEvolProp,currentValProp):
		self.resetDictionaries()
		self.dicProperties["Type"] = self.parent.gui.cbNetTypeEvol.currentText()
		self.dicProperties["FracInhib"] = self.parent.gui.dsbFracInhibEvol.value()
		if self.parent.gui.checkBoxNodesEvol.isChecked():
			self.dicProperties["Nodes"] = self.parent.gui.sbNodesEvol.value()
		if self.parent.gui.checkBoxEdgesEvol.isChecked():
			self.dicProperties["Edges"] = self.parent.gui.sbEdgesEvol.value()
		if self.parent.gui.checkBoxDensityEvol.isChecked():
			self.dicProperties["Density"] = self.parent.gui.dsbDensityEvol.value()
		if self.parent.gui.cbNetTypeEvol.currentText() == "Free-scale":
			self.dicProperties["InDeg"] = self.parent.gui.dsbInDegExpEvol.value()
			self.dicProperties["OutDeg"] = self.parent.gui.dsbOutDegExpEvol.value()
			self.dicProperties["Reciprocity"] = self.parent.gui.dsbRecipEvol.value()
		if self.parent.gui.cbNetTypeEvol.currentText() == "EDR":
			self.dicProperties["Lambda"] = self.parent.gui.dsbLambdaEvol.value()
			self.dicProperties["Rho"] = self.parent.gui.sbNeuronDensEvol.value()
		strName = ""
		# pour le moment on s'occupe pas des poids
		self.dicProperties["Weighted"] = False
		if self.parent.gui.gbGraphName.isChecked():
			strName = self.dicProperties["Type"] + "_"
		for string in self.dicProperties.keys():
			if string != "Type":
				strName += string[0] + str(self.dicProperties[string])
		self.dicProperties["Name"] = strName
		self.dicProperties[strEvolProp] = currentValProp

	def resetDictionaries(self):
		self.dicProperties = {}
		self.dicWProp = {}

	'''def setGaussWeights(self):
		self.dicWProp["MeanExc"] = self.parent.gui.dsbMeanExcWeights.value()
		self.dicWProp["VarExc"] = self.parent.gui.dsbVarExcWeights.value()
		self.dicWProp["MeanInhib"] = self.parent.gui.dsbMeanInhibWeights.value()
		self.dicWProp["VarInhib"] = self.parent.gui.dsbVarInhibWeights.value()

	def setLogNormWeights(self):
		self.dicWProp["ScaleExc"] = self.dsbScaleExcWeights.value()
		self.dicWProp["LocationExc"] = self.dsbLocationExcWeights.value()
		self.dicWProp["ScaleInhib"] = self.dsbScaleInhibWeights.value()
		self.dicWProp["LocationInhib"] = self.dsbLocationInhibWeights.value()'''

	##################
	# get functions

	def getMeasurements(self):
		lstMeas = []
		if self.parent.gui.gbAssort.isEnabled():
			lstMeas.append(self.parent.gui.gbAssort.title())
		if self.parent.gui.gbClustering.isEnabled():
			lstMeas.append(self.parent.gui.gbClustering.title())
		if self.parent.gui.gbReciprocity.isEnabled():
			lstMeas.append(self.parent.gui.gbReciprocity.title())
		if self.parent.gui.gbConnectComp.isEnabled():
			lstMeas.append(self.parent.gui.gbConnectComp.title())
			if self.parent.gui.tabWAnalysis.currentIndex() == 0:
				lstMeas.append("Weak CC")
		if self.parent.gui.gbDiameter.isEnabled():
			lstMeas.append(self.parent.gui.gbDiameter.title())
		if self.parent.gui.gbSpectrum.isEnabled():
			lstMeas.append(self.parent.gui.gbSpectrum.title())
		return lstMeas


	##################
	# Graph analysis

	def plotDistrib(self):
		# get selected graph
		idxCurrent = self.parent.gui.comboBoxSelectGraph.currentIndex()
		graph = self.parent.gui.comboBoxSelectGraph.itemData(idxCurrent)
		strGraphName = graph.getName().replace(".","p")
		# do we care about weights?
		bWeights = False
		if self.parent.gui.checkBoxConsiderWeights.isChecked():
			bWeights = True
		# look at which subgraph(s) we want to study
		dicGraphType = {}
		dicGraphStorage = {}
		if self.parent.gui.checkBoxAnalyzeExc.isChecked():
			dicGraphType["Exc"] = graph.genExcSubgraph
		if self.parent.gui.checkBoxAnalyzeInhib.isChecked():
			dicGraphType["Inhib"] = graph.genInhibSubgraph
		if self.parent.gui.checkBoxAnalyzeAll.isChecked():
			dicGraphType["Total"] = graph.copy
		dicBetwNodes = {}
		dicBetwEdges = {}
		# plot properties
		if self.parent.gui.gbBetweenness.isChecked():
			lstArgsBetw = []
			if self.parent.gui.checkBoxBetwEdges.isChecked():
				lstArgsBetw.append("Edges")
			if self.parent.gui.checkBoxBetwNodes.isChecked():
				lstArgsBetw.append("Nodes")
			for strType in dicGraphType.keys():
				dicGraphStorage[strType] = dicGraphType[strType]()
				strFileName = "betw_{}_{}".format(strGraphName,strType)
				strGP = self.parent.gnuPlotter.genGpStrBetw(strFileName,lstArgsBetw)
				strGPTMP,dicBetwNodes[strType],dicBetwEdges[strType] = plotBetwDistrib(self.parent, dicGraphStorage[strType],lstArgsBetw,False,bWeights)
				strGP += strGPTMP
				strSubprocess = "data/histoBetweenness.gp"
				with open(strSubprocess,"w") as fileGP:
					fileGP.write(strGP)
				subprocess.call(["gnuplot", strSubprocess])
		if self.parent.gui.gbDegDistrib.isChecked():
			lstArgsDeg = []
			if self.parent.gui.checkBoxDegIn.isChecked():
				lstArgsDeg.append("in")
			if self.parent.gui.checkBoxDegOut.isChecked():
				lstArgsDeg.append("out")
			if self.parent.gui.checkBoxDegTot.isChecked():
				lstArgsDeg.append("total")
			for strType in dicGraphType.keys():
				if strType not in dicGraphStorage.keys():
					dicGraphStorage[strType] = dicGraphType[strType]()
				strFileName = "deg_{}_{}".format(strGraphName,strType)
				strGP,bLogDeg = self.parent.gnuPlotter.genGpStrDeg(strFileName,lstArgsDeg)
				strGP += plotDegDistrib(self.parent, dicGraphStorage[strType],lstArgsDeg,bLogDeg,bWeights)
				strSubprocess = "data/histoDegree.gp"
				with open(strSubprocess,"w") as fileGP:
					fileGP.write(strGP)
				subprocess.call(["gnuplot", strSubprocess])
		if bWeights:
			dicPlots = {}
			for strType in dicGraphType.keys():
				if strType not in dicGraphStorage.keys():
					dicGraphStorage[strType] = dicGraphType[strType]()
				arrWeightCount, arrWeight = weightDistribution(dicGraphStorage[strType],False)
				dicPlots["Weight distrib. ({})".format(strType)] = [np.array([arrWeight,arrWeightCount]), "Count", "Weight"]
			plotView = self.plottingWidget.createPlotView(dicPlots)
			self.plottingWidget.addPlotView(graph.getName(),plotView)
			self.plottingWidget.show()
		# nodes' properties
		bNodeProp = False
		strHeader = "Node"
		lstStrVal = np.arange(graph.getNodes()).astype(str)
		lstTab = np.repeat("\t",graph.getNodes())
		if self.parent.gui.checkBoxBetwVal.isChecked():
			bNodeProp = True
			for strType in dicGraphType.keys():
				if strType not in dicGraphStorage.keys():
					dicGraphStorage[strType] = dicGraphType[strType]()
					dicBetwNodes[strType] = betwCentrality(dicGraphStorage[strType],bWeights)[0]
				elif strType not in dicBetwNodes.keys():
					dicBetwNodes[strType] = betwCentrality(dicGraphStorage[strType],bWeights)[0]
				strHeader += "\tBetw.-" + strType
				lstStrVal = np.core.defchararray.add(lstStrVal,lstTab)
				lstStrVal = np.core.defchararray.add(lstStrVal,dicBetwNodes[strType].a.astype(str))
		if self.parent.gui.gbDegreeVal.isChecked():
			bNodeProp = True
			for strType in dicGraphType.keys():
				if strType not in dicGraphStorage.keys():
					dicGraphStorage[strType] = dicGraphType[strType]()
				if self.parent.gui.checkBoxInDegVal.isChecked():
					strHeader += "\tIn-deg.-" + strType
					lstStrVal = np.core.defchararray.add(lstStrVal,lstTab)
					lstDeg = dicGraphStorage[strType].getGraph().degree_property_map("in").a
					lstStrVal = np.core.defchararray.add(lstStrVal,lstDeg.astype(str))
				if self.parent.gui.checkBoxOutDegVal.isChecked():
					strHeader += "\tOut-deg.-" + strType
					lstStrVal = np.core.defchararray.add(lstStrVal,lstTab)
					lstDeg = dicGraphStorage[strType].getGraph().degree_property_map("out").a
					lstStrVal = np.core.defchararray.add(lstStrVal,lstDeg.astype(str))
				if self.parent.gui.checkBoxTotDegVal.isChecked():
					strHeader += "\tTot.-deg.-" + strType
					lstStrVal = np.core.defchararray.add(lstStrVal,lstTab)
					lstDeg = dicGraphStorage[strType].getGraph().degree_property_map("total").a
					lstStrVal = np.core.defchararray.add(lstStrVal,lstDeg.astype(str))
		strHeader+="\n"
		if bNodeProp:
			with open("data/nodeVal" + strGraphName,"w") as fileNodeVal:
				fileNodeVal.write(strHeader)
				idxLast = len(lstStrVal)-1
				for i in range(idxLast+1):
					fileNodeVal.write(lstStrVal[i])
					if i != idxLast:
						fileNodeVal.write("\n")
		# nodes' sorting
		bNodeSort = False
		nNodesToKeep = self.parent.gui.sbNodesToKeep.value()
		strSort = ""
		if self.parent.gui.checkBoxBetwSort.isChecked():
			bNodeSort = True
			for strType in dicGraphType.keys():
				if strType not in dicGraphStorage.keys():
					dicGraphStorage[strType] = dicGraphType[strType]()
					dicBetwNodes[strType] = betwCentrality(dicGraphStorage[strType],bWeights)[0]
				elif strType not in dicBetwNodes.keys():
					dicBetwNodes[strType] = betwCentrality(dicGraphStorage[strType],bWeights)[0]
				strSort += "Node betweenness sorting - " + strType + "\n"
				lstBetwSort = np.argsort(dicBetwNodes[strType].a)
				for i in range(nNodesToKeep):
					strSort += " {}".format(lstBetwSort[i])
				strSort += "\n"
		if self.parent.gui.gbDegSort.isChecked():
			bNodeSort = True
			for strType in dicGraphType.keys():
				if strType not in dicGraphStorage.keys():
					dicGraphStorage[strType] = dicGraphType[strType]()
				if self.parent.gui.checkBoxInDegSort.isChecked():
					lstDeg = dicGraphStorage[strType].getGraph().degree_property_map("in").a
					strSort += "Node in-degree sorting - " + strType + "\n"
					for i in range(nNodesToKeep):
						strSort += " {}".format(lstDeg[i])
					strSort += "\n"
				if self.parent.gui.checkBoxOutDegSort.isChecked():
					lstDeg = dicGraphStorage[strType].getGraph().degree_property_map("out").a
					strSort += "Node out-degree sorting - " + strType + "\n"
					for i in range(nNodesToKeep):
						strSort += " {}".format(lstDeg[i])
					strSort += "\n"
				if self.parent.gui.checkBoxTotDegSort.isChecked():
					lstDeg = dicGraphStorage[strType].getGraph().degree_property_map("total").a
					strSort += "Node total-degree sorting - " + strType + "\n"
					for i in range(nNodesToKeep):
						strSort += " {}".format(lstDeg[i])
					strSort += "\n"
		if bNodeSort:
			with open("data/sort_" + strGraphName,"w") as fileSort:
				fileSort.write(strSort)
		# betweenness Vs weight
		if self.parent.gui.checkBoxBetwVsWeight.isChecked():
			for strType in dicGraphType.keys():
				if strType not in dicGraphStorage.keys():
					dicGraphStorage[strType] = dicGraphType[strType]()
					dicBetwEdges[strType] = betwCentrality(dicGraphStorage[strType])[1]
				elif strType not in dicBetwEdges.keys():
					dicBetwEdges[strType] = betwCentrality(dicGraphStorage[strType])[1]
				plotBetwVsWeight(self.parent,dicGraphStorage[strType],dicBetwEdges[strType])

	def plotEvolProp(self):
		# get requested averaging number
		numAvg = 1
		if self.parent.gui.sbAverage.isEnabled():
			numAvg = self.parent.gui.sbAverage.value()
		print("--- Averaging over {} samples ---".format(numAvg))
		dicVaryingQuantities = {}
		lstStrMeasurements = self.getMeasurements()
		dicVaryingQuantities = self.getVaryingQuantities()
		# check log and weights
		bWeights = False
		dicLog = {	"Degree": False,
					"Betweenness": False }
		if self.parent.gui.checkBoxConsiderWeights.isChecked():
			bWeights = True
		if self.parent.gui.checkBoxLogDegX.isChecked():
			dicLog["Degree"] = True
		if self.parent.gui.checkBoxLogBetwX.isChecked():
			dicLog["Betweenness"] = True
		# check subgraph types to be studied:
		lstSubgraphTypes = []
		if self.parent.gui.checkBoxAnalyzeExc.isChecked():
			lstSubgraphTypes.append("Exc")
		if self.parent.gui.checkBoxAnalyzeInhib.isChecked():
			lstSubgraphTypes.append("Inhib")
		if self.parent.gui.checkBoxAnalyzeAll.isChecked():
			lstSubgraphTypes.append("All")
		# for each varying quantity
		for strVarQuantity,lstVarValues in dicVaryingQuantities.items():
			# initialize progressbar and plots informations
			self.parent.gui.initProgressBar()
			dicPlotFunc, dicArgs, dicStrGp = checkPlots(self.parent,lstSubgraphTypes, strVarQuantity)
			nNecessarySteps = len(lstVarValues)
			# file names
			strFile = "evol_{}_var{}_".format(self.parent.gui.cbNetTypeEvol.currentText(),strVarQuantity)
			for strMeas in lstStrMeasurements:
				strFile += strMeas[:1]
			dicFileNames = { subgraphType: strFile + "_{}".format(subgraphType) for subgraphType in lstSubgraphTypes }
			# initialize files
			initFiles(self.parent, lstSubgraphTypes, dicFileNames, strVarQuantity, lstStrMeasurements)
			# iterations and averaging
			rStepToPercent = 100./(nNecessarySteps*numAvg)
			for i in range(nNecessarySteps):
				self.setDicPropGraphEvol(strVarQuantity,lstVarValues[i])
				# dictionnary containing the average values for each graph subtypes
				dicAvgValues, dicAvgDistrib = initDicAvg(dicPlotFunc, dicArgs, lstStrMeasurements)
				dicGraphAvgValues = { subgraphType: deepcopy(dicAvgValues) for subgraphType in lstSubgraphTypes }
				dicGraphAvgDistrib = { subgraphType: deepcopy(dicAvgDistrib) for subgraphType in lstSubgraphTypes }
				#~ dicGraphAvgValues = { subgraphType: multiprocessing.Manager().dict(dicAvgValues) for subgraphType in lstSubgraphTypes }
				#~ dicGraphAvgDistrib = { subgraphType: multiprocessing.Manager().dict(dicAvgDistrib) for subgraphType in lstSubgraphTypes }
				strAddInfo = "{}{}".format(strVarQuantity[0:4],lstVarValues[i])
				strGraphName = ""
				numNodes = 0
				for j in range(numAvg):
					graph = GraphClass(self.dicProperties)
					QtGui.qApp.processEvents()
					strGraphName = graph.getName().replace('.', 'p')
					numNodes = graph.getNodes()
					# for each subgraph (exc, inhib, all/complete)
					for subgraphType, dicAvg in dicGraphAvgValues.items():
						#~ dicGraphDistribs = dicGraphAvgDistrib[subgraphType]
						#~ procScalar = multiprocessing.Process(target=getNetworkProperties, args=(graph, subgraphType, self.dicNetAnalysis, dicPlotFunc, lstStrMeasurements, dicAvg, numAvg))
						#~ self.parent.gui.lstProcessesEvolProp[-1].append(procScalar)
						#~ procScalar.start()
						#~ # distributions
						#~ procDistrib = multiprocessing.Process(target=getNetworkDistrib, args=(graph, subgraphType, dicGraphDistribs,dicLog,bWeights,i,strAddInfo))
						#~ self.parent.gui.lstProcessesEvolProp[-1].append(procDistrib)
						#~ procDistrib.start()
						dicGraphDistribs = dicGraphAvgDistrib[subgraphType]
						QtGui.qApp.processEvents()
						# scalar properties
						getNetworkProperties(graph, subgraphType, self.dicNetAnalysis, dicPlotFunc, lstStrMeasurements, dicAvg, numAvg)
						QtGui.qApp.processEvents()
						# distributions
						getNetworkDistrib(graph, subgraphType, dicGraphDistribs,dicLog,bWeights,i,strAddInfo)
					# update progressBar
					self.parent.gui.progBarEvolProp.setValue(float(numAvg*i+j+1)*rStepToPercent)
					QtGui.qApp.processEvents()
				#~ for proc in self.parent.gui.lstProcessesEvolProp[-1]:
					#~ proc.join()
				#~ if self.parent.gui.lstProcessesEvolProp:
					#~ self.parent.gui.lstProcessesEvolProp.pop()
				#~ self.parent.gui.progBarEvolProp.setValue(float(numAvg*(i+1))*rStepToPercent)
				#~ QtGui.qApp.processEvents()
				# compute distrib and write averaged properties
				computeDistributions(numNodes, dicLog, dicGraphAvgDistrib, numAvg)
				writeAveragedMeasurements(self.parent, strGraphName, lstVarValues[i], dicStrGp, dicFileNames, dicGraphAvgValues, lstStrMeasurements, nNecessarySteps, i, strAddInfo)
				writeAveragedDistributions(self.parent, strGraphName, lstVarValues[i], dicStrGp, dicFileNames, dicGraphAvgDistrib, nNecessarySteps, i, strAddInfo)
			self.parent.gui.progBarEvolProp.setVisible(False)
			# plot the measurements
			if self.parent.gui.gbGraphMeas.isChecked():
				for subgraphType in lstSubgraphTypes:
					with open("data/" + dicFileNames[subgraphType] + ".gp","w") as fileGP:
						strGP,lstLabelsY2 = self.parent.gnuPlotter.genGpStrEvolMeas(dicFileNames[subgraphType],strVarQuantity,lstStrMeasurements)
						for col,strMeas in enumerate(lstStrMeasurements):
							strGP += self.parent.gnuPlotter.completeGpStrEvol(dicFileNames[subgraphType],lstLabelsY2,col,strMeas)
							if strMeas != lstStrMeasurements[-1]:
								strGP += ",\\\n"
						fileGP.write(strGP)
					strSubprocess = "data/" + dicFileNames[subgraphType] + ".gp"
					subprocess.call(["gnuplot", strSubprocess]) # careful to call it OUT of 'with open(...) as ...'
			# plot the distributions if necessary
			for subgraphType in lstSubgraphTypes:
				for strPlot in dicPlotFunc.keys():
					strSubprocess = "data/histo" + strPlot + "Exc.gp"
					with open(strSubprocess,"w") as fileGP:
						fileGP.write(dicStrGp[subgraphType][strPlot])
					subprocess.call(["gnuplot", strSubprocess]) # careful to call it OUT of 'with open(...) as ...'

	def getVaryingQuantities(self):
		dicVaryingQuantities = {}
		dicSSS = {"Start": 0, "Stop": 0, "Step": 0}
		for child in self.parent.gui.gbEvolX.children():
			if child != self.parent.gui.gbEvolX.layout():
				# on parcours toutes les groupBox des quantités pouvant varier
				if child.isChecked():
					strQuantity = child.title()
					for subChild in child.children():
						# on cherche les dsb et sb des Start, Stop, Step
						nLen = len(subChild.objectName())
						if subChild.objectName()[nLen-5:] == "Start":
							dicSSS["Start"] = subChild.value()
						if subChild.objectName()[nLen-4:] == "Stop":
							dicSSS["Stop"] = subChild.value()
						if subChild.objectName()[nLen-4:] == "Step":
							dicSSS["Step"] = subChild.value()
					dicVaryingQuantities[strQuantity] = np.arange(dicSSS["Start"], dicSSS["Stop"], dicSSS["Step"])
		return dicVaryingQuantities

	def showMeasurements(self):
		lstStrMeasurements = self.getMeasurements()
		dicData = {}
		idxCurrent = self.parent.gui.comboBoxSelectGraph.currentIndex()
		graph = self.parent.gui.comboBoxSelectGraph.itemData(idxCurrent)
		print(graph.getDensity())
		if self.parent.gui.gbGraphMeas.isChecked():
			if self.parent.gui.checkBoxAnalyzeExc.isChecked():
				subGraph = graph.genExcSubgraph()
				for strMeas in lstStrMeasurements:
					rMeas = self.dicNetAnalysis[strMeas](subGraph.getGraph())
					dicData[strMeas] = rMeas
				strTitle = graph.getName() + "Exc"
				self.plottingWidget.addData(strTitle,dicData)
				dicData = {}
			if self.parent.gui.checkBoxAnalyzeInhib.isChecked():
				subGraph = graph.genInhibSubgraph()
				for strMeas in lstStrMeasurements:
					rMeas = self.dicNetAnalysis[strMeas](subGraph.getGraph())
					dicData[strMeas] = rMeas
				strTitle = graph.getName() + "Inhib"
				self.plottingWidget.addData(strTitle,dicData)
				dicData = {}
			if self.parent.gui.checkBoxAnalyzeAll.isChecked():
				for strMeas in lstStrMeasurements:
					rMeas = self.dicNetAnalysis[strMeas](graph.getGraph())
					dicData[strMeas] = rMeas
				strTitle = graph.getName()
				self.plottingWidget.addData(strTitle,dicData)
		self.plottingWidget.show()

	def __del__(self):
		self.dicNetAnalysis = None
		print("GraphAnalysis died")
