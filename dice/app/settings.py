#!/usr/bin/python
# -*- coding: utf-8 -*-


import os

_dirnameTop = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 

OUTPUT_PATH_DEFAULT = os.path.join(os.path.expanduser("~"), "dice-exports")

STATIC_FILES_SOURCE = _dirnameTop + "/media/templates-bs4/static/"



#
# CONCEPTS DEFAULTS
#

MIN_CONCEPTS_SCORE_DEFAULT = 0.6
MIN_CONCEPTS_FREQ_DEFAULT = 3 


#
# NETWORK DEFAULTS
#

MAX_NETWORK_NODES_DEFAULT = 250
MAX_NETWORK_EDGES_DEFAULT = 350
