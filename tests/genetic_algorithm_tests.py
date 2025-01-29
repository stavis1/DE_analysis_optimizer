#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 17:22:29 2025

@author: 4vt
"""

import numpy as np
rng = np.random.default_rng(1)

import testSuite_ancestor_objs
from DE_analysis_optimizer.genetic_algorithm import get_breeding_population, breed, mutate

class geneticAlgorithmTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def test_get_breeding_pop_works(self):
        class DummyOutcome():
            def __init__(self, recall, PPV):
                self.recall = recall
                self.PPV = PPV
                self.hash = hash(recall + PPV + rng.random())
            
            def __hash__(self):
                return self.hash
            
            def __eq__(self, o):
                return self.hash == hash(o)
            
        recalls = [0.1,0.2,0.3]
        PPVs = [0.1,0.2,0.3]
        outcomes = [DummyOutcome(recall, PPV) for recall, PPV in zip(recalls, PPVs)]
        new_outcomes = get_breeding_population(outcomes)
        
        with self.subTest('Are there the correct number of outcomes?'):
            self.assertEqual(len(new_outcomes), 2)
        with self.subTest('Were the correct outcomes chosen?'):
            self.assertEqual(min(new_outcomes, key = lambda o: o.recall).recall, 0.2)
            self.assertEqual(min(new_outcomes, key = lambda o: o.PPV).PPV, 0.2)
            self.assertEqual(max(new_outcomes, key = lambda o: o.recall).recall, 0.3)
            self.assertEqual(max(new_outcomes, key = lambda o: o.PPV).PPV, 0.3)
    
    def test_breeding_works(self):
        #make fake pipeline options
        class DummyPipelineStep():
            def __init__(self, name):
                self.name = name

        N_steps = 10
        step_options = {}
        for i in range(N_steps):
            step_options[str(i)] = [f'{i}_{j}' for j in range(3)]
        all_pipeline_steps = {n:DummyPipelineStep(n) for l in step_options.values() for n in l}
        self.options.step_options = step_options
        
        #make fake outcomes
        class DummyOutcome():
            def __init__(self, recall, PPV, steps):
                self.recall = recall
                self.PPV = PPV
                self.steps = steps
                self.hash = hash(str(recall + PPV) + ''.join(steps))
            
            def __hash__(self):
                return self.hash
            
            def __eq__(self, o):
                return self.hash == hash(o)
            
        recalls = [0.1,0.2,0.3]
        PPVs = [0.2,0.1,0.3]
        step_lists = [[f'{i}_{j}' for i in range(N_steps)] for j in range(3)]
        outcomes = [DummyOutcome(recall, PPV, steps) for recall, PPV, steps in zip(recalls, PPVs, step_lists)]
        
        #test breeding function
        pipeline = breed(self.options, outcomes, all_pipeline_steps)        
        steps_chosen = [pipeline.steps[o].name for o in pipeline.step_order]
        step_idxs = set(s[-1] for s in steps_chosen)
        
        with self.subTest('Did some amount of crossover happen?'):
            self.assertEqual(len(step_idxs), 2)
    
    def test_mutatation_works(self):
        #make fake pipeline options
        class DummyPipelineStep():
            def __init__(self, name):
                self.name = name

        N_steps = 10
        step_options = {}
        for i in range(N_steps):
            step_options[str(i)] = [f'{i}_{j}' for j in range(3)]
        all_pipeline_steps = {n:DummyPipelineStep(n) for l in step_options.values() for n in l}
        self.options.step_options = step_options
        
        #make fake outcomes
        class DummyOutcome():
            def __init__(self, recall, PPV, steps):
                self.recall = recall
                self.PPV = PPV
                self.steps = steps
                self.hash = hash(str(recall + PPV) + ''.join(steps))
            
            def __hash__(self):
                return self.hash
            
            def __eq__(self, o):
                return self.hash == hash(o)
            
        recalls = [0.1,0.2,0.3]
        PPVs = [0.2,0.1,0.3]
        step_lists = [[f'{i}_{j}' for i in range(N_steps)] for j in range(3)]
        outcomes = [DummyOutcome(recall, PPV, steps) for recall, PPV, steps in zip(recalls, PPVs, step_lists)]
        
        #test mutation function
        pipeline = breed(self.options, outcomes, all_pipeline_steps)
        attempts = set([pipeline.attempt_line()])
        steps_chosen_init = ''.join([pipeline.steps[o].name[-1] for o in pipeline.step_order])
        pipeline = mutate(self.options, pipeline, attempts, all_pipeline_steps)
        steps_chosen = ''.join([pipeline.steps[o].name[-1] for o in pipeline.step_order])
       
        with self.subTest('Did some amount of mutation happen?'):
            self.assertNotEqual(steps_chosen, steps_chosen_init)

        