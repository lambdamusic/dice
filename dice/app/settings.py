#!/usr/bin/python
# -*- coding: utf-8 -*-


import os

_dirnameTop = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 

OUTPUT_PATH_DEFAULT = os.path.join(os.path.expanduser("~"), "dice-exports")

STATIC_FILES_SOURCE = _dirnameTop + "/media/templates-bs4/static/"
