#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Python batch to evaluate reservoirs by doing a systematic grid search in parameter space """

import sys
import argparse
import threading



#
#---
# Default parameters
#-----------------------

CURRENT_DIR = sys.path[0] + '/'
DIR_RESULTS = "results/"
FILE_XML_CONTEXT = "data/paramSeparation.xml"


#
#---
# Parser
#--------------------

## define
parser = argparse.ArgumentParser(description="GridSearch: parameter exploration for reservoir computing", usage='%(prog)s [options]')
parser.add_argument("-d", "--destination", action="store", default=CURRENT_DIR+DIR_RESULTS,
					help="Path to results folder")
parser.add_argument("-s", "--server", action="store", default="10.69.200.8:4242",
					help="Server adress and port")
parser.add_argument("-r", "--runtype", action="store", default="separation",
					help="Type of grid search: 'separation' (default) or 'learning'")
parser.add_argument("-n", "--networks", action="store", default=CURRENT_DIR+"data/networks.xml",
					help="Path to networks information file")
parser.add_argument("-c", "--context", action="store", default=CURRENT_DIR+FILE_XML_CONTEXT,
					help="Path to networks information file")

## parse
args = parser.parse_args()
if args.runtype == "learning" and args.context == (CURRENT_DIR+FILE_XML_CONTEXT):
	args.context = CURRENT_DIR+"data/paramLearning.xml"

try:
	os.makedirs(CURRENT_DIR+DIR_RESULTS)
except OSError:
	if not os.path.isdir(CURRENT_DIR+DIR_RESULTS):
		raise


#
#---
# Main loop
#--------------------

if __name__ == "__main__":

	#--------------------------------#
	# Init objects and communication #
	#--------------------------------#

	gridSearcher = GridSearcher(args)
	bContinue = gridSearcher.xml_context()
	
	## loop
	
	if bContinue:
		print("Context sent", bContinue)
		with open(args.destination+"batch", "w") as fileBatchResult:
			''' work starting from here '''
			bCrunchGraphs = True
			numRuns = 0
			#~ xmlSelecLearning = xmlHandler.initXmlLearning() # look at that later
			#~ dicResults = {}
			while bCrunchGraphs:
				#~ bNewRow = False
				#~ xmlParamList = None
				print("--- Run %d ---" % numRuns)
				#~ dicPair = netGenerator.nextPair()
				bRecvd = gridSearcher.send_next()
				if bRecvd:
					# save information
					strNameReservoir, strNameConnect = gridSearcher.current_names()
					fileBatchResult.write("{}{}.txt\n".format(strNameConnect,strNameReservoir))
					fileBatchResult.flush()
					# process them
					sys.stdout.write("\rSending...")
					sys.stdout.flush()
					gridSearcher.send_parameters()
					sys.stdout.write("\rParameters sent\n")
					sys.stdout.flush()
					# chat, run and wait for results
					bRecv = True
					while bRecv:
						bRecv, strStep = comm.receive()
						if strStep == "Running" and comm.results is not None:
							# save and store previous results
							strResultName = previousResult[0]+ '_' +previousResult[1]
							dicResults[strResultName] = xmlHandler.saveXmlToTxt("{}{}.txt".format(previousResult[0], previousResult[1]), comm.results, previousResult[2])
							# save current reservoir and connectivity
							saveNeighbourList(dicPair["reservoir"], "results/matrices/")
							saveConnect(dicPair["connect"],"results/matrices/",strNameReservoir)
					previousResult = (strNameConnect, strNameReservoir, xmlParamList)
					# average the results every nAvg
					if len(dicResults) == xmlHandler.nAvg:
						xmlHandler.addParam(dicResults.keys()[0], xmlSelecLearning)
						t = threading.Thread(target=averageResults, args = ("results/avg", dicResults, xmlSelecLearning, 300, 25, xmlHandler.nAvg))
						t.start()
						bNewRow = True
					xmlHandler.addItems(bNewRow, strNameReservoir, strNameConnect, xmlSelecLearning)
				else:
					strResultName = previousResult[0] + '_' + previousResult[1]
					dicResults[strResultName] = xmlHandler.saveXmlToTxt("{}{}.txt".format(previousResult[0], previousResult[1]), comm.results, previousResult[2])
					xmlHandler.addParam(dicResults.keys()[0], xmlSelecLearning)
					averageResults("results/avg", dicResults, xmlSelecLearning, 300, 25, xmlHandler.nAvg)
					dicResults = {}
					with open("results/selecLearning.xml", "w") as fileXmlLearning:
						strXml = xmlHandler.tostring(xmlSelecLearning)
						fileXmlLearning.write(strXml)
					bCrunchGraphs = False
				numRuns += 1
			print("Run finished")
