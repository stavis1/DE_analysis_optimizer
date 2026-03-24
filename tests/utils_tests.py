#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:04:18 2025

@author: 4vt
"""
import unittest
from shutil import rmtree
import os
from multiprocessing import Pool, set_start_method

import testSuite_ancestor_objs
from DE_analysis_optimizer.utils import read_data, init_data_manager, NewPipelineGenerator, Message
from DE_analysis_optimizer.pipeline import Outcome

def writer(pipe):
    pipe.send(Message('submit_attempt', 'testattempt'))
    
    outcome = Outcome(['test'], [0.1, 0.2])
    pipe.send(Message('submit_outcome', outcome))
    return None

def reader(pipe):
    pipe.send(Message('get_attempts', 0))
    attempt = pipe.recv()
    pipe.send(Message('get_outcomes', 0))
    outcome = pipe.recv()
    return (attempt, outcome)

class utilsTestSuite(testSuite_ancestor_objs.baseTestSuite):    
    def test_data_reader_finds_data(self):
        data = read_data(self.options)
        self.assertIsNotNone(data.get_data())

    def test_data_manager_works(self):
        self.delete('test_output/outcomes.tsv')
        self.options.cores = 3
                
        with Pool(self.options.cores) as p:
            pipes = init_data_manager(self.options, p)

            p.apply(writer, (pipes[0],))            
            attempt, outcome = p.apply(reader, (pipes[0],))
            p.terminate()
    
        with self.subTest('Is the attempt message correct?'):
            self.assertEqual(attempt, ['testattempt'])
        with self.subTest('Is the outcome message correct?'):
            self.assertEqual(outcome[0].report(), ['test', 0.1, 0.2])
        with self.subTest('Was the outcome message saved to file?'):
            with open('test_output/outcomes.tsv', 'r') as tsv:
                text = tsv.readlines()[1]
                self.assertEqual(text, 'test\t0.1\t0.2\n')
    
    def test_race_condition_robustness(self):        
        with Pool(2) as p:
            #initialize the manager process for attempts and outcomes data
            pipe = init_data_manager(self.options, p)[0]
            
            #initialize two new pipeline generators
            generators = [NewPipelineGenerator(pipe, self.options) for _ in range(2)]
            
            pipeline_strings = []
            #run these generators in lockstep
            for i in range(3):
                #generate pipelines
                pipelines = [generator.get_new_pipeline() for generator in generators]
                
                #generate outcomes
                outcomes = [Outcome([p.steps[step].name for step in p.step_order], [i/3]*2) for p in pipelines]
                for outcome in outcomes:
                    pipeline_strings.append(''.join(outcome.steps))
                    pipe.send(Message('submit_outcome', outcome))
            
            with self.subTest('Are all pipelines unique?'):
                self.assertEqual(len(set(pipeline_strings)), len(pipeline_strings))
            with self.subTest('Have all generators recieved attempt updates?'):
                self.assertTrue(all(generator.attempts for generator in generators))

if __name__ == '__main__':
    import make_test_data
    set_start_method('fork')
    unittest.main()
