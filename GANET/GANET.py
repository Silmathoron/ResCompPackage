#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main file of the "Cute pie" programm for network generation and analysis """


import sys
sys.path.append("gui")
sys.path.append("mainClasses")
sys.path.append("plottingTools")
sys.path.append("../netClasses/")
sys.path.append("../commonTools/")
import threading

from PySide import QtCore, QtGui
from PySide.QtGui import QApplication

from NetWindow import NetWindow
from GraphGenerator import GraphGenerator
from GraphAnalyzer import GraphAnalyzer
from FileManager import FileManager
from ReservoirComputing import ReservoirComputing
from GnuPlotter import GnuPlotter
from WeightsManager import WeightsManager

__version__ = '0.3'



#
#---
# Main class
#-----------------------

class GANET:

	def __init__(self):
		# listes des graphs et connectivités + fichier de batch reservoir/connectivité
		self.lstGraphs = []
		self.lstConnect = []
		self.batch = []
		# multiprocessing
		self.listWGraphs = []
		listWConnect = []
		self.lstProcessesGraphGen = []
		self.lstProcessesEvolProp = []
		self.bProcKilled = False

	def __enter__(self):
		self.gui = NetWindow(self)
		self.graphAnalyser = GraphAnalyzer(self) # GraphAnalysis qui servira à analyser les graphs
		self.graphGenerator = GraphGenerator(self) # GraphGenerator pour les créer
		self.gnuPlotter = GnuPlotter(self) # GnuPlotter pour les figures
		self.fileManager = FileManager(self) # FileManager pour loading/saving
		self.resComputer = ReservoirComputing(self) # créer et analyser des matrices de connectivités en lien avec les graphes pour leur utilisation en reservoir computing
		self.weightsManager = WeightsManager(self)
		return self

	def sendLoadConnectSignal(self):
			sender = self.sender()
			strType = None
			if sender.objectName() == "pbLoadInputConnect":
				strType = "input"
			elif sender.objectName() == "pbLoadReadoutConnect":
				strType = "readout"
			self.fileManager.loadConnect(strType)

	def connect_interface(self):
		if self.gui is not None:
			# les actions sur la création ou l'analyse de graphes/connectivités
			QtCore.QObject.connect(self.gui.pbCreateGraph, QtCore.SIGNAL("clicked()"), self.startProcessGraphGen)
			QtCore.QObject.connect(self.gui.pbCancelGraphGen, QtCore.SIGNAL("clicked()"), self.stopLastProcessGraphGen)
			QtCore.QObject.connect(self.gui.pbPlotDistrib, QtCore.SIGNAL("clicked()"), self.graphAnalyser.plotDistrib)
			QtCore.QObject.connect(self.gui.pbPlotEvol, QtCore.SIGNAL("clicked()"), self.graphAnalyser.plotEvolProp)
			self.gui.pbMeasurements.clicked.connect(self.graphAnalyser.showMeasurements)
			self.gui.pbPlotDegDistribConnect.clicked.connect(self.resComputer.plotConnectivityDegree)
			self.gui.pbPlotWeightDistribConnect.clicked.connect(self.resComputer.plotConnectivityWeightDistrib)
			self.gui.pbCompareDegree.clicked.connect(self.resComputer.compareDegrees)
			self.gui.pbCompDegBetw.clicked.connect(self.resComputer.compareDegBetw)
			self.gui.pbBatchAnalysis.clicked.connect(self.resComputer.analyseBatch)
			self.gui.pbGenerateConnect.clicked.connect(self.resComputer.makeConnectivities)
			# les save/load/remove
			self.gui.toolButtonSaveFile.clicked.connect(self.fileManager.setNeighbourListFile)
			self.gui.pbSave.clicked.connect(self.fileManager.saveNeighbourList)
			self.gui.pbLoad.clicked.connect(self.fileManager.loadGraph)
			self.gui.pbLoadInputConnect.clicked.connect(self.sendLoadConnectSignal)
			self.gui.pbLoadReadoutConnect.clicked.connect(self.sendLoadConnectSignal)
			self.gui.pbLoadBatch.clicked.connect(self.fileManager.loadBatch)
			self.gui.pbSaveConnect.clicked.connect(self.fileManager.saveConnect)
			self.gui.pbRemove.clicked.connect(self.fileManager.removeData)

	# add graph to the list widget, the comboboxes and activate the buttons
	def newGraphAdded(self, lstNewGraphs):
		for graph in lstNewGraphs:
			self.lstGraphs.append(graph)
			strGraphName = graph.get_name()
			if self.gui.comboBoxSaveNetw.findText(strGraphName) != -1:
				strGraphName += "_{}".format(len(self.lstGraphs))
				graph.setName(strGraphName)
			QtGui.QListWidgetItem(strGraphName,self.listWGraphs)
			idxItem = self.listWGraphs.count() - 1
			self.listWGraphs.item(idxItem).setText(unicode(strGraphName))
			self.listWGraphs.item(idxItem).setData(1,graph)
			self.gui.comboBoxSaveNetw.addItem(strGraphName,graph)
			self.gui.comboBoxSelectGraph.addItem(strGraphName,graph)
			self.gui.comboBoxReservoir.addItem(strGraphName,graph)
			self.gui.comboBoxConnectBaseReservoir.addItem(strGraphName,graph)
			self.gui.pbPlotDistrib.setEnabled(True)
			self.gui.pbSave.setEnabled(True)
			self.gui.pbGenerateConnect.setEnabled(True)
			if self.gui.comboBoxSelectConnect.count() != 0:
				self.gui.pbCompareDegree.setEnabled(True)
				self.gui.pbCompDegBetw.setEnabled(True)

	# add to the list widget, the combobox and activate the buttons
	def newConnectivityAdded(self):
		connectivity = self.lstConnect[-1]
		strConnectName = connectivity.get_name()
		QtGui.QListWidgetItem(strConnectName,self.listWConnect)
		idxItem = self.listWConnect.count() - 1
		self.listWConnect.item(idxItem).setText(unicode(strConnectName))
		self.listWConnect.item(idxItem).setData(1,connectivity)
		self.gui.comboBoxSelectConnect.addItem(strConnectName,connectivity)
		self.gui.pbPlotDegDistribConnect.setEnabled(True)
		self.gui.pbPlotWeightDistribConnect.setEnabled(True)
		self.gui.pbSaveConnect.setEnabled(True)
		if self.gui.comboBoxReservoir.count() != 0:
			self.gui.pbCompareDegree.setEnabled(True)
			self.gui.pbCompDegBetw.setEnabled(True)

	def initProgressBar(self):
		self.gui.progBarEvolProp.setRange(0, 100)
		self.gui.progBarEvolProp.setVisible(True)
		self.gui.progBarEvolProp.setValue(0.001)

	def startProcessGraphGen(self):
		# remove process that terminated
		lstToRemove = []
		for i,lstProc in enumerate(self.lstProcessesGraphGen):
			lstProcessToRemove = []
			for j,process in enumerate(lstProc):
				if not process.is_alive():
					lstProcessToRemove.append(j)
			for j in lstProcessToRemove[::-1]:
				self.lstProcessesGraphGen.pop(j)
			if not lstProc:
				lstToRemove.append(i)
		for i in lstToRemove[::-1]:
			self.lstProcessesGraphGen.pop(i)
		# start new one
		self.gui.pbCancelGraphGen.setEnabled(True)
		t = threading.Thread(target=self.graphGenerator.generateGraph, args=())
		t.start()

	def stopLastProcessGraphGen(self):
		if self.lstProcessesGraphGen:
			self.bProcKilled = True
			lstProc = self.lstProcessesGraphGen.pop()
			for proc in lstProc:
				proc.terminate()
			if not self.lstProcessesGraphGen:
				self.gui.pbCancelGraphGen.setEnabled(False)
		else:
			self.gui.pbCancelGraphGen.setEnabled(False)
		
	def threadEvolProp(self):
		None # later

	def __exit__(self, *args):
		# empty processes lists
		self.lstProcessesGraphGen = []
		self.gui.close()


#
#---
# Execute
#-----------------------

if __name__ == "__main__":
	app = QApplication(sys.argv)
	with GANET() as ganet:
		ganet.connect_interface()
		ganet.gui.show()
		#import pdb; pdb.set_trace()
		ret = app.exec_()
	#~ sys.exit(ret)
