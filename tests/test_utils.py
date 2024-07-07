#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 17:33:28 2024

@author: anon
"""

import sys
from shutil import rmtree
import os
import unittest
import logging

from DE_analysis_optimizer.options import options, setup_workspace

class baseTestSuite(unittest.TestCase):
    def setUp(self):
        self.init_dir = os.getcwd()
        self.init_argv = sys.argv
        test_path = os.path.dirname(__name__)
        sys.argv = [sys.argv[0], '--options', os.path.join(test_path, 'test_options.toml')]
        self.args = options()
        logger = logging.getLogger('DE_analysis_optimizer')
        logger.setLevel(logging.FATAL)
        os.chdir(self.args.working_directory)
        pass
    
    def tearDown(self):
        os.chdir(self.init_dir)
        sys.argv = self.init_argv
        pass

