#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Weights manager for NetGen """


from copy import deepcopy



#
#---
# Generating weights
#------------------------

class WeightsManager:
	def __init__(self,parent):
		self.parent = parent
		self.dicWProp = {}
		# dic linking the weight generator
		self.dicGraphWeightsType = {	"Gaussian": self.setGraphGaussWeights,
										"Lognormal": self.setGraphLogNormWeights
									}
		self.dicConnectWeightsType = {	"Gaussian": self.setConnectGaussWeights,
										"Lognormal": self.setConnectLogNormWeights
									}

	def generateWeightsDictionnary(self):
		self.reset()
		if self.parent.gui.tabWidget.currentIndex() == 0: # graph generator
			if self.parent.gui.wTabWeights.currentIndex() == 0: #uncorr
				self.dicWProp["Distribution"] = self.parent.gui.cbWeightsDistrib.currentText()
				self.dicGraphWeightsType[self.dicWProp["Distribution"]]() # we generate the distributions characteristics
			else:
				self.dicWProp["Distribution"] = self.parent.gui.cbWeightsCorrelation.currentText() # "betweenness" ou "degree"
				self.dicWProp["Max"] = self.parent.gui.dsbMaxWeightCorr.value()
				self.dicWProp["Min"] = self.parent.gui.dsbMinWeightCorr.value()
		elif self.parent.gui.tabWidget.currentIndex() == 3: # connectivity
			if self.parent.gui.wTabWeightsConnect.currentIndex() == 0: #uncorr
				self.dicWProp["Distribution"] = self.parent.gui.cbWeightsDistribConnect.currentText()
				self.dicConnectWeightsType[self.dicWProp["Distribution"]]() # we generate the distributions characteristics
			else:
				self.dicWProp["Distribution"] = self.parent.gui.cbWeightsCorrelConnectivity.currentText() # "betweenness" ou "x-degree"
				self.dicWProp["Max"] = self.parent.gui.dsbMaxWeightConnect.value()
				self.dicWProp["Min"] = self.parent.gui.dsbMinWeightConnect.value()
		return deepcopy(self.dicWProp)

	def setGraphGaussWeights(self):
		self.dicWProp["MeanExc"] = self.parent.gui.dsbMeanExcWeights.value()
		self.dicWProp["VarExc"] = self.parent.gui.dsbVarExcWeights.value()
		self.dicWProp["MeanInhib"] = self.parent.gui.dsbMeanInhibWeights.value()
		self.dicWProp["VarInhib"] = self.parent.gui.dsbVarInhibWeights.value()

	def setGraphLogNormWeights(self):
		self.dicWProp["ScaleExc"] = self.dsbScaleExcWeights.value()
		self.dicWProp["LocationExc"] = self.dsbLocationExcWeights.value()
		self.dicWProp["ScaleInhib"] = self.dsbScaleInhibWeights.value()
		self.dicWProp["LocationInhib"] = self.dsbLocationInhibWeights.value()

	def setConnectGaussWeights(self):
		self.dicWProp["MeanExc"] = self.parent.gui.dsbMeanExcWConnect.value()
		self.dicWProp["VarExc"] = self.parent.gui.dsbVarExcWConnect.value()
		self.dicWProp["MeanInhib"] = self.parent.gui.dsbMeanInhibWConnect.value()
		self.dicWProp["VarInhib"] = self.parent.gui.dsbVarInhibWConnect.value()

	def setConnectLogNormWeights(self):
		self.dicWProp["ScaleExc"] = self.dsbScaleExcWConnect.value()
		self.dicWProp["LocationExc"] = self.dsbLocationExcWConnect.value()
		self.dicWProp["ScaleInhib"] = self.dsbScaleInhibWConnect.value()
		self.dicWProp["LocationInhib"] = self.dsbLocationInhibWConnect.value()

	def reset(self):
		self.dicWProp = {}

	def close(self):
		self.parent = None
		self.dicGraphWeightsType = None
		self.dicConnectWeightsType = None
		self.dicWProp = None

	def __del__(self):
		print("Weightsmanager died")
