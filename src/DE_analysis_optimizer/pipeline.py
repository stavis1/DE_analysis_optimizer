#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 17:53:15 2025

@author: 4vt
"""
import numpy as np

class Pipeline:
    def __init__(self, options):
        self.step_order = sorted(list(options.step_options.keys()))
        self.steps = {}
        self.results = []
    
    def __hash__(self):
        return hash(self.attempt_line())
    
    def __eq__(self, o):
        return hash(self) == hash(o)
    
    def add_step(self, step, order):
        self.steps[order] = step
    
    def run(self, data):
        for step in self.step_order:
            data = self.steps[step].process(data)
        truths = data.get_truths()
        significant = data.get_significance()
        tp = np.nansum(np.logical_and(significant[:,np.newaxis], truths), axis = 0)
        fp = np.nansum(np.logical_and(significant[:,np.newaxis], np.logical_not(truths)), axis = 0)
        fn = np.nansum(np.logical_and(np.logical_not(significant)[:,np.newaxis], truths), axis = 0)
        FDRs = fp/(fp+tp)
        recalls = fn/(fn+tp)
        for FDR, recall in zip(FDRs, recalls):
            self.results.append(recall)
            self.results.append(FDR)
    
    def attempt_line(self):
        return ''.join([self.steps[step].name for step in self.step_order])
    
    def report(self):
        return [self.steps[step].name for step in self.step_order] + self.results



