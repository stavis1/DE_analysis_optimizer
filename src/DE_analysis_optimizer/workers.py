#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 13:36:06 2025

@author: 4vt
"""

def run_optimization_worker(options, initial_data, pipe):
    '''
    There will be one worker process run per core.
    Each will live for the lifetime of the program.
    Each will run an infinite loop of optimization steps. 
    '''
    from copy import deepcopy
    import numpy as np
    from DE_analysis_optimizer.utils import NewPipelineGenerator, Message

    generator = NewPipelineGenerator(pipe, options)
    while True:
        pipeline = generator.get_new_pipeline()
        
        try:
            #set up new working data
            data = deepcopy(initial_data)
    
            #run the pipeline
            pipeline.run(data)
            
            #write outcomes
            outcome = pipeline.report()
            pipe.send(Message('submit_outcome', outcome))
        
        except:
            #failed pipelines get nan metrics
            pipeline.results = [np.nan]*len(options.ground_truths)*2
            outcome = pipeline.report()
            pipe.send(Message('submit_outcome', outcome))

def run_data_manager(options, pipes):
    '''
    Receives and stores attempted runs.
    Provides lists of attempted runs upon request.
    Receives, stores, and writes to file outcomes.
    Provides lists of outcomes upon request.
    '''
    import os
    import traceback

    #initialize the outcomes file
    outcomes = [f'{col}_{metric}' for col in options.ground_truths for metric in ('recall', 'PPV')]
    outcomes_file = os.path.join(options.output_directory, 'outcomes.tsv')
    with open(outcomes_file, 'w') as tsv:
        tsv.write('\t'.join(options.step_order + outcomes) + '\n')
        
    #monitor pipes
    attempts = []
    outcomes = []
    while True:
        for pipe in pipes:
            if pipe.poll():
                message = pipe.recv()
                
                #handle attempts
                if message.purpose == 'get_attempts':
                    pipe.send(attempts[message.value:])
                elif message.purpose == 'submit_attempt':
                    attempts.append(message.value)
                
                #handle outcomes
                elif message.purpose == 'get_outcomes':
                    pipe.send(outcomes[message.value:])
                elif message.purpose == 'submit_outcome':
                    outcomes.append(message.value)

                    with open(outcomes_file, 'a') as tsv:
                        tsv.write('\t'.join(str(e) for e in message.value.report()) + '\n')

