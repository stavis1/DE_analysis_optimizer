#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 15:36:09 2025

@author: 4vt
"""

from DE_analysis_optimizer.pipeline import Pipeline

#set up a random number generator for breeding and mutation
import numpy as np
rng = np.random.default_rng(1)

def get_breeding_population(outcomes):
    from sortedcontainers import SortedList
    
    recall_order = SortedList(outcomes, key = lambda o: o.recall)
    PPV_order = SortedList(outcomes, key = lambda o: o.PPV)
    
    double_pareto_front = [] #this will be all outcomes that are dominated by at most one other outcome
    for outcome in outcomes:
        recall_idx = recall_order.bisect_right(outcome)
        PPV_idx = PPV_order.bisect_right(outcome)
        dominators = set(recall_order[recall_idx:]).intersection(PPV_order[PPV_idx:])
        if len(dominators) <= 1:
            double_pareto_front.append(outcome)
    
    return double_pareto_front
        
def breed(options, breeders, all_pipeline_steps):
    parent1, parent2 = rng.choice(breeders, 2, replace = False)
    step_choices = rng.choice((0,1), len(parent1.steps))
    new_steps = [parent1.steps[i] if choice else parent2.steps[i] for i, choice in enumerate(step_choices)]
    child = Pipeline(options)
    step_orders = sorted(list(options.step_options.keys()))
    for step_name, order in zip(new_steps, step_orders):
        step = all_pipeline_steps[step_name]
        child.add_step(step, order)
    return child

def mutate(options, pipeline, attempts, all_pipeline_steps):
    while pipeline in attempts:
        order = rng.choice(list(options.step_options.keys()))
        step = all_pipeline_steps[rng.choice(options.step_options[order])]
        pipeline.add_step(step, order)
    return pipeline








