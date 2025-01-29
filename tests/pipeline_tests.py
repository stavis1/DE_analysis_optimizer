#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:54:06 2025

@author: 4vt
"""
import numpy as np
import testSuite_ancestor_objs
from DE_analysis_optimizer.pipeline import Pipeline
from DE_analysis_optimizer.pipeline_steps import Noop, Step
from DE_analysis_optimizer.utils import read_data

class pipelineTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def test_attempt_line_works(self):
        self.options.step_options = dict(list(self.options.step_options.items())[:2])
        pipeline = Pipeline(self.options)
        class DummyStep(Step):
            def __init__(self):
                self.name = 'test'
        
        pipeline.add_step(Noop(), '1_protein_rollup')
        pipeline.add_step(DummyStep(), '2_normalization')
        attempt = pipeline.attempt_line()
        self.assertEqual(attempt, 'nooptest')
    
    def test_run_and_report_work(self):        
        self.options.step_options = dict(list(self.options.step_options.items())[:2])
        pipeline = Pipeline(self.options)
        class DummyStep(Step):
            def __init__(self):
                self.name = 'test'
            
            def process(self, data):
                super().process(data)
                scores = data.get_score()
                data.set_score([0]*len(scores))
                data.set_significance([False, True]*(len(scores)//2))
                return data
        
        pipeline.add_step(Noop(), '1_protein_rollup')
        pipeline.add_step(DummyStep(), '2_normalization')
        data = read_data(self.options)
        scores_init = data.get_score()
        significant_init = data.get_significance()
        pipeline.run(data)
        results = pipeline.report()
        
        with self.subTest('Did the scores change?'):
            self.assertNotEqual(np.sum(data.get_score()), np.sum(scores_init))
            self.assertNotEqual(np.sum(data.get_significance()), np.sum(significant_init))
        
        with self.subTest('Are the metrics roughly accurate?'):
            self.assertAlmostEqual(pipeline.results[0], 0.5)
            self.assertAlmostEqual(pipeline.results[1], 0.5)
        
        with self.subTest('Does the report line make sense?'):
            self.assertEqual(len(results), len(self.options.step_options.keys()) + (data.get_truths().shape[1]*2))
            self.assertEqual(results[0]+results[1], pipeline.attempt_line())


