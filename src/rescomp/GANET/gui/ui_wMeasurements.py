# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wMeasurements.ui'
#
# Created: Wed Apr 29 15:27:47 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_wMeasurements(object):
    def setupUi(self, wMeasurements):
        wMeasurements.setObjectName("wMeasurements")
        wMeasurements.resize(641, 472)
        self.gridLayout = QtGui.QGridLayout(wMeasurements)
        self.gridLayout.setObjectName("gridLayout")
        self.dsbAssort = QtGui.QDoubleSpinBox(wMeasurements)
        self.dsbAssort.setReadOnly(True)
        self.dsbAssort.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.dsbAssort.setDecimals(4)
        self.dsbAssort.setMaximum(1.0)
        self.dsbAssort.setObjectName("dsbAssort")
        self.gridLayout.addWidget(self.dsbAssort, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(wMeasurements)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.dsbRecip = QtGui.QDoubleSpinBox(wMeasurements)
        self.dsbRecip.setReadOnly(True)
        self.dsbRecip.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.dsbRecip.setDecimals(4)
        self.dsbRecip.setMaximum(1.0)
        self.dsbRecip.setObjectName("dsbRecip")
        self.gridLayout.addWidget(self.dsbRecip, 3, 1, 1, 1)
        self.dsbDiam = QtGui.QSpinBox(wMeasurements)
        self.dsbDiam.setReadOnly(True)
        self.dsbDiam.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.dsbDiam.setObjectName("dsbDiam")
        self.gridLayout.addWidget(self.dsbDiam, 5, 1, 1, 1)
        self.label_5 = QtGui.QLabel(wMeasurements)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.label = QtGui.QLabel(wMeasurements)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtGui.QLabel(wMeasurements)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.dsbCluster = QtGui.QDoubleSpinBox(wMeasurements)
        self.dsbCluster.setReadOnly(True)
        self.dsbCluster.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.dsbCluster.setDecimals(4)
        self.dsbCluster.setMaximum(1.0)
        self.dsbCluster.setObjectName("dsbCluster")
        self.gridLayout.addWidget(self.dsbCluster, 2, 1, 1, 1)
        self.graphicsViewSpectrum = QtGui.QGraphicsView(wMeasurements)
        self.graphicsViewSpectrum.setObjectName("graphicsViewSpectrum")
        self.gridLayout.addWidget(self.graphicsViewSpectrum, 7, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 1)
        self.dsbConnect = QtGui.QSpinBox(wMeasurements)
        self.dsbConnect.setReadOnly(True)
        self.dsbConnect.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.dsbConnect.setObjectName("dsbConnect")
        self.gridLayout.addWidget(self.dsbConnect, 4, 1, 1, 1)
        self.label_4 = QtGui.QLabel(wMeasurements)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.label_6 = QtGui.QLabel(wMeasurements)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)

        self.retranslateUi(wMeasurements)
        QtCore.QMetaObject.connectSlotsByName(wMeasurements)

    def retranslateUi(self, wMeasurements):
        wMeasurements.setWindowTitle(QtGui.QApplication.translate("wMeasurements", "NetGen - Measurements", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("wMeasurements", "Reciprocity:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("wMeasurements", "Diameter:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("wMeasurements", "Assortativity:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("wMeasurements", "Clustering:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("wMeasurements", "Connected components:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("wMeasurements", "Spectrum:", None, QtGui.QApplication.UnicodeUTF8))

