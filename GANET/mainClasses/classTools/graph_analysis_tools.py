#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Graph analysis tools """

import numpy as np
from copy import deepcopy

from graph_measure import degree_list, betweenness_list


#
#---
# Initialize
#-------------------------

def checkPlots(parent, lstSubgraphTypes, strVarQuantity):
	""" check whether we have to plot:
	- the degree
	- the betweenness distribution """
	dicPlotFunc={} # les fonctions à appeler
	dicArgs={} # leurs arguments
	dicStrGp = { subgraphType: {} for subgraphType in lstSubgraphTypes}
	if parent.gui.gbBetweenness.isChecked():
		dicPlotFunc["Betweenness"] = gpBetwDistrib
		dicArgs["Betweenness"] = []
		if parent.gui.checkBoxBetwEdges.isChecked():
			dicArgs["Betweenness"].append("Edges")
		if parent.gui.checkBoxBetwNodes.isChecked():
			dicArgs["Betweenness"].append("Nodes")
		for subgraphType in lstSubgraphTypes:
			dicStrGp[subgraphType]["Betweenness"] = parent.gnuPlotter.genGpStrBetw(
													"evol_Betw{}_Var{}_{}".format(parent.gui.cbNetTypeEvol.currentText(),strVarQuantity,subgraphType),
													dicArgs["Betweenness"])
	if parent.gui.gbDegDistrib.isChecked():
		dicPlotFunc["Degree"] = plotDegDistrib
		dicArgs["Degree"]= []
		if parent.gui.checkBoxDegIn.isChecked():
			dicArgs["Degree"].append("in")
		if parent.gui.checkBoxDegOut.isChecked():
			dicArgs["Degree"].append("out")
		if parent.gui.checkBoxDegTot.isChecked():
			dicArgs["Degree"].append("total")
		for subgraphType in lstSubgraphTypes:
			dicStrGp[subgraphType]["Degree"], _ = parent.gnuPlotter.genGpStrDeg(
														"evol_Deg{}_Var{}_{}".format(parent.gui.cbNetTypeEvol.currentText(),strVarQuantity, subgraphType),
														dicArgs["Degree"])
	return dicPlotFunc, dicArgs, dicStrGp

def initDicAvg(dicPlotFunc,dicArgs,lstStrMeasurements):
	dicAvgValues = { strMeas: 0 for strMeas in lstStrMeasurements }
	dicAvgDistrib = {}
	for strPlot in dicPlotFunc.keys():
		if strPlot == "Degree":
			dicDegree = {}
			for degType in dicArgs["Degree"]:
				dicDegree[degType] = np.array([])
			dicAvgDistrib["Degree"] = dicDegree
		if strPlot == "Betweenness":
			dicBetweenness = {}
			for betwType in dicArgs["Betweenness"]:
				dicBetweenness[betwType] = np.array([])
			dicAvgDistrib["Betweenness"] = dicBetweenness
	return dicAvgValues, dicAvgDistrib
	
def initFiles(parent, lstSubgraphTypes, dicFileNames, strVarQuantity, lstStrMeasurements):
	if parent.gui.gbGraphMeas.isChecked():
		for subgraphType in lstSubgraphTypes:
			with open("data/" + dicFileNames[subgraphType],"w") as fileEvol:
				fileEvol.write(strVarQuantity)
				for strMeas in lstStrMeasurements:
					fileEvol.write("\t" + strMeas)
				fileEvol.write("\n")

#
#---
# Compute
#-------------------------

def getNetworkProperties(graph, subgraphType, dicNetAnalysis, dicPlotFunc, lstStrMeasurements, dicAvg, numAvg):
	# generate the appropriate subgraph
	subGraph = graph
	if subgraphType == "Exc":
		subGraph = graph.genExcSubgraph()
	if subgraphType == "Inhib":
		subGraph = graph.genInhibSubgraph()
	# make measure
	for strMeas in lstStrMeasurements:
		dicAvg[strMeas] += dicNetAnalysis[strMeas](subGraph.get_graph()) / float(numAvg)

def getNetworkDistrib(graph, subgraphType, dicGraphDistribs, dicLog, bWeights, idx, strName):
	# generate the appropriate subgraph
	subGraph = graph
	if subgraphType == "Exc":
		subGraph = graph.genExcSubgraph()
	if subgraphType == "Inhib":
		subGraph = graph.genInhibSubgraph()
	if "Degree" in dicGraphDistribs.keys():
		for degType, arr in dicGraphDistribs["Degree"].items():
			dicGraphDistribs["Degree"][degType] = np.hstack((arr, degree_list(subGraph.get_graph(), degType, bWeights)))
	if "Betweenness" in dicGraphDistribs.keys():
		arrNodeBetw, arrEdgeBetw = betweenness_list(subGraph.get_graph(), bWeights)
		if "Nodes" in dicGraphDistribs["Betweenness"].keys():
			dicGraphDistribs["Betweenness"]["Nodes"] = np.hstack((dicGraphDistribs["Betweenness"]["Nodes"], deepcopy(arrNodeBetw.a)))
		if "Edges" in dicGraphDistribs["Betweenness"].keys():
			dicGraphDistribs["Betweenness"]["Edges"] = np.hstack((dicGraphDistribs["Betweenness"]["Edges"], deepcopy(arrEdgeBetw.a)))

def computeDistributions(numNodes, dicLog, dicGraphAvgDistrib, numAvg):
	numBins = int(numNodes / 10)
	for subgraphType, dicDistribs in dicGraphAvgDistrib.items():
		if "Degree" in dicDistribs.keys():
			for degType, arr in dicDistribs["Degree"].items():
				bins = np.linspace(arr.min(), arr.max(), numBins)
				if dicLog["Degree"]:
					bins = np.logspace(np.log10(np.maximum(arr.min(),1)), np.log10(arr.max()), numBins)
				vecCounts,vecDeg = np.histogram(arr, bins)
				dicDistribs["Degree"][degType] = (vecCounts / float(numAvg), vecDeg[:-1])
		if "Betweenness" in dicDistribs.keys():
			for betwType in dicDistribs["Betweenness"].keys():
				arr = dicDistribs["Betweenness"][betwType]
				bins = np.linspace(arr.min(), arr.max(), numBins)
				if dicLog["Betweenness"]:
					bins = np.logspace(np.log10(np.maximum(arr.min(),10**-8)), np.log10(arr.max()), numBins)
				vecCounts,vecBetw = np.histogram(arr, bins)
				dicDistribs["Betweenness"][betwType] = (vecCounts / float(numAvg), vecBetw[:-1])


#
#---
# Results and gnuplot files
#-------------------------

def writeAveragedMeasurements(parent, strGraphName, varValue, dicStrGp, dicFileNames, dicGraphAvgValues, lstStrMeasurements, nNecessarySteps, idx, strAddInfo):
	for subgraphType, dicAvg in dicGraphAvgValues.items():
		with open("data/" + dicFileNames[subgraphType],"a") as fileEvol:
			fileEvol.write("{}".format(varValue))
			for strMeas in lstStrMeasurements:
				fileEvol.write("\t{}".format(dicAvg[strMeas]))
			fileEvol.write("\n")
			
def writeAveragedDistributions(parent, strGraphName, varValue, dicStrGp, dicFileNames, dicGraphAvgDistrib, nNecessarySteps, idx, strAddInfo):
	for subgraphType, dicDistribs in dicGraphAvgDistrib.items():
		for distribType, dicDistrib in dicDistribs.items():
			if distribType == "Betweenness":
				dicStrGp[subgraphType]["Betweenness"] += gpBetwDistrib(parent,strGraphName,dicDistrib,idx,strAddInfo)
				if idx != nNecessarySteps-1:
					dicStrGp[subgraphType]["Betweenness"] += ",\\\n"
			if distribType == "Degree":
				dicStrGp[subgraphType]["Degree"] += gpDegDistrib(parent,strGraphName,dicDistrib,idx,strAddInfo)
				if idx != nNecessarySteps-1:
					dicStrGp[subgraphType]["Degree"] += ",\\\n"

def gpBetwDistrib(parent,strGraphName,dicBetweenness,idx=0,strAddInfo=""):
	strGP = ""
	# for each type of betweenness
	for i,betwType in enumerate(dicBetweenness.keys()):
		strGP,strFileHistoName = parent.gnuPlotter.completeGpStrBetw(betwType,strGraphName,idx,i,strAddInfo)
		if betwType != dicBetweenness.keys()[-1]:
				strGP += ",\\\n"
		with open(strFileHistoName,"w") as fileHisto:
			strHisto = ""
			tplArr = dicBetweenness[betwType]
			for i,count in enumerate(tplArr[0]):
				if count != 0:
					strHisto += "{}\t{}\n".format(tplArr[1][i],count)
			fileHisto.write(strHisto)
	return strGP
	
def gpDegDistrib(parent,strGraphName,dicDegree,idx=0,strAddInfo=""):
	strGP = ""
	for i,strDegType in enumerate(dicDegree.keys()): #strDegType = "in", "out" ou "total"
		strGP,strFileHistoName = parent.gnuPlotter.completeGpStrDeg(strDegType,strGraphName,idx,i,strAddInfo)
		if strDegType != dicDegree.keys()[-1]:
			strGP += ",\\\n"
		with open(strFileHistoName, "w") as fileHisto:
			strHisto = ""
			tplArr = dicDegree[strDegType]
			for i, count in enumerate(tplArr[0]):
				if count != 0:
					strHisto += "{}\t{}\n".format(tplArr[1][i],count)
			fileHisto.write(strHisto)
	return strGP


#
#---
# Plotting
#-------------------------

def plotBetwVsWeight(parent, graph,lstBetw):
	if graph.isWeighted():
		lstWeights = graph.get_graph().edge_properties["weight"].a
		lstData = np.zeros((2,len(lstWeights)))
		lstData[0,:] = lstWeights
		lstData[1,:] = lstBetw.a
		strFileName = "betVsWeight_"+graph.get_name().replace(".","p")
		np.savetxt("data/" + strFileName, np.transpose(lstData), delimiter='\t', newline='\n', header='Weight\tBetweenness')
		# .gp file
		strGP,strStyle,strPts = parent.gnuPlotter.genGpStrBetwVsWeight(strFileName)
		strGP += "'data/{0}' with {1} ls 3 {2}".format(strFileName,strStyle,strPts)
		with open("data/betVsWeight.gp","w") as fileGP:
			fileGP.write(strGP)
		strSubprocess = "data/betVsWeight.gp"
		subprocess.call(["gnuplot", strSubprocess])

def plotBetwDistrib(parent,graph,lstArgs,bLog,bWeights,idx=0,strAddInfo=""):
	strGP = ""
	nNodes = graph.num_vertices()
	nEdges = graph.num_edges()
	# get the centralities
	lstNodeBetwPM,lstEdgeBetwPM = betweenness_list(graph.get_graph(),bWeights)
	dicLstBetw = {"Nodes": np.zeros(nNodes), "Edges": np.zeros(nEdges)}
	dicNumBins = {"Nodes": int(np.ceil(nNodes/50.0)),"Edges": int(np.ceil(nEdges/200.0))}
	dicHistoBetw = {"Nodes": [], "NBins": [], "Edges": [], "EBins": []}
	strGraphName = graph.get_name().replace('.', 'p')
	# get relevant informations for strGP
	for i,data in enumerate(lstArgs):
		if data == "Edges":
			dicLstBetw["Edges"] = lstEdgeBetwPM.a
		elif data == "Nodes":
			dicLstBetw["Nodes"] = lstNodeBetwPM.a
		strGPTMP,strFileHistoName = parent.gnuPlotter.completeGpStrBetw(data,strGraphName,idx,i,strAddInfo)
		strGP += strGPTMP
		if data != lstArgs[-1]:
				strGP += ",\\\n"
		with open(strFileHistoName,"w") as fileHisto:
			# write data into the file
			dicHistoBetw[data],dicHistoBetw[data[0] + "Bins"] = np.histogram(dicLstBetw[data],dicNumBins[data])
			if parent.gui.checkBoxLogBetwX.isChecked():
				rMax = np.log10(np.amax(dicHistoBetw[data[0] + "Bins"]))
				rMinTMP = np.amin(dicHistoBetw[data[0] + "Bins"])
				rMin = -8
				if rMinTMP != 0.0:
					rMin = np.log10(rMinTMP)
				lstBins = np.logspace(rMin,rMax,dicNumBins[data])
				dicHistoBetw[data],dicHistoBetw[data[0] + "Bins"] = np.histogram(dicLstBetw[data],lstBins)
			strHisto = ""
			for i,count in enumerate(dicHistoBetw[data]):
				if count != 0:
					strHisto += "{}\t{}\n".format(0.5*(dicHistoBetw[data[0]+"Bins"][i]+dicHistoBetw[data[0]+"Bins"][i+1]),dicHistoBetw[data][i])
			fileHisto.write(strHisto)
	return strGP, lstNodeBetwPM, lstEdgeBetwPM

def plotDegDistrib(parent,graph,lstArgs,bLogDeg,bWeights,idx=0,strAddInfo=""):
	strGP = ""
	# get relevant informations
	strGraphName = graph.get_name().replace('.', 'p')
	strFileName = "deg_{}".format(strGraphName)
	# on calcul les distributions demandées et on les ajoute dans le fichier .gp
	for i,strDegType in enumerate(lstArgs): #strDegType = "in", "out" ou "total"
		strGPTMP,strFileHistoName = parent.gnuPlotter.completeGpStrDeg(strFileName,strDegType,idx,i,strAddInfo)
		strGP += strGPTMP
		if strDegType != lstArgs[-1]:
			strGP += ",\\\n"
		vecCounts,vecDeg = degree_distrib(graph,strDegType,bLogDeg,bWeights)
		with open(strFileHistoName, "w") as fileHisto:
			for i in range(len(vecCounts)):
				if vecCounts[i] != 0:
					fileHisto.write("{}\t{}\n".format(vecDeg[i],vecCounts[i]))
	return strGP

def degree_distrib(graph, strDegType, bLogDeg=False, bWeights=True):
	lstDegrees = degree_list(graph.get_graph(),strDegType,bWeights)
	numBins = graph.num_vertices() / 15
	bins = np.linspace(lstDegrees.min(), lstDegrees.max(), numBins)
	if bLogDeg:
		bins = np.logspace(np.log10(np.maximum(lstDegrees.min(),1)), np.log10(lstDegrees.max()), numBins)
	vecCounts,vecDeg = np.histogram(lstDegrees, bins)
	return vecCounts,vecDeg[0:-1]

def weight_distribution(graph,bLogWeights=False):
	numBins = graph.num_edges() / 35
	arrWeights = graph.get_graph().edge_properties["weight"].a
	bins = np.linspace(arrWeights.min(), arrWeights.max(), numBins)
	if bLogWeights:
		bins = np.logspace(np.log10(np.maximum(arrWeights.min(),1)), np.log10(arrWeights.max()), numBins)
	vecCounts,vecWeight = np.histogram(arrWeights, bins)
	return vecCounts,vecWeight[:-1]
