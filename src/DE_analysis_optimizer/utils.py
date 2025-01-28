#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 14:20:40 2025

@author: 4vt
"""

def init_data_manager(options, pool):
    from multiprocessing import Pipe
    from DE_analysis_optimizer.workers import run_data_manager
    
    #initialize attempts manager
    manager_ends = []
    optimizer_ends = []
    for _ in range(options.cores - 1):
        manager_end, optimizer_end = Pipe()
        manager_ends.append(manager_end)
        optimizer_ends.append(optimizer_end)
    pool.starmap_async(run_data_manager, ((options, manager_ends),))
    
    return optimizer_ends

def read_data(options):
    '''
    Reads in the raw analyte quantities file.
    '''
    import pandas as pd    
    from DE_analysis_optimizer.data import Data
    
    df = pd.read_csv(options.data_file, sep = '\t')
    data = Data(options, df)
    return data

class Outcome:
    def __init__(self, steps, recall, FDR):
        self.recall = recall
        self.FDR = FDR
        self.steps = steps[1].to_dict()
        self.hash = hash(''.join(steps[1].values))
    
    def __hash__(self):
        return self.hash
    
    def __eq__(self, o):
        return self.hash == hash(o)

def get_outcomes(options):
    '''
    Constructs a list of Outcome objects which hold the settings and performance metrics which are the targets of optimization.
    '''
    import os
    import pandas as pd
    
    data = pd.read_csv(os.path.join(options.output_directory, 'outcomes.tsv'), sep = '\t')
    steps = data[sorted(list(options.step_options.keys()))].iterrows()
    truth = options.ground_truths[0]    
    outcomes = [Outcome(step, recall, FDR) for step, recall, FDR in zip(steps, data[f'{truth}_recall'], data[f'{truth}_FDR'])]
    return outcomes

def get_attempts(options):
    '''
    Constructs a set of paramteter combinations for initiated attempts.
    '''
    import pandas as pd

    data = pd.read_csv('attempted.tsv', sep = '\t')
    attempts = set(''.join(attempt) for attempt in zip(*[data[c] for c in data.columns]))
    return attempts


