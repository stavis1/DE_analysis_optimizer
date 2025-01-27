#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from DE_analysis_optimizer.options import Options
options = Options()

from multiprocessing import Pool
from DE_analysis_optimizer.worker import run_worker
from DE_analysis_optimizer.utils import init_files

#set up working directory
init_files(options)

#run parallel worker loops
with Pool(options.cores) as p:
    p.map(run_worker, range(options.cores))
