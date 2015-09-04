#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Plotting widget for reservoir/connectivity analysis """

from PySide import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


#
#---
# Plotting widget
#-----------------------

class PlotWidget(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.scroll = QtGui.QScrollArea()
		self.scroll.setWidgetResizable(True)
		self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.scrollWidget = QtGui.QWidget(self.scroll)
		self.scrollLayout = QtGui.QVBoxLayout(self.scrollWidget)
		self.pbReset = QtGui.QPushButton("Reset")
		self.scrollLayout.addWidget(self.pbReset)
		spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
		self.scrollLayout.addSpacerItem(spacerItem)
		self.scrollWidget.setLayout(self.scrollLayout)
		self.scroll.setWidget(self.scrollWidget)
		self.layout = QtGui.QVBoxLayout()
		self.layout.addWidget(self.scroll)
		self.setLayout(self.layout)
		self.resize(850,780)
		self.numGraphs = 0
		QtCore.QObject.connect(self, QtCore.SIGNAL('triggered()'), self.reset)
		self.pbReset.clicked.connect(self.reset)
	
	#----------------#
	# plots and data #
	#----------------#
	
	def addPlotView(self,strTitle,plotWidget):
		qLabel = QtGui.QLabel(strTitle)
		self.scrollLayout.insertWidget(1,plotWidget)
		self.scrollLayout.insertWidget(1,qLabel)

	def createPlotView(self,dicPlots): # lstData = [2d array, strXaxis, strYaxis]
		plotWidget = pg.GraphicsLayoutWidget()
		plotWidget.setMinimumWidth(750)
		plotWidget.setMaximumHeight(400)
		for strPlotName,lstData in dicPlots.items():
			plot = plotWidget.addPlot(title=strPlotName)
			plot.setMaximumHeight(370)
			plot.plot(np.transpose(lstData[0]),pen=None,symbol=3)
			plot.setLabel('bottom',lstData[2])
			plot.setLabel('left',lstData[1])
		self.numGraphs +=1
		self.updateScrollArea()
		return plotWidget

	def addData(self,strTitle,dicData):
		gbData = QtGui.QGroupBox()
		gbData.setTitle(strTitle)
		gridLayout = QtGui.QGridLayout()
		numData = len(dicData.keys())
		numLeftRows = int(numData/2) +1
		i = 1
		for datatype, value in dicData.items():
			labelDatatype = QtGui.QLabel(datatype)
			dsbValue = QtGui.QDoubleSpinBox()
			dsbValue.setMaximum(10000)
			dsbValue.setDecimals(4)
			dsbValue.setValue(value)
			dsbValue.setReadOnly(True)
			if i <= numLeftRows:
				gridLayout.addWidget(labelDatatype,i,1,1,1)
				gridLayout.addWidget(dsbValue,i,2,1,1)
			else:
				gridLayout.addWidget(labelDatatype,i-numLeftRows,3,1,1)
				gridLayout.addWidget(dsbValue,i-numLeftRows,4,1,1)
			i+=1
		gbData.setLayout(gridLayout)
		self.scrollLayout.insertWidget(1,gbData)

	#
	########
	# reset

	def updateScrollArea(self):
		nHeight = self.numGraphs * 420 + 50
		self.scrollWidget.setMinimumSize(800, nHeight)

	def reset(self):
		while self.scrollLayout.count() > 2:
			child = self.scrollLayout.takeAt(1)
			child.widget().deleteLater()
		self.numGraphs = 0
		self.updateScrollArea()
