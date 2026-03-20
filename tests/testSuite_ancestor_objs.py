#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 17:33:28 2024

@author: anon
"""

import sys
import os
import unittest
from shutil import rmtree

from DE_analysis_optimizer.options import Options
from DE_analysis_optimizer.utils import read_data
from DE_analysis_optimizer.utils import get_all_pipeline_steps


class baseTestSuite(unittest.TestCase):
    def delete(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            else:
                rmtree(path, ignore_errors=True)
        
    def setUp(self):
        self.init_dir = os.getcwd()
        self.init_argv = sys.argv
        test_path = os.path.dirname(__name__)
        sys.argv = [sys.argv[0], '--options', os.path.join(test_path, 'test_options.toml')]
        self.options = Options()
        pass
    
    def tearDown(self):
        self.delete(self.options.output_directory)
        os.chdir(self.init_dir)
        sys.argv = self.init_argv
        pass

class baseLipidomicsTestSuite(baseTestSuite):
    def setUp(self):
        super().setUp()
        self.data = read_data(self.options)
        self.pipeline_steps = get_all_pipeline_steps()

class baseProteomisTestSuite(baseTestSuite):
    def setUp(self):
        super().setUp()
        test_path = os.path.dirname(__name__)
        sys.argv = [sys.argv[0], '--options', os.path.join(test_path, 'test_proteomics_options.toml')]
        self.options = Options()
        self.data = read_data(self.options)
        self.pipeline_steps = get_all_pipeline_steps()



