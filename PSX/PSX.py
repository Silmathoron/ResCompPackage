#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Phase-Space eXplorer """


import sys
sys.path.append('searcherClasses/')
sys.path.append('../ioTools/')
sys.path.append('../commonTools')
sys.path.append('../netClasses')

from SocketComm import SocketComm

from Metropolis import Metropolis
from GridSearcher import GridSearcher

__version__ = '0.2'

PATH_RES_CONNECT = "data/"


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
parser.add_argument("-r", "--runtype", action="store", default="learning",
					help="Type of grid search: 'separation' (default) or 'learning'")
parser.add_argument("-x", "--exploration", action="store", default="metropolis",
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
	comm = SocketComm(lstSrvHost, args.timeout)
	bConnected = comm.open_socket()

	if bConnected:
		# initialize
		explorer = None
		if args.exploration == "gridsearch":
			explorer = GridSearcher(args, comm)
		else:
			explorer = Metropolis(args, comm)

		# launch run
		explorer.run()
