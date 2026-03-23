#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 15:58:24 2026

@author: chemod-u02
"""

import unittest
import testSuite_ancestor_objs


class NormalizationTestSuite(testSuite_ancestor_objs.baseLipidomicsTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['1_normalization']
        self.tearDown()
    
    def test_shift_correction(self):
        from copy import deepcopy
        import numpy as np
        
        A = self.data.get_A()
        A *= 1.2
        self.data.set_A(A)
        init_mean_diff = np.nanmean(self.data.get_A()) - np.nanmean(self.data.get_B())
        
        for step_option in self.step_options:
            if step_option not in ['noop']:
                data = deepcopy(self.data)
                data = self.pipeline_steps[step_option].process(data)
                mean_diff = np.nanmean(data.get_A()) - np.nanmean(data.get_B())
            
                with self.subTest(f'Can {step_option} remove a multiplicative shift?'):
                    self.assertLess(mean_diff, init_mean_diff)

class ProteinRollupTestSuite(testSuite_ancestor_objs.baseProteomicsTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['2_protein_rollup']
        self.tearDown()

if __name__ == '__main__':
    import make_test_data
    unittest.main()




    

