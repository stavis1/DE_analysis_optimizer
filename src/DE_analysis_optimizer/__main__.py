#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DE_analysis_optimizer.options import Options
options = Options()

from multiprocessing import Pool
from DE_analysis_optimizer.worker import run_worker
from DE_analysis_optimizer.utils import init_files, read_data

#set up working directory
init_files(options)
initial_data = read_data(options)

#run parallel worker loops
with Pool(options.cores) as p:
    p.starmap(run_worker, [(options, initial_data)]*len(options.cores))
