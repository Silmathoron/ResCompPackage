#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Phase-Space eXplorer """


import argparse
import multiprocessing

from .global_param import *

from .searcherClasses import CommPSX, Metropolis, GridSearcher

__version__ = '1.0'



#
#---
# Parser
#--------------------

## define

parser = argparse.ArgumentParser(description="GridSearch: parameter exploration for reservoir computing", usage='%(prog)s [options]')
parser.add_argument("-i", "--input", action="store", default=IPATH,
					help="Path to XML input file")
parser.add_argument("-p", "--path", action="store", default=PATH,
					help="Path to saving/result folder")
parser.add_argument("-s", "--server", action="store", default="10.69.200.8:4242",
					help="Server adress and port")
parser.add_argument("-t", "--timeout", action="store", default=5000,
					help="Socket timeout")
parser.add_argument("-r", "--runtype", action="store", default="separation",
					help="Type of grid search: 'separation' (default) or 'learning'")
parser.add_argument("-x", "--exploration", action="store", default="gridsearch",
					help="Type phase space exploration ('gridsearch' or 'metropolis' -- default)")

## parse
args = parser.parse_args()



#
#---
# Searcher
#--------------

class Psx:

	def __init__(self, exploration=args.exploration, input_path=args.input,
				 run_type=args.runtype, path=args.path,
				 server=args.server, timeout=args.timeout):
		self.exploration = exploration
		self.args = args
		self.args.timeout = timeout
		self.args.server = server
		self.args.path = path
		self.args.runtype = run_type
		self.args.input = input_path
		# connect to server
		lstSrvHost = args.server.split(':')
		self.comm = CommPSX(lstSrvHost, args.timeout)
		# set connection and deploy communicator
		self.connectionExplorer, connectionComm = multiprocessing.Pipe()
		self.comm.connectionClient = connectionComm
		self.comm.deploy()
		# check success
		self.connectionExplorer.send((STATUS,))
		self.bConnected = self.connectionExplorer.recv()

	def run(self):
		if self.bConnected:
			print("initiating")
			# initialize
			explorer = None
			if self.exploration == "gridsearch":
				explorer = GridSearcher(self.args, self.connectionExplorer)
			else:
				explorer = Metropolis(self.args, self.connectionExplorer)
			# launch run
			explorer.run()


#
#---
# Main
#--------------

if __name__ == "__main__":
	# connect to server
	lstSrvHost = args.server.split(':')
	comm = CommPSX(lstSrvHost, args.timeout)
	# set connection and deploy communicator
	connectionExplorer, connectionComm = multiprocessing.Pipe()
	comm.connectionClient = connectionComm
	comm.deploy()
	# check success
	connectionExplorer.send((STATUS,))
	bConnected = connectionExplorer.recv()
	print("explorer connected")

	if bConnected:
		print("initiating")
		# initialize
		explorer = None
		if args.exploration == "gridsearch":
			explorer = GridSearcher(args, connectionExplorer)
		else:
			explorer = Metropolis(args, connectionExplorer)
		# launch run
		explorer.run()
