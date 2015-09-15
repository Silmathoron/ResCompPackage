#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" GridSearcher class """


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

	#-----#
	# Run #
	#-----#

	def run(self):
		bContinue = self.xml_context()
		if bContinue:
			with open(self.args.path+"batch", "w") as fileBatchResult:
				bCrunchGraphs = True
				numRuns = 0
				#~ dicResults = {}
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
						# chat, run and wait for results
						xmlResults = self.get_results()
						if xmlResults is not None:
							# save and store previous results
							strResultName = previousResult[0]+ '_' + previousResult[1]
							dicResults[strResultName] = xmlHandler.save_xml_to_txt("{}{}.txt".format(previousResult[0], previousResult[1]), self.comm.results, previousResult[2])
							# save current reservoir and connectivity
							saveNeighbourList(dicPair["reservoir"], "results/matrices/")
							saveConnect(dicPair["connect"],"results/matrices/",strNameReservoir)
						previousResult = (strNameConnect, strNameReservoir, xmlParamList)
					else:
						strResultName = previousResult[0] + '_' + previousResult[1]
						dicResults[strResultName] = xmlHandler.save_xml_to_txt("{}{}.txt".format(previousResult[0], previousResult[1]), self.comm.results, previousResult[2])
						bCrunchGraphs = False
					numRuns += 1
				print("Run finished")
		
