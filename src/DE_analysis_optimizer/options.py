#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 15:03:53 2024

@author: 4vt
"""

from argparse import ArgumentParser
import os
import sys

class InputError(Exception):
    pass

class Options:
    def __init__(self):
        self.parse_args()
        self.handle_working_directory()
        self.logger_init()
        self.validate_inputs()        
        self.find_data()
        if self.cores < 1:
            self.cores = os.cpu_count()
    
    def parse_args(self):
        parser = ArgumentParser()
        parser.add_argument('-o', '--options', action = 'store', required = True,
                            help = 'Path to options file.')
        parser.add_argument('-p', '--print', action = 'store', required = False, default = False,
                            help = 'print a default options file with the specified name and exit', metavar = 'options.toml')
        args = parser.parse_args()

        if args.print:
            self.print_options(args.print)
            sys.exit(0)
        elif not args.options:
            raise InputError('One of "--options" or "--print" must be used.')

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
    
    def logger_init(self):
        import logging
        
        self.logs = logging.getLogger('DE_analysis_optimizer')
        self.logs.setLevel(10)
        formatter = formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s: %(message)s')

        logfile = logging.FileHandler(self.log_file)
        logfile.setLevel(10)
        logfile.setFormatter(formatter)
        self.logs.addHandler(logfile)
        
        logstream = logging.StreamHandler()
        logstream.setLevel(self.log_level)
        logstream.setFormatter(formatter)
        self.logs.addHandler(logstream)
    
    def validate_inputs(self):
        #check if toml has all necessary information
        required = ['working_directory',
                    'output_directory',
                    'overwrite',
                    'log_file',
                    'log_level',
                    'cores']
        problems = [r for r in required if not r in self.__dict__.keys()]
        if problems:
            msg = 'Required settings not found in options file:\n' + '\n'.join(problems)
            self.logs.error(msg)
            raise InputError()

    def find_data(self):
        pass

    def print_options(self, path):
        import shutil
        resolved_path = os.path.abspath(os.path.dirname(__file__))
        example_options = os.path.join(resolved_path, 'example_options.toml')
        shutil.copy2(example_options, path)



