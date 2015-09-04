#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Python batch to evaluate reservoirs through a Metropolis algorithm """

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
