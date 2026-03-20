#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 12:18:53 2026

@author: chemod-u02
"""
import unittest
from unittest.mock import patch
from multiprocessing import Pool, set_start_method
import time

import testSuite_ancestor_objs
from DE_analysis_optimizer.pipeline_steps import Noop, Step
from DE_analysis_optimizer.workers import run_optimization_worker
from DE_analysis_optimizer.utils import read_data, init_data_manager

class workersTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def test_run_optimization_worker(self):
        #make a dummy step that produces random significance calls
        #this will result in random quality metrics for the outcomes
        rng = self.options.rng
        class DummyStep(Step):
            def __init__(self):
                self.name = 'test'
            
            def process(self, data):
                super().process(data)
                scores = data.get_score()
                data.set_score([0]*len(scores))
                data.set_significance(rng.choice([True, False], len(scores)))
                return data
        
        #make three versions of dummy steps and noops so that the pipelines can be 'different' so mutate() doesn't hang
        dummies = [DummyStep() for _ in range(3)]
        for i,d in enumerate(dummies):
            d.name = f'dummy_{i}'
        
        noops = [Noop() for _ in range(3)]
        for i,n in enumerate(noops):
            n.name = f'noop_{i}'
        
        #fill in the step options with these duplicated steps
        for step in self.options.step_order[:-1]:
            self.options.step_options[step] = [f'noop_{i}' for i in range(3)]
        self.options.step_options[self.options.step_order[-1]] = [f'dummy_{i}' for i in range(3)]
        
        #make mock all_pipeline_steps dict
        class MockUtils:
            def __init__(self):
                self.all_pipeline_steps = {s.name:s for s_list in (dummies, noops) for s in s_list}
                
            def get_all_pipeline_steps(self):
                return self.all_pipeline_steps
        
        global worker_wrapper
        def worker_wrapper(*args):
            #temporarily replace DE_analysis_optimizer.utils with the MockUtils object
            with patch.dict('sys.modules', {'DE_analysis_optimizer.utils':MockUtils()}):
                run_optimization_worker(*args)
        
        # =============================================================================
        # __main__.py
        # =============================================================================
        #parse data
        initial_data = read_data(self.options)
        
        self.options.cores = 2
        with Pool(self.options.cores) as p:
            #initialize the manager process for attempts and outcomes data
            pipes = init_data_manager(self.options, p)
            
            #construct jobs
            n_workers = len(pipes)
            jobs = zip([self.options]*n_workers, [initial_data]*n_workers, pipes)

            #run worker loop
            p.starmap_async(worker_wrapper, jobs)
            time.sleep(2)
            p.terminate()

        #assess results
        with self.subTest('Were outcome messages saved to file?'):
            with open('test_output/outcomes.tsv', 'r') as tsv:
                text = tsv.readlines()
                self.assertGreater(len(text), 1)

if __name__ == '__main__':
    import make_test_data
    set_start_method('fork')
    unittest.main()
        
        
        
        