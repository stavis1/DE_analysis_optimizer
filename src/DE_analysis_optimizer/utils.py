#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 14:20:40 2025

@author: 4vt
"""

from multiprocessing import Pipe
from DE_analysis_optimizer.workers import run_data_manager
from DE_analysis_optimizer.genetic_algorithm import get_breeding_population, breed, mutate, random_pipeline
from DE_analysis_optimizer import pipeline_steps
import pandas as pd    
from DE_analysis_optimizer.data import Data
    

def init_data_manager(options, pool):    
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
    df = pd.read_csv(options.data_file, sep = '\t')
    if options.protein_metadata:
        metadata = pd.read_csv(options.protein_metadata, sep = '\t')
        data = Data(options, df, metadata)
    else:
        data = Data(options, df)
    
    return data

def get_all_pipeline_steps(options):
    #set up a dictionary that maps pipeline step names to their objects
    all_pipeline_steps = {}
    for Step in pipeline_steps.__dict__.values():
        if type(Step) == type:
            step = Step(options)
            if hasattr(step, 'name') and type(step.name) == str:
                all_pipeline_steps[step.name] = step
    
    return all_pipeline_steps

class Message:
    def __init__(self, purpose, value):
        self.purpose = purpose
        self.value = value


class NewPipelineGenerator():
    def __init__(self, pipe, options):
        self.pipe = pipe
        self.options = options
        self.all_pipeline_steps = get_all_pipeline_steps(options)
        self.outcomes = []
        self.attempts = set()
        
    def get_new_pipeline(self):
        #read outcomes
        self.pipe.send(Message('get_outcomes', len(self.outcomes)))
        self.outcomes.extend(self.pipe.recv())
        
        #generate new pipeline
        if self.outcomes:
            self.outcomes = get_breeding_population(self.outcomes)
            pipeline = breed(self.options, self.outcomes, self.all_pipeline_steps)
        else:
            pipeline = random_pipeline(self.options, self.all_pipeline_steps)
        
        #read attempted pipelines
        self.pipe.send(Message('get_attempts', len(self.attempts)))
        self.attempts.update(self.pipe.recv())
        
        #ensure the new pipeline is unique
        pipeline = mutate(self.options, pipeline, self.attempts, self.all_pipeline_steps)
        
        #write current pipeline to attempted pipelines table
        attempt = pipeline.attempt_line()
        self.pipe.send(Message('submit_attempt', attempt))
        return pipeline
