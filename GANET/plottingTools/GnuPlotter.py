#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Gnuplotter for NetGen """


class GnuPlotter:
	def __init__(self, parent):
		self.parent = parent

	def genGpStrBetw(self,strFileName,lstArgs):
		# run all the tests to complete the .gp
		strData1 = lstArgs[0]
		strMirror = ""
		strYLog = ""
		strYAdd0 = "add ('0' 0)"
		if self.parent.gui.checkBoxLogBetwY.isChecked():
			strYLog = "set logscale y\n"
			strYAdd0 = ""
		strTerm = "epslatex color dashed\n"
		strOutput = "tex"
		strFormatX = ""
		strPtSize= "1.5"
		strOffset = "offset 0,1 "
		if self.parent.gui.rbPlotPDF.isChecked():
			strTerm = "pdf transparent enhanced dashed font 'FreeSerif'\n"
			strOutput = "pdf"
			strPtSize = "0.5"
			strOffset = ""
		strXLog = ""
		strXAdd0 = "add ('0' 0) "
		if self.parent.gui.checkBoxLogBetwX.isChecked():
			strXLog = "set logscale x\n"
			strXAdd0 = ""
			strFormatX = '$%2.1t \\cdot 10^{%L}$'
			if self.parent.gui.rbPlotPDF.isChecked():
				strFormatX = "\"%2.1t {/Symbol \\327}10^{%L}\""
		strData2 = ""
		if len(lstArgs) == 2:
			strMirror = "nomirror "
			strY2Log = ""
			strY2Add0 = "add ('0' 0)"
			if self.parent.gui.checkBoxLogBetwY.isChecked():
				strY2Log = "set logscale y2\n"
				strY2Add0 = ""
			strX2Log = ""
			strX2Add0 = "add ('0' 0) "
			if self.parent.gui.checkBoxLogBetwX.isChecked():
				strX2Log = "set logscale x2\n"
				strX2Add0 = ""
			strData2 ="\n\
set y2label rotate '{0}'\n\
{1}\
set y2tics nomirror {2}\n\
set x2label \"{0}' betweenness\"\n\
{3}\
set x2tics nomirror {4}offset -0.5,0 rotate by 30\n\
set format x2 {5}\n\
set my2tics 5\n\
set mx2tics 5\n".format(lstArgs[1],strY2Log,strY2Add0,strX2Log,strX2Add0,strFormatX)
		strKey = "off"
		if self.parent.gui.gbSetLegendDistrib.isChecked():
			strKey ="{} {}".format(self.parent.gui.cbLegendHorizAlign.currentText(),self.parent.gui.cbLegendVertAlign.currentText())
		# generate the GP file
		strGP = "load 'plottingTools/SpectrPerso.plt'\n\
set grid linestyle 18 lc rgb '#cccccc'\n\
\n\
set ylabel rotate '{0}'\n\
{1}\
set ytics {2}{3}\n\
set mytics 5\n\
set xlabel {4}\"{0}' betweenness\"\n\
{5}\
set xtics {2}{6}offset -0.5,0 rotate by -30\n\
set format x {7}\n\
set mxtics 5\n\
{8}\
\n\
set key {9}\n\
set term {10}\n\
set output 'data/graphs/{11}.{12}'\n\
set pointsize {13}\n\
\n\
plot ".format(strData1,strYLog,strMirror,strYAdd0,strOffset,strXLog,strXAdd0,strFormatX,strData2,strKey,strTerm,strFileName,strOutput,strPtSize)
		return strGP

	def completeGpStrBetw(self,strBetwType,strGraphName,idxIter=0,idxCurrent=0,strAddInfo=""):
		strStyle = ""
		strPts = ""
		if self.parent.gui.rbPoints.isChecked():
			strStyle = "points"
			strPts = "pt 7 "
		if self.parent.gui.rbLines.isChecked():
			strStyle = "lines"
		if self.parent.gui.rbLinespoints.isChecked():
			strStyle = "linespoints"
			strPts = "pt 7 "
		if strBetwType == "Nodes":
			if strPts != "":
				strPts = "pt 6 "
		strFileHistoName = "data/betw{0}_{1}{2}".format(strBetwType[0],strGraphName,strAddInfo)
		strGP = "'{0}' using 1:2 axes x{1}y{1} with {2} ls {3} {4}title \"{5}' betw.{6}\"".format(strFileHistoName,idxCurrent+1,strStyle,idxIter+1,strPts,strBetwType," - " + strAddInfo)
		return strGP,strFileHistoName

	def genGpStrEvolMeas(self,strFileName,strVarQuantity,lstStrMeasurements):
		# get the required informations
		lstLabelsY1 = []
		lstLabelsY2 = []
		lstLogscale = []
		if self.parent.gui.gbAssort.isEnabled():
			if self.parent.gui.rbAssortY1.isChecked():
				lstLabelsY1.append(self.parent.gui.gbAssort.title())
			else:
				lstLabelsY2.append(self.parent.gui.gbAssort.title())
			if self.parent.gui.checkBoxLogAssort.isChecked():
				lstLogscale.append(self.parent.gui.gbAssort.title())
		if self.parent.gui.gbClustering.isEnabled():
			if self.parent.gui.rbClusteringY1.isChecked():
				lstLabelsY1.append(self.parent.gui.gbClustering.title())
			else:
				lstLabelsY2.append(self.parent.gui.gbClustering.title())
			if self.parent.gui.checkBoxLogCluster.isChecked():
				lstLogscale.append(self.parent.gui.gbClustering.title())
		if self.parent.gui.gbReciprocity.isEnabled():
			if self.parent.gui.rbRecipY1.isChecked():
				lstLabelsY1.append(self.parent.gui.gbReciprocity.title())
			else:
				lstLabelsY2.append(self.parent.gui.gbReciprocity.title())
			if self.parent.gui.checkBoxLogRecip.isChecked():
				lstLogscale.append(self.parent.gui.gbReciprocity.title())
		if self.parent.gui.gbConnectComp.isEnabled():
			if self.parent.gui.rbConnectY1.isChecked():
				lstLabelsY1.append(self.parent.gui.gbConnectComp.title())
			else:
				lstLabelsY2.append(self.parent.gui.gbConnectComp.title())
			if self.parent.gui.checkBoxLogCC.isChecked():
				lstLogscale.append(self.parent.gui.gbConnectComp.title())
		if self.parent.gui.gbDiameter.isEnabled():
			if self.parent.gui.rbDiamY1.isChecked():
				lstLabelsY1.append(self.parent.gui.gbDiameter.title())
			else:
				lstLabelsY2.append(self.parent.gui.gbDiameter.title())
			if self.parent.gui.checkBoxLogDiam.isChecked():
				lstLogscale.append(self.parent.gui.gbDiameter.title())
		if self.parent.gui.gbSpectrum.isEnabled():
			if self.parent.gui.rbSpectrY1.isChecked():
				lstLabelsY1.append(self.parent.gui.gbSpectrum.title())
			else:
				lstLabelsY2.append(self.parent.gui.gbSpectrum.title())
			if self.parent.gui.checkBoxLogSpectr.isChecked():
				lstLogscale.append(self.parent.gui.gbSpectrum.title())
		# s'il y a des logscale, on les plot tous sur Y2
		bLogScale = False
		for strLabel in lstLogscale:
			bLogScale = True
			try:
				idx = lstLabelsY1.index(strLabel)
				del lstLabelsY1[idx]
			except ValueError:
				idx = lstLabelsY2.index(strLabel)
				del lstLabelsY2[idx]
		# on crée les labels Y1 et Y2
		strLabelY1 = ""
		strLabelY2 = ""
		if bLogScale:
			lstLabelsY1.extend(lstLabelsY2)
			lstLabelsY2 = lstLogscale
		for strLabel in lstLabelsY1:
			strLabelY1 += strLabel
			if strLabel != lstLabelsY1[-1]:
				strLabelY1 += ", "
		for strLabel in lstLabelsY2:
			strLabelY2 += strLabel
			if strLabel != lstLabelsY2[-1]:
				strLabelY2 += ", "
		# set the data for the axes
		strYMirror = ""
		strAxisY2 = ""
		if strLabelY2 != "":
			strYMirror = "nomirror "
			strY2Log = ""
			if bLogScale:
				strY2Log = "set logscale y2\n"
			strAxisY2 = "set y2label rotate '{0}'\n\
{1}\
set y2tics nomirror\n\
set my2tics 5\n\
set mx2tics 5\n".format(strLabelY2,strY2Log)
		# output type and legend
		strTerm = "epslatex color dashed\n"
		strOutput = "tex"
		strFormatX = "'$%2.1t \\cdot 10^{%L}$'"
		strPtSize= "1.5"
		strOffset = "offset 0,1 "
		if self.parent.gui.rbPlotPDF.isChecked():
			strTerm = "pdf transparent enhanced dashed font 'FreeSerif'\n"
			strOutput = "pdf"
			strFormatX = "\"%2.1t {/Symbol \\327}10^{%L}\""
			strPtSize = "0.5"
			strOffset = ""
		strKey = "off"
		if self.parent.gui.gbSetLegendDistrib.isChecked():
			strKey ="{} {}".format(self.parent.gui.cbLegendHorizAlign.currentText(),self.parent.gui.cbLegendVertAlign.currentText())
		# create the .gp file
		strGP = "load 'plottingTools/Set1.plt'\n\
set ylabel rotate '{0}'\n\
set xlabel {1}'{2}'\n\
set ytics {3}\n\
set mytics 5\n\
set mxtics 5\n\
{4}\
\n\
set key {5}\n\
set term {6}\
set grid linestyle 18 lc rgb '#cccccc'\n\
set output 'data/graphs/{7}.{8}'\n\
set pointsize {9}\n\
plot  ".format(strLabelY1,strOffset,strVarQuantity,strYMirror,strAxisY2,strKey,strTerm,strFileName,strOutput,strPtSize)
		return strGP,lstLabelsY2
		
	def completeGpStrEvol(self,strFile,lstLabelsY2,col,strMeas):
		strStyle = ""
		strPts = ""
		if self.parent.gui.rbPoints.isChecked():
			strStyle = "points"
			strPts = "pt {}".format(2*col+5)
		if self.parent.gui.rbLines.isChecked():
			strStyle = "lines"
		if self.parent.gui.rbLinespoints.isChecked():
			strStyle = "linespoints"
			strPts = "pt {}".format(2*col+5)
		nNumY = 1
		if strMeas in lstLabelsY2:
			nNumY = 2
		strGP = "'data/{0}' using 1:{1} axes x1y{2} with {3} ls {4} {5}title '{6}'".format(strFile,col+2,nNumY,strStyle,col+2,strPts,strMeas)
		return strGP

	def genGpStrDeg(self,strFileName,lstArgs):
		# get the required informations
		strYLog = ""
		if self.parent.gui.checkBoxLogDegY.isChecked():
			strYLog = "set logscale y\n"
		strXLog = ""
		bLogDeg = False
		if self.parent.gui.checkBoxLogDegX.isChecked():
			strXLog = "set logscale x\n"
			bLogDeg = True
		strTerm = "epslatex color dashed\n"
		strOutput = "tex"
		strFormatX = "'$%2.1t \\cdot 10^{%L}$'"
		strPtSize= "1.5"
		strOffset = "offset 0,1 "
		if self.parent.gui.rbPlotPDF.isChecked():
			strTerm = "pdf transparent enhanced dashed font 'FreeSerif'\n"
			strOutput = "pdf"
			strFormatX = "\"%2.1t {/Symbol \\327}10^{%L}\""
			strPtSize = "0.5"
			strOffset = ""
		strKey = "off"
		if self.parent.gui.gbSetLegendDistrib.isChecked():
			strKey ="{} {}".format(self.parent.gui.cbLegendHorizAlign.currentText(),self.parent.gui.cbLegendVertAlign.currentText())
		# build the .gp file
		strGP = "load 'plottingTools/SpectrPerso.plt'\n\
set ylabel rotate 'Nodes'\n\
set xlabel {7}'Degree'\n\
set mytics 5\n\
set mxtics 5\n\
set grid linestyle 18 lc rgb '#cccccc'\n\
{0}\
{1}\
\n\
set key {2}\n\
set term {3}\
set output 'data/graphs/{4}.{5}'\n\
set pointsize {6}\n\
plot ".format(strYLog,strXLog,strKey,strTerm,strFileName,strOutput,strPtSize,strOffset)
		return strGP, bLogDeg
	
	def completeGpStrDeg(self,strDegType,strFileName,idxIter=0,idxCurrent=0,strAddInfo=""):
		strStyle = ""
		strPts = ""
		if self.parent.gui.rbPoints.isChecked():
			strStyle = "points"
		if self.parent.gui.rbLines.isChecked():
			strStyle = "lines"
		if self.parent.gui.rbLinespoints.isChecked():
			strStyle = "linespoints"
		if self.parent.gui.rbPoints.isChecked():
				strPts = "pt {} ".format(7-idxCurrent)
		if self.parent.gui.rbLinespoints.isChecked():
			strPts = "pt {} ".format(7-idxCurrent)
		strFileHistoName = "data/{0}_{1}_{2}".format(strFileName,strAddInfo,strDegType)
		strGP = "'{0}' using 1:2 with {1} ls {2} {3}title '{4}{5}'".format(strFileHistoName,strStyle,idxIter+idxCurrent+1,strPts,strDegType," - " + strAddInfo)
		return strGP,strFileHistoName
	
	def genGpStrBetwVsWeight(self,strFileName):
		strYLog = ""
		strXLog = ""
		if self.parent.gui.checkBoxLogY.isChecked():
			strYLog = "set logscale y\n"
		if self.parent.gui.checkBoxLogX.isChecked():
			strXLog = "set logscale x\n"
		strTerm = "epslatex color dashed\n"
		strOutput = "tex"
		strFormatX = ""
		strPtSize= "1.5"
		strOffset = "offset 0,1 "
		if self.parent.gui.rbPlotPDF.isChecked():
			strTerm = "pdf transparent enhanced dashed font 'FreeSerif'\n"
			strOutput = "pdf"
			strPtSize = "0.5"
			strOffset = ""
		strPts = ""
		if self.parent.gui.rbPoints.isChecked():
			strStyle = "points"
			strPts = "pt 7"
		if self.parent.gui.rbLines.isChecked():
			strStyle = "lines"
		if self.parent.gui.rbLinespoints.isChecked():
			strStyle = "linespoints"
			strPts = "pt 7"
			strGP = "load 'plottingTools/Set1.plt'\n\
set grid linestyle 18 lc rgb '#cccccc'\n\
\n\
set ylabel rotate 'Betweenness'\n\
{0}\
set ytics\n\
set mytics 5\n\
set xlabel {1}'Weight'\n\
{2}\
set xtics\n\
set mxtics 5\n\
\n\
set key off\n\
set term {3}\n\
set output 'data/graphs/{4}.{5}'\n\
set pointsize {6}\n\
\n\
plot ".format(strYLog,strOffset,strXLog,strTerm,strFileName,strOutput,strPtSize)
		return strGP,strStyle,strPts

	def __del__(self):
		print("GnuPlotter died")
