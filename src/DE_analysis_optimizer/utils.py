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
    if options.protein_metadata:
        metadata = pd.read_csv(options.protein_metadata)
        data = Data(options, df, metadata)
    else:
        data = Data(options, df)
    
    return data

def get_all_pipeline_steps():
    from DE_analysis_optimizer import pipeline_steps

    #set up a dictionary that maps pipeline step names to their objects
    all_pipeline_steps = {}
    for Step in pipeline_steps.__dict__.values():
        if type(Step) == type:
            step = Step()
            if hasattr(step, 'name') and type(step.name) == str:
                all_pipeline_steps[step.name] = step
    
    return all_pipeline_steps

