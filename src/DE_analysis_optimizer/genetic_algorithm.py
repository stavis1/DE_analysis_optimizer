#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 15:36:09 2025

@author: 4vt
"""

from DE_analysis_optimizer.pipeline import Pipeline

def get_breeding_population(outcomes):
    from sortedcontainers import SortedList
    
    #sorted lists substantially speed up dominance checks
    recall_order = SortedList(outcomes, key = lambda o: o.recall)
    PPV_order = SortedList(outcomes, key = lambda o: o.PPV)
    
    double_pareto_front = [] #this will be all outcomes that are dominated by at most one other outcome
    for outcome in outcomes:
        #find all outcomes better in each dimension
        recall_idx = recall_order.bisect_right(outcome)
        PPV_idx = PPV_order.bisect_right(outcome)
        
        #identify dominating outcomes
        dominators = set(recall_order[recall_idx:]).intersection(PPV_order[PPV_idx:])
        if len(dominators) <= 1:
            double_pareto_front.append(outcome)
    
    return double_pareto_front
        
def breed(options, breeders, all_pipeline_steps):
    #get two parents from the breeding population
    if len(breeders) > 1:
        parent1, parent2 = options.rng.choice(breeders, 2, replace = False)
    else:
        parent1, parent2 = breeders[0]
    
    #choose which parent donates a step for each step in the new pipeline
    step_choices = options.rng.choice((0,1), len(parent1.steps))
    new_steps = [parent1.steps[i] if choice else parent2.steps[i] for i, choice in enumerate(step_choices)]
    
    #make new pipeline
    child = Pipeline(options)
    for step_name, order in zip(new_steps, options.step_order):
        step = all_pipeline_steps[step_name]
        child.add_step(step, order)
    return child

def mutate(options, pipeline, attempts, all_pipeline_steps):
    #randomly change steps in the pipeline until it is different from any pipeline yet attempted
    while pipeline in attempts:
        order = options.rng.choice(list(options.step_options.keys()))
        step = all_pipeline_steps[options.rng.choice(options.step_options[order])]
        pipeline.add_step(step, order)
    return pipeline


def random_pipeline(options, all_pipeline_steps):
    #initialize a pipeline with random choices for each step
    pipeline = Pipeline(options)
    for order in options.step_order:
        choice = options.rng.choice(options.step_options[order])
        step = all_pipeline_steps[choice]
        pipeline.add_step(step, order)
    return pipeline





