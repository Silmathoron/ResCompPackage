#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Phase-Space eXplorer """


import sys
sys.path.append('searcherClasses/')
sys.path.append('../ioClasses/')
sys.path.append('../commonTools')
sys.path.append('../netClasses')
import argparse
import multiprocessing

from CommPSX import CommPSX

from Metropolis import Metropolis
from GridSearcher import GridSearcher

__version__ = '1.0'



#
#---
# Parser
#--------------------

## define
parser = argparse.ArgumentParser(description="GridSearch: parameter exploration for reservoir computing", usage='%(prog)s [options]')
parser.add_argument("-i", "--input", action="store", default='data/input.xml',
					help="Path to XML input file")
parser.add_argument("-p", "--path", action="store", default=PATH_RES_CONNECT,
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
	connectionExplorer.send([STATUS])
	bConnected = connectionExplorer.recv()

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
