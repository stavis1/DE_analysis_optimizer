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

class baseDataProcessingStepTestSuite(baseTestSuite):
    def test_nan_support(self):
        from copy import deepcopy
        import numpy as np
        
        for step_option in self.step_options:
            this_data = deepcopy(self.data)
            this_data = self.pipeline_steps[step_option].process(this_data)
            with self.subTest(f'Can {step_option} handle nan values?'):
                self.assertTrue(np.any(np.isfinite(this_data.get_data())))

class baseLinearShiftTestSuite(baseTestSuite):
    def add_linear_shift(self):
        import numpy as np
        #add a linear shift of 15X the mean to only the ground-truth significant values
        self.truth = self.data.get_truths()[:,0]
        means = np.nanmean(self.data.get_data(), axis = 1)
        shifts = self.truth * 15 * means
        A = self.data.get_A() + shifts[:,np.newaxis]
        self.data.set_A(A)

class baseLipidomicsTestSuite(baseTestSuite):
    def setUp(self):
        super().setUp()
        self.data = read_data(self.options)
        self.pipeline_steps = get_all_pipeline_steps()
    
class baseProteomicsTestSuite(baseTestSuite):
    def setUp(self):
        super().setUp()
        test_path = os.path.dirname(__name__)
        sys.argv = [sys.argv[0], '--options', os.path.join(test_path, 'test_proteomics_options.toml')]
        self.options = Options()
        self.data = read_data(self.options)
        self.pipeline_steps = get_all_pipeline_steps()



