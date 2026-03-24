#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 17:44:16 2024

@author: anon
"""
import unittest
from multiprocessing import set_start_method
from options_tests import *
from utils_tests import *
from data_tests import *
from pipeline_tests import *
from genetic_algorithm_tests import *
from integration_test import *
from pipeline_steps_tests import *

if __name__ == '__main__':
    import make_test_data
    set_start_method('fork')
    unittest.main()