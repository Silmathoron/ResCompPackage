#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" GridSearcher class """


import sys

from PhaseSpaceExplorer import PhaseSpaceExplorer
from global_param import *



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
		self.lstParameterSet = self.xmlHandler.grid_search_param_list()

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
				previousResult = []
				dicResults = {}
				while bCrunchGraphs:
					print("--- Run %d ---" % numRuns)
					bRecvd = self.send_next_matrices()
					print("matrix received?",bRecvd)
					if bRecvd:
						# save information
						strNameReservoir, strNameConnect = self.current_names()
						fileBatchResult.write("{}{}.txt\n".format(strNameConnect,strNameReservoir))
						fileBatchResult.flush()
						# process them
						sys.stdout.write("\rSending...")
						sys.stdout.flush()
						bRecvd = self.send_parameters()
						sys.stdout.write("\rParameters sent\n")
						sys.stdout.flush()
						# run and wait for results
						xmlResults = self.xmlHandler.from_string(self.get_results())
						if xmlResults is not None:
							# save and store previous results
							if previousResult:
								strResultName = previousResult[0]+ '_' + previousResult[1]
								dicResults[strResultName] = xmlHandler.save_xml_to_txt("{}{}.txt".format(previousResult[0], previousResult[1]), self.comm.results, previousResult[2])
							# save current reservoir and connectivity
							saveNeighbourList(dicPair["reservoir"], "results/matrices/")
							saveConnect(dicPair["connect"],"results/matrices/",strNameReservoir)
						previousResult = (strNameConnect, strNameReservoir, xmlResults)
					else:
						strResultName = previousResult[0] + '_' + previousResult[1]
						dicResults[strResultName] = xmlHandler.save_xml_to_txt("{}{}.txt".format(previousResult[0], previousResult[1]), self.comm.results, previousResult[2])
						bCrunchGraphs = False
					numRuns += 1
				print("Run finished")
		
