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
		self.tplParameterSet = self.xmlHandler.gen_grid_search_param()

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
				dicResults = {}
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
						xmlParam = self.send_parameters()
						sys.stdout.write("\rParameters sent\n")
						sys.stdout.flush()
						# run and wait for results
						xmlResults = self.xmlHandler.from_string(self.get_results())
						if xmlResults is not None:
							# save results
							strResultName = strNameConnect + "_" + strNameReservoir
							dicResults[strResultName] = self.xmlHandler.save_results("{}.txt".format(strResultName), xmlResults, xmlParam)
							# save current reservoir and connectivity
							#~ saveNeighbourList(dicPair["reservoir"], "results/matrices/")
							#~ saveConnect(dicPair["connect"],"results/matrices/",strNameReservoir)
						else:
							bCrunchGraphs = False
					numRuns += 1
				print("Run finished")
		
