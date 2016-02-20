#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Global parameters for PSX """

import os

# communication
CONTEXT = "CONTEXT"
STATUS = "STATUS"
RUNNING = "RUNNING"
PARAM = "PARAM"
MAT_CLIENT = "MATRIX"
SCENAR_CLIENT = "SCENARIO"
RUN = "RUN\r\n"

DATA = "data"
SIZE= "size"
ID = "id"
MAXPROG = "max_progress"
COMMAND = "client_command"
C_P = "command_param"
C_S = "command_scenario"
C_M = "command_matrix"


# files and paths
IPATH = os.path.dirname(os.path.realpath(__file__)) + '/data/'
INPUT = 'input.xml'
PATH = os.getcwd() + "/"
MATRIX_SUBPATH = "results/matrices/"
