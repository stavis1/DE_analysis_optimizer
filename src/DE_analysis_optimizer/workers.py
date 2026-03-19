#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 13:36:06 2025

@author: 4vt
"""

class Message:
    def __init__(self, purpose, value):
        self.purpose = purpose
        self.value = value

def run_optimization_worker(options, initial_data, pipe):
    '''
    There will be one worker process run per core.
    Each will live for the lifetime of the program.
    Each will run an infinite loop of optimization steps. 
    '''
    from copy import deepcopy
    from DE_analysis_optimizer.genetic_algorithm import get_breeding_population, breed, mutate
    from DE_analysis_optimizer import pipeline_steps

    #set up a dictionary that maps pipeline step names to their objects
    all_pipeline_steps = {}
    for Step in pipeline_steps.__dict__.values():
        if type(Step) == type:
            step = Step()
            if hasattr(step, 'name') and type(step.name) == str:
                all_pipeline_steps[step.name] = step
    
    outcomes = []
    attempts = set()
    while True:
        #read outcomes
        pipe.send(Message('get_outcomes', len(outcomes)))
        outcomes.extend(pipe.recv())
        
        #generate new pipeline
        outcomes = get_breeding_population(outcomes)
        pipeline = breed(options, outcomes, all_pipeline_steps)
        
        #read attempted pipelines
        pipe.send(Message('get_attempts', len(attempts)))
        attempts.update(pipe.recv())
        
        #ensure the new pipeline is unique
        pipeline = mutate(options, pipeline, attempts, all_pipeline_steps)
        
        #write current pipeline to attempted pipelines table
        attempt = pipeline.attempt_line()
        pipe.send(Message('submit_attempt', attempt))
        
        #set up new working data
        data = deepcopy(initial_data)

        #run the pipeline
        pipeline.run(data)
        
        #write outcomes
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




