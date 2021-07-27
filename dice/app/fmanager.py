#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import time
import shutil

from .settings import *



class FileManager(object):
    """Handle file-related operations and provide state for them.
    """

    def __init__(self, title="", output_path=OUTPUT_PATH_DEFAULT):
        """
        Init
        """
        super(FileManager, self).__init__()
        self.timestamp = time.strftime("%Y%m%d-%H%M%S") # uniquely identified a viz run
        self.timestamp_name = "dice-" + self.timestamp
        self.output_path = output_path + "/" + self.timestamp_name
        self.title = title or self.timestamp
        self.final_url = "" # set after build

    def setup(self, newdir=None):
        """Create main output folders"""
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        if newdir:
            _new = os.path.join(self.output_path, newdir)
            if not os.path.exists(_new):
                os.makedirs(_new)


    def save2File(self, contents, filename):
        """Save text contents to a file location"""
        self.setup()
        fullpath = os.path.join(self.output_path, filename)
        f = open(fullpath, 'w')
        f.write(contents)  # python will convert \n to os.linesep
        f.close()  # you can omit in most cases as the destructor will call it
        url = "file://" + fullpath
        return url

    def saveDslData(self, dslDataset, filename=""):
        self.setup()
        filename = filename or "dsl-data-" + self.timestamp + ".json"
        fullpath = os.path.join(self.output_path_cached_data, filename)
        dslDataset.save_json(filename=fullpath)
        url = "file://" + fullpath
        return url

    def copyDir(self, src,  subpath):
        """Copy directory  and all of its contents to a subpath in the output folder"""
        dst = self.output_path + "/" + subpath
        shutil.copytree(src, dst)






