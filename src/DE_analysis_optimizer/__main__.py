#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DE_analysis_optimizer.options import Options
options = Options()

from multiprocessing import Pool, set_start_method
from DE_analysis_optimizer.worker import run_optimization_worker
from DE_analysis_optimizer.utils import read_data, init_data_manager

#parse data
initial_data = read_data(options)

if __name__ == '__main__':
    set_start_method('fork')
    with Pool(options.cores) as p:
        #initialize the manager process for attempts and outcomes data
        pipes = init_data_manager(options, p)
        
        #construct jobs
        n_workers = len(pipes)
        jobs = zip([options]*n_workers, [initial_data]*n_workers, pipes)
        
        #run parallel worker loops
        p.starmap(run_optimization_worker, jobs)
