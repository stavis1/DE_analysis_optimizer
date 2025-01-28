#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 13:36:06 2025

@author: 4vt
"""

def run_worker(options, initial_data):
    '''
    There will be one worker process run per core.
    Each will live for the lifetime of the program.
    Each will run an infinite loop of optimization steps. 
    All inter-process communication will be mediated by writing to on-disk files.
    '''
    from copy import deepcopy
    
    from DE_analysis_optimizer.utils import get_outcomes, get_attempts
    
    while True:
        #read outcomes
        outcomes = get_outcomes(options)
        
        #read attempted pipelines
        attempts = get_attempts(options)
        
        #generate new pipeline
        
        #write current pipeline to attempted pipelines table
        
        #set up new working data
        data = deepcopy(initial_data)

        #run the pipeline
        
        #assess results
        
        #write outcomes

