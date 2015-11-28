#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Reservoir computing analysis for NetGen """

import sys
sys.path.append("netTools/")
sys.path.append("plottingTools/")
import numpy as np

from ... import GraphClass, InputConnect
from .plotWidget import PlotWidget


class ReservoirComputing:
	def __init__(self,parent):
		self.parent = parent
		self.graphReservoir = None
		# properties of the connectivity to generate
		self.lstCorrelType = []
		self.bAntiCorr = False
		self.dicWProp = {}
		self.plottingWidget = PlotWidget()

	#
	#---
	# Plotting distributions
	#-------------------------------

	# degree
	
	def plotConnectivityDegree(self):
		idxCurrent = self.parent.comboBoxSelectConnect.currentIndex()
		self.connect = self.parent.comboBoxSelectConnect.itemData(idxCurrent)
		lstConnectDeg = None
		if self.connect.getType() == "input":
			lstConnectDeg = np.sum(np.absolute(self.connect.getMatConnect()),axis=1)
		elif self.connect.getType() == "readout":
			lstConnectDeg = np.sum(np.absolute(self.connect.getMatConnect()),axis=0)
		# plot the result
		lstNeurons = np.arange(min(self.connect.getDimensions()))
		print(lstNeurons,lstConnectDeg)
		dicPlots = {"Degree repartition of the connectivity": [np.array([lstNeurons,lstConnectDeg]), "Degree", "Input neuron"]}
		plotView = self.plottingWidget.createPlotView(dicPlots)
		self.plottingWidget.addPlotView(self.connect.getName(),plotView)
		self.plottingWidget.show()
		self.connect = None

	# weights
	
	def plotConnectivityWeightDistrib(self):
		idxCurrent = self.parent.comboBoxSelectConnect.currentIndex()
		self.connect = self.parent.comboBoxSelectConnect.itemData(idxCurrent)
		numBins = self.connect.getDimensions()[0]*self.connect.getDimensions()[1]/35
		bins = np.linspace(self.connect.getMatConnect().min(), self.connect.getMatConnect().max(), numBins)
		lstConnectWeights = np.reshape(self.connect.getMatConnect(),(1,-1))
		vecCounts,vecWeight = np.histogram(lstConnectWeights, bins)
		# plot the result
		print(len(vecWeight),len(vecCounts))
		dicPlots = {"Weight distribution of the connectivity": [np.array([vecWeight[:-1],vecCounts]), "Count", "Weight"]}
		plotView = self.plottingWidget.createPlotView(dicPlots)
		self.plottingWidget.addPlotView(self.connect.getName(),plotView)
		self.plottingWidget.show()
		self.connect = None

	
	#
	#---
	# Correlations
	#-------------------------------

	# degree-degree

	def compareDegrees(self, reservoir=None, connectivity=None):
		if reservoir == None:
			idxCurrent = self.parent.comboBoxReservoir.currentIndex()
			self.graphReservoir = self.parent.comboBoxReservoir.itemData(idxCurrent)
		if connectivity == None:
			idxCurrent = self.parent.comboBoxSelectConnect.currentIndex()
			self.connect = self.parent.comboBoxSelectConnect.itemData(idxCurrent)
		lstReservoirTotDeg = np.absolute(lstNodesDegrees(self.graphReservoir,"total"))
		lstReservoirInDeg = np.absolute(lstNodesDegrees(self.graphReservoir,"in"))
		lstReservoirOutDeg = np.absolute(lstNodesDegrees(self.graphReservoir,"out"))
		lstConnectDeg = np.sum(np.absolute(self.connect.getMatConnect()),axis=0)
		# plot the result
		dicPlots = {	"Reservoir (tot) VS connectivity degrees": [np.array([lstConnectDeg,lstReservoirTotDeg]), "Degree from connectivity", "Total-degree (reservoir)"],
						"Reservoir (in) VS connectivity degrees": [np.array([lstConnectDeg,lstReservoirInDeg]), "Degree from connectivity", "In-degree (reservoir)"],
						"Reservoir (out) VS connectivity degrees": [np.array([lstConnectDeg,lstReservoirOutDeg]), "Degree from connectivity", "Out-degree (reservoir)"]
					}
		plotView = self.plottingWidget.createPlotView(dicPlots)
		self.plottingWidget.addPlotView(self.connect.getName(),plotView)
		self.plottingWidget.show()
		# dereference
		self.graphReservoir = None
		self.connect = None

	# degree-betweenness
	
	def compareDegBetw(self, reservoir=None, connectivity=None):
		if reservoir == None:
			idxCurrent = self.parent.comboBoxReservoir.currentIndex()
			self.graphReservoir = self.parent.comboBoxReservoir.itemData(idxCurrent)
		if connectivity == None:
			idxCurrent = self.parent.comboBoxSelectConnect.currentIndex()
			self.connect = self.parent.comboBoxSelectConnect.itemData(idxCurrent)
		lstReservoirBetw = np.absolute(betwCentrality(self.graphReservoir)[0].a)
		lstConnectDeg = np.sum(np.absolute(self.connect.getMatConnect()),axis=0)
		# plot the result
		dicPlots = {	"Reservoir betweenness VS connectivity degree": [np.array([lstConnectDeg,lstReservoirBetw]), "Degree from connectivity", "Betweenness (reservoir)"] }
		plotView = self.plottingWidget.createPlotView(dicPlots)
		self.plottingWidget.addPlotView(self.connect.getName(),plotView)
		self.plottingWidget.show()
		# dereference
		self.graphReservoir = None
		self.connect = None

	
	#
	#---
	# Batch analysis
	#-------------------------------

	# load data
	
	def setBatch(self,lstBatch,strDirectory):
		self.batch = lstBatch
		self.batchDirectory = strDirectory
		self.parent.pbBatchAnalysis.setEnabled(True)

	# analyze
	
	def analyseBatch(self):
		self.plottingWidget.close()
		strResult = ""
		# look at the required comparisons
		if self.parent.checkBoxCorrDegDeg.isChecked():
			strResult += "In-deg. correl\tOut-deg. correl\tTotal-deg. correl"
		if self.parent.checkBoxCorrDegBetw.isChecked():
			if strResult != "":
				strResult += "\t"
			strResult += "Deg./Betw. correl"
		if self.parent.checkBoxInOutSimilarity.isChecked():
			if strResult != "":
				strResult += "\t"
			strResult += "In/Out similarity"
		strResult += "\n"
		# check which kind of matrices are to be analyzed
		bInConnect = False
		bOutConnect = False
		bReservoir = False
		if "in" in self.batch[0].lower():
			bInConnect = True
		if "out" in self.batch[0].lower():
			bOutConnect = True
		if "res" in self.batch[0].lower():
			bReservoir = True
		# for each reservoir/connectivity pair
		for i in range(1,len(self.batch)):
			strLine = self.batch[i]
			# generate in connectivity
			idxInConnectNameEnd = 0
			idxReservoirNameEnd = 0
			if bInConnect:
				idxInConnectNameEnd = strLine.find(" ")
				fileNameInConnect = self.batchDirectory + strLine[:idxInConnectNameEnd]
				self.inConnect = self.parent.fileManager.genConnectFromFile(fileNameInConnect)
			# generate reservoir
			if bReservoir:
				idxReservoirNameEnd = strLine.find(" ",idxInConnectNameEnd+1)
				fileNameReservoir =  self.batchDirectory + strLine[idxInConnectNameEnd+1:idxReservoirNameEnd]
				self.graphReservoir = self.parent.fileManager.genGraphFromFile(fileNameReservoir)
				self.excReservoir = self.graphReservoir.genExcSubgraph()
				self.inhibReservoir = self.graphReservoir.genInhibSubgraph()
			# generate out connectivity
			if bOutConnect:
				fileNameOutConnect = self.batchDirectory + strLine[idxReservoirNameEnd+1:]
				self.outConnect = self.parent.fileManager.genConnectFromFile(fileNameOutConnect)
			if self.parent.checkBoxCorrDegDeg.isChecked() and bOutConnect and bReservoir:
				tplCorrDegDeg = self.calcDegDegCorrel()
				strResult += "{}\t{}\t{}".format(tplCorrDegDeg[0], tplCorrDegDeg[1],tplCorrDegDeg[2])
			if self.parent.checkBoxCorrDegBetw.isChecked() and bOutConnect and bReservoir:
				if strResult[-1] != "n":
					strResult += "\t"
				strResult += "{}".format(self.calcDegBetwCorrel())
			if self.parent.checkBoxInOutSimilarity.isChecked()  and bOutConnect and bInConnect:
				if strResult[-1] != "n":
					strResult += "\t"
				strResult += "{}".format(self.calcInOutSimilarity())
			strResult += "\n"
		fileName = self.parent.fileManager.dialogFileName("Save batch analysis")
		if fileName != "":
			with open(fileName,"w") as fileBatchAnalysis:
				fileBatchAnalysis.write(strResult)
		# dereference
		self.graphReservoir = None
		self.excReservoir = None
		self.inhibReservoir = None
		self.inConnect = None
		self.outConnect = None

	# batch calculations

	def calcDegDegCorrel(self):
		lstConnectDeg = np.sum(np.absolute(self.outConnect.getMatConnect()),axis=1)
		lstReservoirInDeg = lstNodesDegrees(self.graphReservoir,"in")
		lstReservoirOutDeg = lstNodesDegrees(self.graphReservoir,"out")
		lstReservoirTotDeg = lstNodesDegrees(self.graphReservoir,"total")
		lstExcResInDeg = lstNodesDegrees(self.excReservoir,"in")
		lstExcResOutDeg = lstNodesDegrees(self.excReservoir,"out")
		lstExcResTotDeg = lstNodesDegrees(self.excReservoir,"total")
		lstInhibResInDeg = lstNodesDegrees(self.inhibReservoir,"in")
		lstInhibResOutDeg = lstNodesDegrees(self.inhibReservoir,"out")
		lstInhibResTotDeg = lstNodesDegrees(self.inhibReservoir,"total")
		# plot if required:
		if self.parent.checkBoxCorrPlot.isChecked():
			# total graph
			dicPlots = {	"In-degree correlation": [np.array([lstConnectDeg,lstReservoirInDeg]), "Res. in-degree", "Degree from connectivity"],
							"Out-degree correlation": [np.array([lstConnectDeg,lstReservoirOutDeg]), "Res. out-degree", "Degree from connectivity"],
							"Total-degree correlation": [np.array([lstConnectDeg,lstReservoirTotDeg]), "Res. total-degree", "Degree from connectivity"]	
						}
			plotView = self.plottingWidget.createPlotView(dicPlots)
			self.plottingWidget.addPlotView(self.outConnect.getName(),plotView)
			# exc graph
			dicPlotsExc = {	"In-degree correlation": [np.array([lstConnectDeg,lstExcResInDeg]), "Res. in-degree", "Degree from connectivity"],
							"Out-degree correlation": [np.array([lstConnectDeg,lstExcResOutDeg]), "Res. out-degree", "Degree from connectivity"],
							"Total-degree correlation": [np.array([lstConnectDeg,lstExcResTotDeg]), "Res. total-degree", "Degree from connectivity"]
						}
			plotViewExc = self.plottingWidget.createPlotView(dicPlotsExc)
			self.plottingWidget.addPlotView(self.outConnect.getName() + ' - Exc.',plotViewExc)
			# inhib graph
			dicPlotsInhib = {	"In-degree correlation": [np.array([lstConnectDeg,lstInhibResInDeg]), "Res. in-degree", "Degree from connectivity"],
							"Out-degree correlation": [np.array([lstConnectDeg,lstInhibResOutDeg]), "Res. out-degree", "Degree from connectivity"],
							"Total-degree correlation": [np.array([lstConnectDeg,lstInhibResTotDeg]), "Res. total-degree", "Degree from connectivity"]
						}
			plotViewInhib = self.plottingWidget.createPlotView(dicPlotsInhib)
			self.plottingWidget.addPlotView(self.outConnect.getName() + " - Inhib.",plotViewInhib)
			self.plottingWidget.show()
		# compute the correlation coefficients
		rNormOutDeg = np.linalg.norm(lstConnectDeg)
		rCoeffIn = 2*np.dot(lstConnectDeg,lstReservoirInDeg)/(rNormOutDeg*np.linalg.norm(lstReservoirInDeg))-1
		rCoeffOut = 2*np.dot(lstConnectDeg,lstReservoirOutDeg)/(rNormOutDeg*np.linalg.norm(lstReservoirOutDeg))-1
		rCoeffTot = 2*np.dot(lstConnectDeg,lstReservoirTotDeg)/(rNormOutDeg*np.linalg.norm(lstReservoirTotDeg))-1
		return rCoeffIn,rCoeffOut,rCoeffTot

	def calcDegBetwCorrel(self):
		lstConnectDeg = np.sum(np.absolute(self.outConnect.getMatConnect()),axis=1)
		lstReservoirBetw = betwCentrality(self.graphReservoir)[0].a
		lstExcResBetw = betwCentrality(self.excReservoir)[0].a
		lstInhibResBetw = betwCentrality(self.inhibReservoir)[0].a
		# plot if required:
		if self.parent.checkBoxCorrPlot.isChecked():
			dicPlots = {	"Betw. correl. (total graph)": [np.array([lstConnectDeg,lstReservoirBetw]), "Res. betweenness", "Degree from connectivity"],
							"Betw. correl. (exc. subgraph)": [np.array([lstConnectDeg,lstExcResBetw]), "Res. betweenness", "Degree from connectivity"],
							"Betw. correl. (inhib. subgraph)": [np.array([lstConnectDeg,lstInhibResBetw]), "Res. betweenness", "Degree from connectivity"]
						}
			plotView = self.plottingWidget.createPlotView(dicPlots)
			self.plottingWidget.addPlotView(self.outConnect.getName(),plotView)
			self.plottingWidget.show()
		# compute the correlation coefficient
		rCoeffBetw = 2*np.dot(lstConnectDeg,lstReservoirBetw)/(np.linalg.norm(lstConnectDeg)*np.linalg.norm(lstReservoirBetw))-1
		return rCoeffBetw

	def calcInOutSimilarity(self):
		matElementsProduct = np.multiply(self.inConnect.getMatConnect(),np.transpose(self.outConnect.getMatConnect()))
		rSimilarity = np.absolute(np.sum(matElementsProduct))/np.sqrt(np.linalg.norm(self.inConnect.getMatConnect())*np.linalg.norm(self.outConnect.getMatConnect()))
		return rSimilarity

	
	#
	#---
	# Generating connectivities
	#-------------------------------

	# for one or all graphs
	
	def makeConnectivities(self):
		if self.parent.comboBoxConnectBaseReservoir.currentText() == "All":
			nGraphs = self.parent.comboBoxConnectBaseReservoir.count()
			for i in range(1,nGraphs):
				self.parent.comboBoxConnectBaseReservoir.setCurrentIndex(i)
				self.genAndSaveOneConnectivity()
		else:
			self.genAndSaveOneConnectivity()

	# generate and save
	
	def genAndSaveOneConnectivity(self):
		self.resetCorrelations()
		self.getConnectivityProperties()
		for strCorr in self.lstCorrelType:
			connectivity = self.generateConnectivity(strCorr)
			self.parent.lstConnect.append(connectivity)
			self.parent.new_connectivity_added()
			# save the connectivity
			if self.parent.checkBoxSaveConnect.isChecked():
				strCorrel = "Anti" if self.bAntiCorr else ""
				strCorrel += strCorr
				self.parent.fileManager.saveConnect(strCorrel,connectivity)
				# update the batch file
				strBatch = "{}\t{}\n".format(connectivity.get_name(),self.parent.comboBoxConnectBaseReservoir.currentText())
				try:
					with open("data/NeighbourList/batch","a") as fileBatch:
						fileBatch.write(strBatch)
				except:
					with open("data/NeighbourList/batch","w") as fileBatch:
						fileBatch.write(strBatch)
		self.graphReservoir = None

	# detailed generation of connectivity
	
	def generateConnectivity(self,strCorr):
		self.resetDicProp()
		self.dicWProp = self.parent.weightsManager.generateWeightsDictionnary()
		dicProp = {"Density": self.rDensity, "InhibFrac": self.rInhibFrac}
		dicProp.update(self.dicWProp)
		connectivity = InputConnect()
		connectivity.set_dimensions((self.numIONeurons,self.numGraphNodes))
		connectivity.gen_matrix(dicProp, self.graphReservoir, strCorr, self.bAntiCorr)
		strCorrel = "Anti" if self.bAntiCorr else ""
		strCorrel += strCorr[:5]
		rFracInhib = self.parent.dsbFracInhibConnect.value()
		rDens = self.parent.gui.dsbConnectivityDensity.value()
		rWeights1 = 0.
		rWeights2 = 0.
		strWeights = ""
		strGraphName = self.graphReservoir.getName()
		strName = ""
		if self.parent.wTabWeightsConnect.currentIndex() == 0:
			strWeights = self.parent.cbWeightsDistrib.currentText()[:5]
			rWeights1 = self.parent.dsbMeanExcWConnect.value()
			rWeights2 = self.parent.dsbVarExcWConnect.value()
		else:
			strWeights = self.parent.cbWeightsCorrelation.currentText()
			rWeights1 = self.parent.dsbMaxWeightConnect.value()
			rWeights2 = self.parent.dsbMinWeightConnect.value()
		strName = "Connect_{0}_{1}-{2}_{3}{4}-{5}_{6}".format(strCorrel,rFracInhib,rDens,strWeights,rWeights1,rWeights2,strGraphName)
		connectivity.set_name(strName)
		return connectivity

	# get the properties
	
	def getConnectivityProperties(self):
		self.numIONeurons = self.parent.gui.sbNumIONeurons.value()
		self.rDensity = self.parent.gui.dsbConnectivityDensity.value()
		self.rInhibFrac = self.parent.gui.dsbFracInhibConnect.value()
		idxCurrent = self.parent.gui.comboBoxConnectBaseReservoir.currentIndex()
		self.graphReservoir = self.parent.gui.comboBoxConnectBaseReservoir.itemData(idxCurrent)
		self.numGraphNodes = self.graphReservoir.getNodes()
		# add list of correlation types to generate
		if self.parent.checkBoxRandomCorrel.isChecked():
			self.lstCorrelType.append("Random")
		if self.parent.checkBoxInDegCorr.isChecked():
			self.lstCorrelType.append("In-degree")
		if self.parent.checkBoxOutDegCorr.isChecked():
			self.lstCorrelType.append("Out-degree")
		if self.parent.checkBoxTotalDegCorr.isChecked():
			self.lstCorrelType.append("Total-degree")
		if self.parent.checkBoxBetwCorr.isChecked():
			self.lstCorrelType.append("Betweenness")
		if self.parent.checkBoxAntiCorr.isChecked():
			self.bAntiCorr = True
		else:
			self.bAntiCorr = False

	
	#
	#---
	# Resetting and deleting
	#-------------------------------
	
	def resetDicProp(self):
		self.dicWProp = {}

	def resetCorrelations(self):
		self.lstCorrelType = []

	def __del__(self):
		print("ResComputer died")
