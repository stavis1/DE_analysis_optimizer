#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 15:58:24 2026

@author: chemod-u02
"""

import unittest
import testSuite_ancestor_objs
from copy import deepcopy
import numpy as np

class NormalizationTestSuite(testSuite_ancestor_objs.baseLipidomicsTestSuite, testSuite_ancestor_objs.baseDataProcessingStepTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['1_normalization']
        self.tearDown()
        self.check_prob_score = False
        self.check_significance = False
    
    def test_shift_correction(self):
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

class ProteinRollupTestSuite(testSuite_ancestor_objs.baseProteomicsTestSuite, testSuite_ancestor_objs.baseDataProcessingStepTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['2_protein_rollup']
        self.tearDown()

    def test_protein_rollup_sanity(self):        
        #get reference value
        max_N_prots = self.data.get_metadata().shape[0]
        
        #check each rollup strategy
        for step_option in self.step_options:
            #process data
            data = deepcopy(self.data)
            data = self.pipeline_steps[step_option].process(data)
            N_prots = data.get_data().shape[0]
            
            with self.subTest(f'Does {step_option} give a sane number of proteins?'):
                self.assertLessEqual(N_prots, max_N_prots)
            with self.subTest(f'Does {step_option} correctly label the analytes?'):
                self.assertTrue(all([a.startswith('protein') for a in data.get_df()['analyte']]))
            with self.subTest(f'Does {step_option} correctly drop the proteins column?:'):
                self.assertTrue('proteins' not in list(data.get_df().columns))

class ImputationTestSuite(testSuite_ancestor_objs.baseLipidomicsTestSuite, testSuite_ancestor_objs.baseDataProcessingStepTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['2_imputation']
        self.tearDown()
    
    def test_nan_reduction(self):
        #get reference value
        init_N_missing = np.sum(np.logical_not(np.isfinite(self.data.get_data())))
        
        for step_option in self.step_options:
            if step_option not in ['noop']:
                #process data
                data = deepcopy(self.data)
                data = self.pipeline_steps[step_option].process(data)
                N_missing = np.sum(np.logical_not(np.isfinite(data.get_data())))
                
                with self.subTest(f'Does {step_option} reduce the number of NANs?'):
                    self.assertLess(N_missing, init_N_missing)
                with self.subTest(f'Does {step_option} remove all NANs?'):
                    self.assertEqual(N_missing, 0)

class NHSTTestSuite(testSuite_ancestor_objs.baseLipidomicsTestSuite, testSuite_ancestor_objs.baseLinearShiftTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['3_statistical_test']
        self.tearDown()

    def test_additive_shift(self):        
        self.add_linear_shift()
        for step_option in self.step_options:
            if step_option not in ['noop']:
                #process data
                data = deepcopy(self.data)
                data = self.pipeline_steps[step_option].process(data)
                significant = data.get_score() < 0.05
                TP = np.nansum(np.logical_and(significant, self.truth))
                FP = np.nansum(np.logical_and(significant, np.logical_not(self.truth)))
                TN = np.nansum(np.logical_and(np.logical_not(significant), np.logical_not(self.truth)))
                FPR = FP/(FP+TN)
                FDR = FP/(FP+TP)
                
                with self.subTest(f'Does {step_option} handle NANs?'):
                    self.assertTrue(np.any(np.isfinite(significant)))
                with self.subTest(f'Does {step_option} have a low FDR?'):
                    self.assertLess(FDR, 0.1)
                with self.subTest(f'Does {step_option} have a low FPR?'):
                    self.assertLess(FPR, 0.1)

class MultiplicityCorrectionTestSuite(testSuite_ancestor_objs.baseLipidomicsTestSuite, testSuite_ancestor_objs.baseLinearShiftTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['4_multiplicity_correction']
        self.tearDown()

    def test_multiplicity_correction(self):
        self.add_linear_shift()
        #run a student's t-test on the data
        from DE_analysis_optimizer.pipeline_steps import StudentT
        self.data = StudentT().process(self.data)
        scores = self.data.get_score()
        
        for step_option in self.step_options:
            #process data
            data = deepcopy(self.data)
            data = self.pipeline_steps[step_option].process(data)
            significant = data.get_significance()
            score_ratio = np.nanmean(scores[significant])/np.nanmean(scores[np.logical_not(significant)])
            
            with self.subTest(f'Do {step_option} significance calls correlate with prob_scores?'):
                self.assertLess(score_ratio, 1)
            with self.subTest(f'Does {step_option} handle NANs?'):
                self.assertTrue(np.any(np.any(np.isfinite(significant))))

class EffectFilterTestSuite(testSuite_ancestor_objs.baseLipidomicsTestSuite, testSuite_ancestor_objs.baseLinearShiftTestSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setUp()
        self.step_options = self.options.step_options['5_effect_size_filter']
        self.tearDown()

    def test_effect_size_filter(self):
        self.add_linear_shift()
        sig_init = np.array([True, False]*(self.data.get_data().shape[0]//2))
        self.data.set_significance(sig_init)
        
        for step_option in self.step_options:
            if step_option not in ['noop']:
                #process data
                data = deepcopy(self.data)
                data = self.pipeline_steps[step_option].process(data)
                significant = data.get_significance()
                significant = significant[np.isfinite(significant)]
                
                with self.subTest(f'Does {step_option} handle NANs?'):
                    self.assertTrue(len(significant) > 0)

                with self.subTest(f'Does {step_option} remove small effect sizes?'):
                    subset = significant[np.logical_not(self.truth)]
                    self.assertTrue(np.all(np.logical_not(subset)))
                
                with self.subTest(f'Does {step_option} retain large effect sizes?'):
                    significant[np.logical_and(self.truth, sig_init)]
                    self.assertTrue(np.all(subset))
                
                with self.subTest(f'Does {step_option} respect negative significance calls?'):
                    significant[np.logical_and(self.truth, np.logical_not(sig_init))]
                    self.assertTrue(np.all(np.logical_not(subset)))
                                

if __name__ == '__main__':
    import make_test_data
    unittest.main()




    

