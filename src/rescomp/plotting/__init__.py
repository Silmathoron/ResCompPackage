#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Content
=======

"""

import matplotlib
matplotlib.use('GTK3Agg')
import warnings
warnings.filterwarnings("ignore", module="matplotlib")

# module import

from .custom_plt import palette
from .plot import *

