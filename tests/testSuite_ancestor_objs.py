#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 17:33:28 2024

@author: anon
"""

import sys
import os
import unittest

from DE_analysis_optimizer.options import Options

class baseTestSuite(unittest.TestCase):
    def setUp(self):
        self.init_dir = os.getcwd()
        self.init_argv = sys.argv
        test_path = os.path.dirname(__name__)
        sys.argv = [sys.argv[0], '--options', os.path.join(test_path, 'test_options.toml')]
        self.options = Options()
        pass
    
    def tearDown(self):
        os.chdir(self.init_dir)
        sys.argv = self.init_argv
        pass

