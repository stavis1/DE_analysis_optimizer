#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 12:07:49 2024

@author: 4vt
"""

from shutil import rmtree

from DE_analysis_optimizer.options import InputError
import testSuite_ancestor_objs

class optionsTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def tearDown(self):
        rmtree(self.options.output_directory)
        super().tearDown()
        
    def test_overwrite_protection(self):
        self.options.overwrite = False
        with self.assertRaises(FileExistsError):
            self.options.handle_working_directory()
    
    def test_required_options_checking(self):
        required = ['working_directory',
                    'output_directory',
                    'overwrite',
                    'cores',
                    'data_file',
                    'step_options']
        for attr in required:
            tmp = self.options.__dict__[attr]
            del self.options.__dict__[attr]
            with self.subTest(msg = f'Testing validation of {attr}'):
                with self.assertRaises(InputError):
                    self.options.validate_inputs()
            setattr(self.options, attr, tmp)
    
    def test_data_file_existance_checking(self):
        rmtree('THIS_FILE_DOES_NOT_EXIST', ignore_errors = True)
        self.options.data_file = 'THIS_FILE_DOES_NOT_EXIST'
        with self.assertRaises(InputError):
            self.options.validate_inputs()

    def test_pipeline_step_specification_checking(self):
        self.options.step_options = {'1_bad_step':['NONEXISTANT_STEP_OPTION']}
        with self.assertRaises(InputError):
            self.options.validate_inputs()

