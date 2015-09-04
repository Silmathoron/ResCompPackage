#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main file of the "Cute pie" programm for network generation and analysis """


from PySide import QtGui, QtCore
from PySide.QtGui import QMainWindow
#import gtk # graph_tool utilise gtk3, donc si le pyside appelle gtk2, importer gtk pour éviter les conflits

from ui_NetGenWindow import *



#
#---
# NetWindow class
#-------------------------

class NetWindow(QMainWindow, Ui_MainWindow,object):
	def __init__(self, parent=None):
		# on crée à partir du constructeur parent de Ui_MainWindow
		super(NetWindow, self).__init__()
		# on initialise avec les paramètres définis par Ui_MainWindow
		self.setupUi(self)
		# on passe en UTF8
		QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("UTF-8"))
		# on initialize les paramètres
		self.dicGraphType = {0: self.setErdosType,
								1: self.setFreeScaleType,
								2: self.setEDRType }
		self.dicEvolType = {0: self.setErdosEvol,
								1: self.setFreeScaleEvol,
								2: self.setEDREvol }
		self.dicWeightsType = {	"Gaussian": self.setGaussWeights,
								"Lognormal": self.setLogNormWeights}
		self.dicCBtoGBMeas = {	self.checkBoxAssort: self.gbAssort,
								self.checkBoxCluster: self.gbClustering,
								self.checkBoxRecip: self.gbReciprocity,
								self.checkBoxCC: self.gbConnectComp,
								self.checkBoxDiam: self.gbDiameter,
								self.checkBoxSpectrum: self.gbSpectrum}
		self.dicCBtoVarGB = {	"In-degree exponent": self.gbInDegExp,
								"Out-degree exponent": self.gbOutDegExp,
								"Reciprocity": self.gbRecip,
								"Lambda": self.gbLambda,
								"Neuron density (/mm^2)": self.gbNeuronDens}
		self.dicCBtoGBevol = {	self.checkBoxDensityEvol: self.gbVarDensity,
								self.checkBoxEdgesEvol: self.gbVarEdges,
								self.checkBoxNodesEvol: self.gbVarNodes,
								self.checkBoxInDegExpEvol: self.gbInDegExp,
								self.checkBoxOutDegExpEvol: self.gbOutDegExp,
								self.checkBoxReciprocityEvol: self.gbRecip,
								self.checkBoxLambdaEvol: self.gbLambda,
								self.checkBoxNeuronDensEvol: self.gbNeuronDens}
		self.dicGBtoCBgen = { 	self.gbVarDensitySeries: self.checkBoxDensity,
								self.gbVarEdgesSeries: self.checkBoxEdges,
								self.gbVarNodesSeries: self.checkBoxNodes,
								self.gbInDegExpSeries: self.checkBoxInDegExp,
								self.gbOutDegExpSeries: self.checkBoxOutDegExp,
								self.gbRecipSeries: self.checkBoxReciprocity,
								self.gbLambdaSeries: self.checkBoxLambda,
								self.gbNeuronDensSeries: self.checkBoxNeurDens}
		self.dicGBtoSBgen = {	self.gbVarDensitySeries: self.dsbDensity,
								self.gbVarEdgesSeries: self.sbEdges,
								self.gbVarNodesSeries: self.sbNodes,
								self.gbInDegExpSeries: self.dsbInDegExp,
								self.gbOutDegExpSeries: self.dsbOutDegExp,
								self.gbRecipSeries: self.dsbRecip,
								self.gbLambdaSeries: self.dsbLambda,
								self.gbNeuronDensSeries: self.sbNeuronDens}
		self.dicGBtoSBevol = {	self.gbVarDensity: self.dsbDensityEvol,
								self.gbVarEdges: self.sbEdgesEvol,
								self.gbVarNodes: self.sbNodesEvol,
								self.gbInDegExp: self.dsbInDegExpEvol,
								self.gbOutDegExp: self.dsbOutDegExpEvol,
								self.gbRecip: self.dsbRecipEvol,
								self.gbLambda: self.dsbLambdaEvol,
								self.gbNeuronDens: self.sbNeuronDensEvol}
		# les variables d'interface pour gérer l'interaction nodes/edges/density
		self.lstUncheckEvolCB = [self.checkBoxEdgesEvol,self.checkBoxDensityEvol]
		self.lstCheckEvolCB = [self.checkBoxNodesEvol]
		self.lstUncheckGenCB = [self.checkBoxEdges]
		self.lstCheckGenCB = [self.checkBoxDensity,self.checkBoxNodes]
		# initialisation
		self.initAll()

	def initAll(self):
		#on initialise l'interface
		self.setNetGenInterface()
		# on désactive les boutons de save/plot
		self.pbPlotDistrib.setEnabled(False)
		self.pbSave.setEnabled(False)
		#on connecte
			# les maj interface
		QtCore.QObject.connect(self.cbNetType, QtCore.SIGNAL("currentIndexChanged(int)"), self.setNetGenInterface)
		QtCore.QObject.connect(self.cbNetTypeEvol, QtCore.SIGNAL("currentIndexChanged(int)"), self.setNetGenInterface)
		QtCore.QObject.connect(self.cbWeightsDistrib, QtCore.SIGNAL("currentIndexChanged(int)"), self.setNetGenInterface)
		# supervising the interface
			# evol
		self.gbGraphMeas.clicked.connect(self.setEnableFrame)
		self.checkBoxAssort.clicked.connect(self.setEvolParam)
		self.checkBoxCluster.clicked.connect(self.setEvolParam)
		self.checkBoxRecip.clicked.connect(self.setEvolParam)
		self.checkBoxCC.clicked.connect(self.setEvolParam)
		self.checkBoxDiam.clicked.connect(self.setEvolParam)
		self.checkBoxSpectrum.clicked.connect(self.setEvolParam)
		self.gbInDegExp.clicked.connect(self.setEvolParam)
		self.gbOutDegExp.clicked.connect(self.setEvolParam)
		self.gbRecip.clicked.connect(self.setEvolParam)
		self.gbLambda.clicked.connect(self.setEvolParam)
		self.gbNeuronDens.clicked.connect(self.setEvolParam)
		self.checkBoxInDegExpEvol.clicked.connect(self.setEvolParam)
		self.checkBoxOutDegExpEvol.clicked.connect(self.setEvolParam)
		self.checkBoxReciprocityEvol.clicked.connect(self.setEvolParam)
		self.checkBoxLambdaEvol.clicked.connect(self.setEvolParam)
		self.checkBoxNeuronDensEvol.clicked.connect(self.setEvolParam)
		self.checkBoxAvg.clicked.connect(self.setEvolParam)
			# gen/series
		self.gbGenSeries.clicked.connect(self.switchSingleSeries)
		self.gbInDegExpSeries.clicked.connect(self.updateGenVariables)
		self.gbOutDegExpSeries.clicked.connect(self.updateGenVariables)
		self.gbRecipSeries.clicked.connect(self.updateGenVariables)
		self.gbLambdaSeries.clicked.connect(self.updateGenVariables)
		self.gbNeuronDensSeries.clicked.connect(self.updateGenVariables)
		self.checkBoxInDegExp.clicked.connect(self.updateGenVariables)
		self.checkBoxOutDegExp.clicked.connect(self.updateGenVariables)
		self.checkBoxReciprocity.clicked.connect(self.updateGenVariables)
		self.checkBoxLambda.clicked.connect(self.updateGenVariables)
		self.checkBoxNeurDens.clicked.connect(self.updateGenVariables)
		for child in self.gbGenSeries.children():
			if child != self.gbGenSeries.layout():
				for subChild in child.children():
					if subChild.__class__ == QtGui.QDoubleSpinBox or subChild.__class__ == QtGui.QSpinBox:
						subChild.valueChanged.connect(self.updateGenStaticValue)
		for child in self.gbEvolX.children():
			if child != self.gbGenSeries.layout():
				for subChild in child.children():
					if subChild.__class__ == QtGui.QDoubleSpinBox or subChild.__class__ == QtGui.QSpinBox:
						subChild.valueChanged.connect(self.updateEvolStaticValue)
		#connect comboBoxSelectGraph
		self.comboBoxSelectGraph.currentIndexChanged.connect(self.updateSbNodesToKeep)
		# supervising the nodes/edges/density interactions
			# graph gen
		self.checkBoxNodes.clicked.connect(self.handlerGen)
		self.checkBoxDensity.clicked.connect(self.handlerGen)
		self.checkBoxEdges.clicked.connect(self.handlerGen)
		self.gbVarDensitySeries.clicked.connect(self.handlerGen)
		self.gbVarEdgesSeries.clicked.connect(self.handlerGen)
		self.gbVarNodesSeries.clicked.connect(self.handlerGen)
			# evol prop
		self.gbVarDensity.clicked.connect(self.handlerEvol)
		self.gbVarEdges.clicked.connect(self.handlerEvol)
		self.gbVarNodes.clicked.connect(self.handlerEvol)
		self.checkBoxNodesEvol.clicked.connect(self.handlerEvol)
		self.checkBoxDensityEvol.clicked.connect(self.handlerEvol)
		self.checkBoxEdgesEvol.clicked.connect(self.handlerEvol)
		# connect closeEvent
		QtCore.QObject.connect(self, QtCore.SIGNAL('triggered()'), self.closeEvent)

	#-------------#
	# L'interface #
	#-------------#

	def setNetGenInterface(self):
		# launch the associated function
		self.dicGraphType[self.cbNetType.currentIndex()]()
		self.dicEvolType[self.cbNetTypeEvol.currentIndex()]()
		self.dicWeightsType[self.cbWeightsDistrib.currentText()]()
		# hide progress bar
		self.progBarEvolProp.setVisible(False)

	def switchSingleSeries(self):
		if not self.gbGenSeries.isChecked():
			lstNED = [self.gbVarDensitySeries,self.gbVarNodesSeries,self.gbVarEdgesSeries]
			for gb,cb in self.dicGBtoCBgen.items():
				if gb in lstNED:
					if gb.isChecked():
						gb.setChecked(False)
						cb.setCheckState(QtCore.Qt.Checked)
						idxCB = self.lstUncheckGenCB.index(cb)
						self.lstCheckGenCB.append(self.lstUncheckGenCB.pop(idxCB))
				else:
					gb.setChecked(False)
					cb.setCheckState(QtCore.Qt.Checked)

	#-----------------------#
	# Nodes, edges, density #
	#-----------------------#

	def handlerGen(self):
		nCount = 0
		widget = self.sender()
		widgetCB = None
		if widget in self.wBoxNetType.children():
			widgetCB = widget
			widget = list(self.dicGBtoCBgen.keys())[list(self.dicGBtoCBgen.values()).index(widgetCB)]
			# update the lists
			if widgetCB.isChecked():
				idxWidget = self.lstUncheckGenCB.index(widgetCB)
				self.lstCheckGenCB.append(self.lstUncheckGenCB.pop(idxWidget))
				if self.gbGenSeries.isChecked():
					widget.setChecked(False)
			else:
				idxWidget = self.lstCheckGenCB.index(widgetCB)
				self.lstUncheckGenCB.append(self.lstCheckGenCB.pop(idxWidget))
		else:
			widgetCB = self.dicGBtoCBgen[widget]
			if widgetCB.isChecked() and widget.isChecked():
				widgetCB.setCheckState(QtCore.Qt.Unchecked)
				idxWidget = self.lstCheckGenCB.index(widgetCB)
				self.lstUncheckGenCB.append(self.lstCheckGenCB.pop(idxWidget))
		# check the situations of the GB
		if self.gbGenSeries.isChecked():
			if self.gbVarDensitySeries.isChecked():
				nCount += 1
			if self.gbVarEdgesSeries.isChecked():
				nCount +=1
			if self.gbVarNodesSeries.isChecked():
				nCount +=1
			# we can have only one gb checked
			if nCount >= 2:
				self.gbVarDensitySeries.setChecked(False)
				self.gbVarEdgesSeries.setChecked(False)
				self.gbVarNodesSeries.setChecked(False)
				widget.setChecked(True)
		# update the checkBoxes
		# count
		nCountCB = 0
		if self.checkBoxNodes.isChecked():
			nCountCB+=1
		if self.checkBoxEdges.isChecked():
			nCountCB+=1
		if self.checkBoxDensity.isChecked():
			nCountCB+=1
		if nCount == 0:
			while nCountCB < 2:
				wOldestUnchecked = self.lstUncheckGenCB[0]
				self.lstCheckGenCB.append(self.lstUncheckGenCB.pop(0))
				wOldestUnchecked.setCheckState(QtCore.Qt.Checked)
				nCountCB +=1
			if nCountCB == 3:
				self.lstUncheckGenCB.append(self.lstCheckGenCB.pop(0))
				self.lstUncheckGenCB[-1].setCheckState(QtCore.Qt.Unchecked)
				nCountCB -=1
		else:
			if nCountCB == 2:
				self.lstUncheckGenCB.append(self.lstCheckGenCB.pop(0))
				self.lstUncheckGenCB[-1].setCheckState(QtCore.Qt.Unchecked)
			if nCountCB == 0:
				wOldestUnchecked = self.lstUncheckGenCB[0]
				if wOldestUnchecked != widgetCB:
					self.lstCheckGenCB.append(self.lstUncheckGenCB.pop(0))
					wOldestUnchecked.setCheckState(QtCore.Qt.Checked)
				else:
					self.lstCheckGenCB.append(self.lstUncheckGenCB.pop(1))
					self.lstCheckGenCB[-1].setCheckState(QtCore.Qt.Checked)

	def handlerEvol(self):
		widget = self.sender()
		widgetCB = None
		if widget in self.wBoxNetTypeEvol.children():
			widgetCB = widget
			widget = self.dicCBtoGBevol[widgetCB]
			# update the lists
			if widgetCB.isChecked():
				idxWidget = self.lstUncheckEvolCB.index(widgetCB)
				self.lstCheckEvolCB.append(self.lstUncheckEvolCB.pop(idxWidget))
				widget.setChecked(False)
			else:
				idxWidget = self.lstCheckEvolCB.index(widgetCB)
				self.lstUncheckEvolCB.append(self.lstCheckEvolCB.pop(idxWidget))
		else:
			widgetCB = list(self.dicCBtoGBevol.keys())[list(self.dicCBtoGBevol.values()).index(widget)]
			if widgetCB.isChecked() and widget.isChecked():
				widgetCB.setCheckState(QtCore.Qt.Unchecked)
				idxWidget = self.lstCheckEvolCB.index(widgetCB)
				self.lstUncheckEvolCB.append(self.lstCheckEvolCB.pop(idxWidget))
		# count CB and GB
		nCount = 0
		nCountCB = 0
		if self.checkBoxNodesEvol.isChecked():
			nCountCB+=1
		if self.checkBoxEdgesEvol.isChecked():
			nCountCB+=1
		if self.checkBoxDensityEvol.isChecked():
			nCountCB+=1
		# check the situations of the GB
		if self.gbVarDensity.isChecked():
			nCount += 1
		if self.gbVarEdges.isChecked():
			nCount +=1
		if self.gbVarNodes.isChecked():
			nCount +=1
		# we cannot have more than one gb checked
		if nCount >= 2:
			self.gbVarDensity.setChecked(False)
			self.gbVarEdges.setChecked(False)
			self.gbVarNodes.setChecked(False)
			widget.setChecked(True)
		# update the checkBoxes
		# count
		if nCount == 0:
			while nCountCB < 2:
				wOldestUnchecked = self.lstUncheckEvolCB[0]
				self.lstCheckEvolCB.append(self.lstUncheckEvolCB.pop(0))
				wOldestUnchecked.setCheckState(QtCore.Qt.Checked)
				nCountCB +=1
			if nCountCB == 3:
				self.lstUncheckEvolCB.append(self.lstCheckEvolCB.pop(0))
				self.lstUncheckEvolCB[-1].setCheckState(QtCore.Qt.Unchecked)
				nCountCB -=1
		else:
			if nCountCB == 2:
				self.lstUncheckEvolCB.append(self.lstCheckEvolCB.pop(0))
				self.lstUncheckEvolCB[-1].setCheckState(QtCore.Qt.Unchecked)
			if nCountCB == 0:
				wOldestUnchecked = self.lstUncheckEvolCB[0]
				if wOldestUnchecked != widgetCB:
					self.lstCheckEvolCB.append(self.lstUncheckEvolCB.pop(0))
					wOldestUnchecked.setCheckState(QtCore.Qt.Checked)
				else:
					self.lstCheckEvolCB.append(self.lstUncheckEvolCB.pop(1))
					self.lstCheckEvolCB[-1].setCheckState(QtCore.Qt.Checked)

	#------------------#
	# Other parameters #
	#------------------#

	def setEvolParam(self):
		widget = self.sender()
		strWText = ""
		if widget in self.dicCBtoGBevol.keys():
			if widget.isChecked():
				self.dicCBtoGBevol[widget].setChecked(False)
			else:
				widget.setEnabled(False)
				self.dicCBtoGBevol[widget].setChecked(True)
		elif widget in self.dicCBtoGBevol.values():
			widgetCB = list(self.dicCBtoGBevol.keys())[list(self.dicCBtoGBevol.values()).index(widget)]
			if widget.isChecked():
				widgetCB.setCheckState(QtCore.Qt.Unchecked)
				widgetCB.setEnabled(False)
			else:
				widgetCB.setEnabled(True)
				widgetCB.setCheckState(QtCore.Qt.Checked)
		elif widget == self.checkBoxAvg:
			if widget.isChecked():
				self.sbAverage.setEnabled(True)
			else:
				self.sbAverage.setEnabled(False)
		else:
			if widget.isChecked():
				self.dicCBtoGBMeas[widget].setEnabled(True)
			else:
				self.dicCBtoGBMeas[widget].setEnabled(False)


	def setEnableFrame(self):
		self.gbGraphMeasAxis.setEnabled(self.gbGraphMeas.isChecked())

	'''def updateEvol(self):
		if self.tabWAnalysis.currentIndex() == 0:
			self.checkBoxSaveEvolGraphs.setEnabled(False)
			self.checkBoxSaveEvolGraphs.setVisible(False)
			self.lineSaveGraphs.setVisible(False)
		else:
			self.checkBoxSaveEvolGraphs.setEnabled(True)
			self.checkBoxSaveEvolGraphs.setVisible(True)
			self.lineSaveGraphs.setVisible(True)'''

	def updateGenVariables(self):
		widget = self.sender()
		if widget in self.gbGenSeries.children():
			associatedCB = self.dicGBtoCBgen[widget]
			associatedSB = self.dicGBtoSBgen[widget]
			if widget.isChecked():
				associatedCB.setCheckState(QtCore.Qt.Unchecked)
			else:
				associatedCB.setCheckState(QtCore.Qt.Checked)
		else:
			# get the associated gb
			associatedGB = list(self.dicGBtoCBgen.keys())[list(self.dicGBtoCBgen.values()).index(widget)]
			if widget.isChecked():
				associatedGB.setChecked(False)
			else:
				associatedGB.setChecked(True)

	def updateGenStaticValue(self):
		widget = self.sender()
		parent = widget.parent()
		sbAssociated = self.dicGBtoSBgen[parent]
		# get average between start and stop
		valAverage = 0
		for child in parent.children():
			if "Start" in child.objectName():
				valAverage += child.value()
			if "Stop" in child.objectName():
				valAverage += child.value()
		valAverage/=2
		# update the (double)spinBox
		sbAssociated.setValue(valAverage)

	def updateEvolStaticValue(self,groupBox):
		widget = self.sender()
		parent = widget.parent()
		sbAssociated = self.dicGBtoSBevol[parent]
		# get average between start and stop
		valAverage = 0
		for child in parent.children():
			if "Start" in child.objectName():
				valAverage += child.value()
			if "Stop" in child.objectName():
				valAverage += child.value()
		valAverage/=2
		# update the (double)spinBox
		sbAssociated.setValue(valAverage)

	#---------------#
	# Network types #
	#---------------#

	def setErdosType(self):
		# hide the unused widgets
		self.checkBoxInDegExp.setVisible(False)
		self.dsbInDegExp.setVisible(False)
		self.dsbOutDegExp.setVisible(False)
		self.checkBoxOutDegExp.setVisible(False)
		self.dsbRecip.setVisible(False)
		self.checkBoxReciprocity.setVisible(False)
		self.dsbLambda.setVisible(False)
		self.checkBoxLambda.setVisible(False)
		self.sbNeuronDens.setVisible(False)
		self.checkBoxNeurDens.setVisible(False)
		self.gbInDegExpSeries.setVisible(False)
		self.gbOutDegExpSeries.setVisible(False)
		self.gbRecipSeries.setVisible(False)
		self.gbLambdaSeries.setVisible(False)
		self.gbNeuronDensSeries.setVisible(False)

	def setErdosEvol(self):
		self.gbNeuronDens.setVisible(False)
		self.gbLambda.setVisible(False)
		self.gbInDegExp.setVisible(False)
		self.gbOutDegExp.setVisible(False)
		self.gbRecip.setVisible(False)
		self.checkBoxInDegExpEvol.setVisible(False)
		self.dsbInDegExpEvol.setVisible(False)
		self.dsbOutDegExpEvol.setVisible(False)
		self.checkBoxOutDegExpEvol.setVisible(False)
		self.checkBoxReciprocityEvol.setVisible(False)
		self.dsbRecipEvol.setVisible(False)
		self.checkBoxLambdaEvol.setVisible(False)
		self.dsbLambdaEvol.setVisible(False)
		self.checkBoxNeuronDensEvol.setVisible(False)
		self.sbNeuronDensEvol.setVisible(False)

	def setFreeScaleType(self):
		# hide the unused widgets
		self.dsbLambda.setVisible(False)
		self.sbNeuronDens.setVisible(False)
		self.checkBoxLambda.setVisible(False)
		self.checkBoxNeurDens.setVisible(False)
		self.checkBoxInDegExp.setVisible(True)
		self.dsbInDegExp.setVisible(True)
		self.dsbOutDegExp.setVisible(True)
		self.checkBoxOutDegExp.setVisible(True)
		self.dsbRecip.setVisible(True)
		self.checkBoxReciprocity.setVisible(True)
		self.gbInDegExpSeries.setVisible(True)
		self.gbOutDegExpSeries.setVisible(True)
		self.gbRecipSeries.setVisible(True)
		self.gbLambdaSeries.setVisible(False)
		self.gbNeuronDensSeries.setVisible(False)

	def setFreeScaleEvol(self):
		self.gbNeuronDens.setVisible(False)
		self.gbLambda.setVisible(False)
		self.gbInDegExp.setVisible(True)
		self.gbOutDegExp.setVisible(True)
		self.gbRecip.setVisible(True)
		self.checkBoxInDegExpEvol.setVisible(True)
		self.dsbInDegExpEvol.setVisible(True)
		self.dsbOutDegExpEvol.setVisible(True)
		self.checkBoxOutDegExpEvol.setVisible(True)
		self.checkBoxReciprocityEvol.setVisible(True)
		self.dsbRecipEvol.setVisible(True)
		self.checkBoxLambdaEvol.setVisible(False)
		self.dsbLambdaEvol.setVisible(False)
		self.checkBoxNeuronDensEvol.setVisible(False)
		self.sbNeuronDensEvol.setVisible(False)

	def setEDRType(self):
		# hide the unused widgets
		self.dsbInDegExp.setVisible(False)
		self.dsbOutDegExp.setVisible(False)
		self.checkBoxInDegExp.setVisible(False)
		self.checkBoxOutDegExp.setVisible(False)
		self.dsbRecip.setVisible(False)
		self.checkBoxReciprocity.setVisible(False)
		self.dsbLambda.setVisible(True)
		self.sbNeuronDens.setVisible(True)
		self.checkBoxLambda.setVisible(True)
		self.checkBoxNeurDens.setVisible(True)
		self.gbInDegExpSeries.setVisible(False)
		self.gbOutDegExpSeries.setVisible(False)
		self.gbRecipSeries.setVisible(False)
		self.gbLambdaSeries.setVisible(True)
		self.gbNeuronDensSeries.setVisible(True)

	def setEDREvol(self):
		self.gbNeuronDens.setVisible(True)
		self.gbLambda.setVisible(True)
		self.checkBoxLambdaEvol.setVisible(True)
		self.checkBoxNeuronDensEvol.setVisible(True)
		self.checkBoxLambdaEvol.setVisible(True)
		self.dsbLambdaEvol.setVisible(True)
		self.checkBoxNeuronDensEvol.setVisible(True)
		self.sbNeuronDensEvol.setVisible(True)
		self.gbInDegExp.setVisible(False)
		self.gbOutDegExp.setVisible(False)
		self.gbRecip.setVisible(False)
		self.checkBoxInDegExpEvol.setVisible(False)
		self.dsbInDegExpEvol.setVisible(False)
		self.dsbOutDegExpEvol.setVisible(False)
		self.checkBoxOutDegExpEvol.setVisible(False)
		self.checkBoxReciprocityEvol.setVisible(False)
		self.dsbRecipEvol.setVisible(False)

	def setGaussWeights(self):
		self.labelScaleExc.setVisible(False)
		self.labelScaleInhib.setVisible(False)
		self.labelLocationInhib.setVisible(False)
		self.labelLocationExc.setVisible(False)
		self.dsbScaleExcWeights.setVisible(False)
		self.dsbScaleInhibWeights.setVisible(False)
		self.dsbLocationInhibWeights.setVisible(False)
		self.dsbLocationExcWeights.setVisible(False)
		self.labelMeanExc.setVisible(True)
		self.labelMeanInhib.setVisible(True)
		self.labelVarInhib.setVisible(True)
		self.labelVarExc.setVisible(True)
		self.dsbVarExcWeights.setVisible(True)
		self.dsbVarInhibWeights.setVisible(True)
		self.dsbMeanInhibWeights.setVisible(True)
		self.dsbMeanExcWeights.setVisible(True)

	def setLogNormWeights(self):
		self.labelMeanExc.setVisible(False)
		self.labelMeanInhib.setVisible(False)
		self.labelVarInhib.setVisible(False)
		self.labelVarExc.setVisible(False)
		self.dsbVarExcWeights.setVisible(False)
		self.dsbVarInhibWeights.setVisible(False)
		self.dsbMeanInhibWeights.setVisible(False)
		self.dsbMeanExcWeights.setVisible(False)
		self.labelScaleExc.setVisible(True)
		self.labelScaleInhib.setVisible(True)
		self.labelLocationInhib.setVisible(True)
		self.labelLocationExc.setVisible(True)
		self.dsbScaleExcWeights.setVisible(True)
		self.dsbScaleInhibWeights.setVisible(True)
		self.dsbLocationInhibWeights.setVisible(True)
		self.dsbLocationExcWeights.setVisible(True)

	def updateSbNodesToKeep(self):
		if self.comboBoxSelectGraph.count() != 0:
			idxCurrent = self.comboBoxSelectGraph.currentIndex()
			nNodes = self.comboBoxSelectGraph.itemData(idxCurrent).getNodes()
			self.sbNodesToKeep.setMaximum(nNodes)

	def closeEvent(self,event):
		# empty self-referencing dictionaries
		self.dicGraphType = None
		self.dicEvolType = None
		self.dicWeightsType = None
		self.dicCBtoGBMeas = None
		self.dicCBtoVarGB = None
		self.dicGBtoCBevol = None
		self.dicGBtoCBgen = None
		self.dicGBtoSBgen = None
		self.dicGBtoSBgen = None
		self.dicGBtoSBevol = None

	def __del__(self):
		print("MainWindow died")
