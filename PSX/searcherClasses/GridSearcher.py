#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" GridSearcher class """


import sys

from PhaseSpaceExplorer import PhaseSpaceExplorer
from ..global_param import *



#
#---
# GridSearcher
#-----------------------

class GridSearcher(PhaseSpaceExplorer):
	
	#------#
	# Init #
	#------#

	def __init__(self, args, connection):
		super(GridSearcher, self).__init__(args, connection)
		self.init_parameters()

	def init_parameters(self):
		self.lstParameterSet = self.xmlHandler.gen_grid_search_param()

	def send_parameters(self):
		''' send the parameters to the server '''
		strNameReservoir, strNameConnect = self.current_names()
		xmlParamList = self.xmlHandler.gen_xml_param(strNameConnect,strNameReservoir,self.lstParameterSet)
		rMaxProgress = float(len(xmlParamList)-1)
		strParam = self.xmlHandler.to_string(xmlParamList)
		self.connectionComm.send((PARAM, strParam, rMaxProgress))
		bReceived = self.connectionComm.recv()

	#-----#
	# Run #
	#-----#

	def run(self):
		bContinue = self.send_xml_context()
		if bContinue:
			print("run started")
			with open(self.args.path+"batch", "w") as fileBatchResult:
				bCrunchGraphs = True
				numRuns = 0
				dicSaving = {}
				while bCrunchGraphs:
					print("--- Run %d ---" % numRuns)
					bRecvd = self.send_next_matrices()
					if bRecvd:
						# save information
						strNameReservoir, strNameConnect = self.current_names()
						fileBatchResult.write("{}{}.txt\n".format(strNameConnect,strNameReservoir))
						fileBatchResult.flush()
						# process them
						sys.stdout.write("\rSending...")
						sys.stdout.flush()
						self.send_parameters()
						sys.stdout.write("\rParameters sent\n")
						sys.stdout.flush()
						# run and wait for results
						dicResults = self.get_results(self.lstParameterSet)
						# save results
						strResultName = strNameConnect + "_" + strNameReservoir
						dicSaving[strResultName] = self.xmlHandler.save_results("{}.txt".format(strResultName), dicResults)
						# save current reservoir and connectivity
						#~ saveNeighbourList(dicPair["reservoir"], "results/matrices/")
						#~ saveConnect(dicPair["connect"],"results/matrices/",strNameReservoir)
					else:
						bCrunchGraphs = False
					numRuns += 1
				print("Run finished")
		
