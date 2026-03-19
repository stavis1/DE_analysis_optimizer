#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 15:03:53 2024

@author: 4vt
"""

from argparse import ArgumentParser
import os
import sys

from DE_analysis_optimizer import pipeline_steps

class InputError(Exception):
    pass

class Options:
    def __init__(self):
        self.parse_args()
        self.handle_working_directory()
        self.validate_inputs()        
        if self.cores < 1:
            self.cores = os.cpu_count()
        import numpy as np
        self.rng = np.random.default_rng(self.rng_seed)
        self.step_order = sorted(list(self.step_options.keys()))
    
    def parse_args(self):
        #parse command line arguments
        parser = ArgumentParser()
        parser.add_argument('-o', '--options', action = 'store', required = True,
                            help = 'Path to options file.')
        parser.add_argument('-p', '--print', action = 'store', required = False, default = False,
                            help = 'print a default options file with the specified name and exit', metavar = 'options.toml')
        args = parser.parse_args()
        
        #print example options file or fail if one is not provided
        if args.print:
            self.print_options(args.print)
            sys.exit(0)
        elif not args.options:
            raise InputError('One of "--options" or "--print" must be used.')
            
        #parse the options toml and add its entries as attributes to this object
        import tomllib
        with open(args.options,'rb') as toml:
            options = tomllib.load(toml)
        self.__dict__.update(options)
    
    def handle_working_directory(self):
        os.chdir(self.working_directory)
        if not os.path.exists(self.output_directory):
            os.mkdir(self.output_directory)      
        else:
            if not self.overwrite:
                raise FileExistsError('An output directory with this name already exists and overwrite is false.')
    
    def validate_inputs(self):
        #check if toml has all necessary information
        required = ['working_directory',
                    'output_directory',
                    'overwrite',
                    'cores',
                    'data_file',
                    'step_options',
                    'rng_seed']
        problems = [r for r in required if not r in self.__dict__.keys()]
        if problems:
            msg = 'Required settings not found in options file:\n' + '\n'.join(problems)
            raise InputError(msg)
        
        #make sure the input data file exists
        if not os.path.exists(self.data_file):
            raise InputError('The specified data file could not be found.')
        
        #make sure the pipeline options are nonempty and contain real steps
        defined_steps = set(o().name for o in pipeline_steps.__dict__.values() if hasattr(o, 'process'))
        for step in self.step_options.keys():
            if not self.step_options[step]:
                raise InputError(f'The pipeline step {step} is empty.')
            for opt in self.step_options[step]:
                if opt not in defined_steps:
                    raise InputError(f'The pipeline step option {opt} is not defined.')

    def print_options(self, path):
        import shutil
        #find location of __main__.py
        resolved_path = os.path.abspath(os.path.dirname(__file__))
        
        #copy example options to requested location
        example_options = os.path.join(resolved_path, 'example_options.toml')
        shutil.copy2(example_options, path)



