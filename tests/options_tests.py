#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 12:07:49 2024

@author: 4vt
"""
import os
import sys
import unittest
from shutil import rmtree

from DE_analysis_optimizer.options import Options, InputError

class optionsTestSuite(unittest.TestCase):
    def setUp(self):
        self.argv_init = sys.argv
        self.wd_init = os.getcwd()
        sys.argv = [sys.argv[0], '--options', 'test_options.toml']
        self.options = Options()
    
    def tearDown(self):
        sys.argv = self.argv_init
        rmtree(self.options.output_directory)
        os.chdir(self.wd_init)
        
    def test_overwrite_protection(self):
        self.options.overwrite = False
        with self.assertRaises(FileExistsError):
            self.options.handle_working_directory()
    
    def test_input_validation(self):
        required = ['working_directory',
                    'output_directory',
                    'overwrite',
                    'log_file',
                    'log_level',
                    'cores']
        for attr in required:
            tmp = self.options.__dict__[attr]
            del self.options.__dict__[attr]
            with self.subTest(msg = f'Testing validation of {attr}'):
                with self.assertRaises(InputError):
                    self.options.validate_inputs()
            setattr(self.options, attr, tmp)
    
