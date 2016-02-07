#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Grid search test """

import os
import sys
path = os.getcwd()
path = path[:path.rfind("/")+1] + "src"
sys.path.insert(0, path)

from rescomp.PSX import Psx
from rescomp.plotting import phase_space



#~ test = Psx(exploration='metropolis')
test = Psx(exploration='gridsearch')
test.run()

dicResult = test.results
#~ phase_space(dicResult.values()[0], cols_var=[0,1,2], heatmap=True)
phase_space(dicResult.values()[0], cols_var=[0,1,2])
#~ phase_space(dicResult.values()[0], cols_var=[0,1,2], col_size=-2)
