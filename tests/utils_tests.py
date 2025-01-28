#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:04:18 2025

@author: 4vt
"""

from shutil import rmtree
import os
from multiprocessing import Pool

import testSuite_ancestor_objs
from DE_analysis_optimizer.utils import read_data, init_data_manager
from DE_analysis_optimizer.workers import Message

def writer(pipe):
    pipe.send(Message('submit_attempt', ['test', 'attempt']))
    pipe.send(Message('submit_outcome', ['test', 'outcome']))
    return None

def reader(pipe):
    pipe.send(Message('get_attempts', 0))
    attempt = pipe.recv()
    pipe.send(Message('get_outcomes', 0))
    outcome = pipe.recv()
    return (attempt, outcome)

class utilsTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def delete(self, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            else:
                rmtree(path, ignore_errors=True)
    
    def test_data_reader_finds_data(self):
        data = read_data(self.options)
        self.assertIsNotNone(data.get_data())
        self.delete('test_output/')

    def test_data_manager_works(self):
        self.delete('test_output/outcomes.tsv')
        self.options.cores = 3
                
        with Pool(self.options.cores) as p:
            pipes = init_data_manager(self.options, p)

            p.apply(writer, (pipes[0],))            
            attempt, outcome = p.apply(reader, (pipes[0],))
            p.terminate()
    
        with self.subTest('Is the attempt message correct?'):
            self.assertEqual(attempt, [['test', 'attempt']])
        with self.subTest('Is the outcome message correct?'):
            self.assertEqual(outcome, [['test', 'outcome']])
        with self.subTest('Was the outcome message saved to file?'):
            with open('test_output/outcomes.tsv', 'r') as tsv:
                text = tsv.readlines()[1]
                self.assertEqual(text, 'test\toutcome\n')
        
        self.delete('test_output/')
    


