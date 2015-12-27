#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Main file of the "Cute pie" programm for network generation and analysis """


import sys
import threading

from .gui import NetWindow
from .mainClasses import (GraphGenerator, GraphAnalyzer, FileManager,
						  ReservoirComputing, WeightsManager, GnuPlotter)

__version__ = '0.3'



#
#---
# Main class
#-----------------------

class Ganet:

	def __init__(self, gui=True):
		# listes des graphs et connectivités + fichier de batch reservoir/connectivité
		self.lstGraphs = []
		self.lstConnect = []
		self.batch = []
		# multiprocessing
		self.lstProcessesGraphGen = []
		self.lstProcessesEvolProp = []
		self.bProcKilled = False
		# main attributes
		if gui:
			from PySide import QtGui
			from .gui import NetWindow
			# start qapp
			app = QtGui.QApplication(sys.argv)
			self.gui = NetWindow(self) if gui else None
		self.graphAnalyser = GraphAnalyzer(self) # GraphAnalysis qui servira à analyser les graphs
		self.graphGenerator = GraphGenerator(self) # GraphGenerator pour les créer
		self.gnuPlotter = GnuPlotter(self) # GnuPlotter pour les figures
		self.fileManager = FileManager(self) # FileManager pour loading/saving
		self.resComputer = ReservoirComputing(self) # créer et analyser des matrices de connectivités en lien avec les graphes pour leur utilisation en reservoir computing
		self.weightsManager = WeightsManager(self)
		if gui:
			self.connect_interface()
			# show
			self.gui.show()
			ret = app.exec_()

	def signal_load_connect(self):
		sender = self.sender()
		strType = None
		if sender.objectName() == "pbLoadInputConnect":
			strType = "input"
		elif sender.objectName() == "pbLoadReadoutConnect":
			strType = "readout"
		self.fileManager.loadConnect(strType)

	def connect_interface(self):
		# les actions sur la création ou l'analyse de graphes/connectivités
		self.gui.pbCreateGraph.clicked.connect(self.start_graphgen_process)
		self.gui.pbCancelGraphGen.clicked.connect(self.stop_graphgen_last_process)
		self.gui.pbPlotDistrib.clicked.connect(self.graphAnalyser.plotDistrib)
		self.gui.pbPlotEvol.clicked.connect(self.graphAnalyser.plotEvolProp)
		self.gui.pbMeasurements.clicked.connect(self.graphAnalyser.show_measurements)
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
		self.gui.pbLoadInputConnect.clicked.connect(self.signal_load_connect)
		self.gui.pbLoadReadoutConnect.clicked.connect(self.signal_load_connect)
		self.gui.pbLoadBatch.clicked.connect(self.fileManager.loadBatch)
		self.gui.pbSaveConnect.clicked.connect(self.fileManager.saveConnect)
		self.gui.pbRemove.clicked.connect(self.fileManager.removeData)

	# add graph to the list widget, the comboboxes and activate the buttons
	def new_graph_added(self, lstNewGraphs):
		for graph in lstNewGraphs:
			self.lstGraphs.append(graph)
			strGraphName = graph.get_name()
			if self.gui.comboBoxSaveNetw.findText(strGraphName) != -1:
				strGraphName += "_{}".format(len(self.lstGraphs))
				graph.set_name(strGraphName)
			QtGui.QListWidgetItem(strGraphName,self.gui.listWGraphs)
			idxItem = self.gui.listWGraphs.count() - 1
			self.gui.listWGraphs.item(idxItem).setText(unicode(strGraphName))
			self.gui.listWGraphs.item(idxItem).setData(1,graph)
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
	def new_connectivity_added(self):
		connectivity = self.lstConnect[-1]
		strConnectName = connectivity.get_name()
		QtGui.QListWidgetItem(strConnectName,selfgui.listWConnect)
		idxItem = selfgui.listWConnect.count() - 1
		selfgui.listWConnect.item(idxItem).setText(unicode(strConnectName))
		selfgui.listWConnect.item(idxItem).setData(1,connectivity)
		self.gui.comboBoxSelectConnect.addItem(strConnectName,connectivity)
		self.gui.pbPlotDegDistribConnect.setEnabled(True)
		self.gui.pbPlotWeightDistribConnect.setEnabled(True)
		self.gui.pbSaveConnect.setEnabled(True)
		if self.gui.comboBoxReservoir.count() != 0:
			self.gui.pbCompareDegree.setEnabled(True)
			self.gui.pbCompDegBetw.setEnabled(True)

	def start_graphgen_process(self):
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
		t = threading.Thread(target=self.graphGenerator.generate_graph, args=())
		t.start()

	def stop_graphgen_last_process(self):
		if self.lstProcessesGraphGen:
			self.bProcKilled = True
			lstProc = self.lstProcessesGraphGen.pop()
			for proc in lstProc:
				proc.terminate()
			if not self.lstProcessesGraphGen:
				self.gui.pbCancelGraphGen.setEnabled(False)
		else:
			self.gui.pbCancelGraphGen.setEnabled(False)
		
	def thread_evol_prop(self):
		None # later

	def __exit__(self, *args):
		# empty processes lists
		self.lstProcessesGraphGen = []
		self.gui.close()

def main():
	app = QtGui.QApplication(sys.argv)
	with GANET() as ganet:
		ganet.connect_interface()
		ganet.gui.show()
		#import pdb; pdb.set_trace()
		ret = app.exec_()

#
#---
# Execute
#-----------------------

if __name__ == "__main__":
	main()
