#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" GridSearcher class """


from NetGen import NetGen
from XmlHandler import XmlHandler

from network_io import mat_to_string



#
#---
# GridSearcher
#-----------------------

class GridSearcher:
	
	#------#
	# Init #
	#------#

	def __init__(self, args, comm):
		self.comm = comm
		# process input file
		self.args = args
		self.xmlHandler = XmlHandler()
		self.xmlHandler.process_input(args.input)
		self.numAvg = self.xmlHandler.get_header_item("averages")
		if self.args.path[-1] != "/": self.args.path += "/"
		# create children
		self.netGenerator = NetGen(args.path, self.xmlHandler)
		#~ self.resultsAverager = Averager(args.destination, args.runtype, self.xmlHandler)

	#------------#
	# Processing #
	#------------#

	## setting context

	def xml_context(self):
		bContinue = self.comm.open_socket()
		strContext = self.xmlHandler.get_string_context()
		bContinue = False if strContext is None else True
		bContinue *= self.comm.send_context(strContext)
		return bContinue

	## generate and send next reservoir/connectivity pair
	
	def send_next_matrices(self):
		self.reservoir, self.connect = self.netGenerator.next_pair()
		if reservoir is not None:
			return self.send_matrices()
		else:
			return False

	## generate and send parameters

	def send_parameters(self):
		# generate list
		lstParam = self.xmlHandler.grid_search_param_list()
		# generate xml object
		strNameReservoir, strNameConnect = self.current_names()
		xmlParamList = self.xmlHandler.gen_xml_param(strNameConnect,strNameReservoir, lstParam)
		# send
		self.comm.send_parameters(xmlParamList)

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
						bRecv = True
						while bRecv:
							bRecv, strStep = self.comm.receive()
							if strStep == "Running" and self.comm.results is not None:
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

	#----------------#
	# Tool functions #
	#----------------#
	
	def send_matrices(self):
		strReservoir = mat_to_string(self.reservoir.get_mat_adjacency(), self.reservoir.get_name())
		strConnect = mat_to_string(self.connect.as_csr(), self.connect.get_name())
		bPairReceived = self.comm.send_data(strReservoir)
		bPairReceived *= self.comm.send_data(strConnect)
		return bPairReceived

	def current_names(self):
		return self.reservoir.get_name(), self.connect.get_name()
		
