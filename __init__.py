"""
ResCompPackage
==============

Package for reservoir computing with complex graphs.

"""

import sys
import os
sys.path.insert(0,os.getcwd())


#-----------------------------------------------------------------------------#
# Requirements
#------------------------
#

# Python > 2.6
assert sys.hexversion > 0x02060000

# graph library
try:
    import graph_tool
except:
    raise ImportError(
            "This module needs `graph_tool` to work.")


#-----------------------------------------------------------------------------#
# Modules
#------------------------
#

from .netClasses import GraphClass, InputConnect
from .GANET import Ganet
from .PSX import Psx
import GANET
import PSX

version = 0.4

__all__ = [ "GraphClass", "InputConnect", "Psx", "Ganet", "version" ]
