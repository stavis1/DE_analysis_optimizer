#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:54:06 2025

@author: 4vt
"""
import unittest
import numpy as np
import testSuite_ancestor_objs
from DE_analysis_optimizer.pipeline import Pipeline
from DE_analysis_optimizer.pipeline_steps import Noop, Step
from DE_analysis_optimizer.utils import read_data

class pipelineTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def test_attempt_line_works(self):
        pipeline = Pipeline(self.options)
        class DummyStep(Step):
            def __init__(self):
                self.name = 'test'
        
        pipeline.add_step(DummyStep(), '1_normalization')
        for step in self.options.step_order[1:]:
            pipeline.add_step(Noop(), step)
        attempt = pipeline.attempt_line()
        self.assertEqual(attempt, ''.join(['test']+['noop']*(len(self.options.step_order)-1)))
    
    def test_run_and_report_work(self):        
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
        
        pipeline.add_step(DummyStep(), '1_normalization')
        for step in self.options.step_order[1:]:
            pipeline.add_step(Noop(), step)
        data = read_data(self.options)
        scores_init = data.get_score()
        significant_init = data.get_significance()
        pipeline.run(data)
        results = pipeline.report().report()
        
        with self.subTest('Did the scores change?'):
            self.assertNotEqual(np.sum(data.get_score()), np.sum(scores_init))
            self.assertNotEqual(np.sum(data.get_significance()), np.sum(significant_init))
        
        with self.subTest('Are the metrics roughly accurate?'):
            self.assertAlmostEqual(pipeline.results[0], 0.5)
            self.assertAlmostEqual(pipeline.results[1], 0.5)
        
        with self.subTest('Does the report line make sense?'):
            self.assertEqual(len(results), len(self.options.step_options.keys()) + (data.get_truths().shape[1]*2))
            self.assertEqual(''.join(results[:len(self.options.step_order)]), pipeline.attempt_line())


if __name__ == '__main__':
    import make_test_data
    unittest.main()