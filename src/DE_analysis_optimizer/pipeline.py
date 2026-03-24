#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 17:53:15 2025

@author: 4vt
"""
import warnings
import numpy as np

class Outcome:
    def __init__(self, steps, results):
        self.steps = steps
        self.results = results
        self.recall = results[0]
        self.PPV = results[1]
        self.hash = hash((*self.steps, self.PPV, self.recall))
        
    def __hash__(self):
        return self.hash
    
    def __eq__(self, o):
        return self.hash == hash(o)

    def report(self):
        return list(self.steps) + list(self.results)

class Pipeline:
    def __init__(self, options):
        self.step_order = options.step_order
        self.steps = {}
        self.results = []
    
    def __hash__(self):
        return hash(self.attempt_line())
    
    def __eq__(self, o):
        return hash(self) == hash(o)
    
    def add_step(self, step, order):
        self.steps[order] = step
    
    def run(self, data):
        #run the pipeline
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for step in self.step_order:
                data = self.steps[step].process(data)
        
            #calculate quality metrics for each definition of ground truth
            truths = data.get_truths()
            significant = data.get_significance()
            tp = np.nansum(np.logical_and(significant[:,np.newaxis], truths), axis = 0)
            fp = np.nansum(np.logical_and(significant[:,np.newaxis], np.logical_not(truths)), axis = 0)
            fn = np.nansum(np.logical_and(np.logical_not(significant)[:,np.newaxis], truths), axis = 0)
            PPVs = fp/(fp+tp)
            recalls = fn/(fn+tp)
            for PPV, recall in zip(PPVs, recalls):
                self.results.append(recall)
                self.results.append(PPV)
    
    def attempt_line(self):
        return ''.join([self.steps[step].name for step in self.step_order])
    
    def report(self):
        return Outcome([self.steps[step].name for step in self.step_order], self.results)



