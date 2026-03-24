#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 12:18:53 2026

@author: chemod-u02
"""
import unittest
from multiprocessing import Pool, set_start_method
import time
import pandas as pd
import numpy as np
import testSuite_ancestor_objs
from DE_analysis_optimizer.workers import run_optimization_worker
from DE_analysis_optimizer.utils import read_data, init_data_manager

class workersTestSuite(testSuite_ancestor_objs.baseProteomicsTestSuite):
    def test_integration(self):
        initial_data = read_data(self.options)
        
        with Pool(self.options.cores) as p:
            #initialize the manager process for attempts and outcomes data
            pipes = init_data_manager(self.options, p)
            
            #construct jobs
            n_workers = len(pipes)
            jobs = zip([self.options]*n_workers, [initial_data]*n_workers, pipes)
            
            #run parallel worker loops
            p.starmap_async(run_optimization_worker, jobs)
            time.sleep(2)
            p.terminate()
        
        
        #assess results
        outcomes = pd.read_csv('test_output/outcomes.tsv', sep = '\t')
        with self.subTest('Were outcome messages saved to file?'):
            self.assertGreater(outcomes.shape[0], 0)
        
        with self.subTest('Are all pipelines unique?'):
            pipeline_cols = [c for c in outcomes.columns if c in self.options.step_order]
            pipelines = [''.join(p) for p in zip(*[outcomes[c] for c in pipeline_cols])]
            self.assertEqual(len(set(pipelines)), outcomes.shape[0])
            
        with self.subTest('Were all metrics non-NAN at least once?'):
            metric_cols = [c for c in outcomes.columns if c.startswith('truth')]
            self.assertTrue(all(np.any(np.isfinite(outcomes[c])) for c in metric_cols))

if __name__ == '__main__':
    import make_test_data
    set_start_method('fork')
    unittest.main()
        
        
        
        