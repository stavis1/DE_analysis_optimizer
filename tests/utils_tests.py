#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:04:18 2025

@author: 4vt
"""

from shutil import rmtree
import os
import pandas as pd
import numpy as np

import testSuite_ancestor_objs
from DE_analysis_optimizer.utils import init_files, read_data, get_outcomes, get_attempts

class utilsTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def setUp(self):
        super().setUp()
        rmtree('attempted.tsv', ignore_errors=True)
        rmtree('test_output/outcomes.tsv', ignore_errors=True)
    
    def tearDown(self):
        super().tearDown()
        rmtree('attempted.tsv', ignore_errors=True)
        rmtree('test_output', ignore_errors=True)
    
    def test_file_initialization(self):
        init_files(self.options)
        
        expected_step_headers = ['1_protein_rollup',
                                 '2_normalization',
                                 '3_statistical_test',
                                 '4_multiplicity_correction',
                                 '5_effect_size_filter',
                                 '6_rules_based_filter']
        expected_outcome_headers = ['truth1_recall',
                                    'truth1_FDR',
                                    'truth2_recall',
                                    'truth2_FDR']
        with self.subTest('Check that attempted.tsv exists'):
            self.assertTrue(os.path.exists('attempted.tsv'))
        with self.subTest('Check that attempted.tsv has the right headers'):
            with open('attempted.tsv', 'r') as tsv:
                self.assertEqual(tsv.readline(), '\t'.join(expected_step_headers)+'\n')
        with self.subTest('Check that outcomes.tsv has the right headers'):
            with open('test_output/outcomes.tsv', 'r') as tsv:
                self.assertEqual(tsv.readline(), '\t'.join(expected_step_headers + expected_outcome_headers)+'\n')

    def test_data_reader_finds_data(self):
        data = read_data(self.options)
        self.assertIsNotNone(data.get_data())

    def test_outcomes_reader_finds_data(self):
        #set up workspace
        init_files(self.options)
        outcome_data = pd.read_csv('test_output/outcomes.tsv', sep = '\t')
        
        #read outcomes data
        outcome_data[outcome_data.columns] = np.full((3,outcome_data.shape[1]), np.nan)
        metric_cols = [c for c in outcome_data.columns if c.endswith('_recall') or c.endswith('_FDR')]
        param_cols = [c for c in outcome_data.columns if not c in metric_cols]

        #make fake outcomes data
        rng = np.random.default_rng(1)
        outcome_data[metric_cols] = rng.uniform(0,1,(3, len(metric_cols)))
        for col in param_cols:
            outcome_data[col] = [f'{col}{i}' for i in range(3)]
        outcome_data.to_csv('test_output/outcomes.tsv', sep = '\t', index = False)
        
        #run outcomes parser
        outcomes = get_outcomes(self.options)
        
        #run tests
        with self.subTest('Are the correct number of outcomes observed?'):
            self.assertEqual(len(outcomes), 3)
        with self.subTest('Are the metrics correctly parsed?'):
            for outcome, recall, FDR in zip(outcomes, outcome_data['truth1_recall'], outcome_data['truth1_FDR']):
                self.assertAlmostEqual(outcome.recall, recall, 8)
                self.assertAlmostEqual(outcome.FDR, FDR, 8)
    
    def test_attempts_reader_finds_data(self):
        #set up workspace
        init_files(self.options)
        attempt_data = pd.read_csv('attempted.tsv', sep = '\t')
        
        #read attempts data
        N = 4
        attempt_data[attempt_data.columns] = np.full((N,attempt_data.shape[1]), np.nan)

        #make fake attempt data
        for col in attempt_data.columns:
            attempt_data[col] = [f'{col}{i}' for i in range(N)]
        attempt_data.to_csv('attempted.tsv', sep = '\t', index = False)
        
        #run attempts parser
        attempts = get_attempts(self.options)
        
        #run tests
        self.assertEqual(len(attempts), N)
        
    
    def test_attempts_and_outcome_hashes_are_comparible(self):
        #set up workspace
        init_files(self.options)
        
        #read data
        N = 4
        attempt_data = pd.read_csv('attempted.tsv', sep = '\t')
        attempt_data[attempt_data.columns] = np.full((N - 1, attempt_data.shape[1]), np.nan)
        outcome_data = pd.read_csv('test_output/outcomes.tsv', sep = '\t')
        outcome_data[outcome_data.columns] = np.full((N, outcome_data.shape[1]), np.nan)
        metric_cols = [c for c in outcome_data.columns if c.endswith('_recall') or c.endswith('_FDR')]
        param_cols = [c for c in outcome_data.columns if not c in metric_cols]

        #make fake attempt data
        for col in attempt_data.columns:
            attempt_data[col] = [f'{col}{i}' for i in range(N - 1)]
        attempt_data.to_csv('attempted.tsv', sep = '\t', index = False)
        
        #make fake outcomes data
        rng = np.random.default_rng(1)
        outcome_data[metric_cols] = rng.uniform(0,1,(N, len(metric_cols)))
        for col in param_cols:
            outcome_data[col] = [f'{col}{i}' for i in range(N)]
        outcome_data.to_csv('test_output/outcomes.tsv', sep = '\t', index = False)
        
        #run parsers
        attempts = get_attempts(self.options)
        outcomes = get_outcomes(self.options)
        
        #run tests
        N_overlap = len([o for o in outcomes if o in attempts])
        self.assertEqual(N_overlap, N-1)





