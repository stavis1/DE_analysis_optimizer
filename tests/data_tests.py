#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 15:54:20 2025

@author: 4vt
"""

from copy import copy
import numpy as np

from DE_analysis_optimizer.utils import read_data
import testSuite_ancestor_objs

class dataTestSuite(testSuite_ancestor_objs.baseTestSuite):
    def setUp(self):
        super().setUp()
        self.data = read_data(self.options)
    
    def test_getters_work(self):
        with self.subTest('Test get_A()'):
            self.assertEqual((100, 3), self.data.get_A().shape)

        with self.subTest('Test get_B()'):
            self.assertEqual((100, 3), self.data.get_B().shape)    

        with self.subTest('Test get_data()'):
            self.assertEqual((100, 6), self.data.get_data().shape)    

        with self.subTest('Test get_truths()'):
            self.assertEqual((100, 2), self.data.get_truths().shape)    

        with self.subTest('Test get_results()'):
            self.assertEqual((100,), self.data.get_results().shape)    

    def test_setters_work(self):
        ones_100x3 = np.full((100,3), 1)
        with self.subTest('Test set_A()'):
            A_init = np.sum(self.data.get_A().to_numpy())
            self.data.set_A(ones_100x3)
            newsum = np.sum(self.data.get_A().to_numpy())
            self.assertEqual(newsum, 100*3)
            self.assertNotEqual(A_init, newsum)

        with self.subTest('Test set_B()'):
            B_init = np.sum(self.data.get_B().to_numpy())
            self.data.set_B(ones_100x3)
            newsum = np.sum(self.data.get_B().to_numpy())
            self.assertEqual(newsum, 100*3)
            self.assertNotEqual(B_init, newsum)
        
        with self.subTest('Test set_results()'):
            results_init = np.sum(self.data.get_results())
            rng = np.random.default_rng(1)
            newresults = rng.choice((True, False), 100)
            self.data.set_results(newresults)
            newsum = np.sum(self.data.get_results().to_numpy())
            self.assertEqual(newsum, np.sum(newresults))
            self.assertNotEqual(results_init, newsum)
            
    