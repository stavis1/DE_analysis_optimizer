#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 15:54:20 2025

@author: 4vt
"""
import unittest
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
            self.assertEqual((100, 6), self.data.get_A().shape)

        with self.subTest('Test get_B()'):
            self.assertEqual((100, 6), self.data.get_B().shape)    

        with self.subTest('Test get_data()'):
            self.assertEqual((100, 12), self.data.get_data().shape)    

        with self.subTest('Test get_truths()'):
            self.assertEqual((100, 2), self.data.get_truths().shape)    

        with self.subTest('Test get_significance()'):
            self.assertEqual((100,), self.data.get_significance().shape)    

        with self.subTest('Test get_score()'):
            self.assertEqual((100,), self.data.get_score().shape)    

    def test_setters_work(self):
        ones_100x6 = np.full((100,6), 1)
        with self.subTest('Test set_A()'):
            A_init = np.sum(self.data.get_A())
            self.data.set_A(ones_100x6)
            newsum = np.sum(self.data.get_A())
            self.assertEqual(newsum, 100*6)
            self.assertNotEqual(A_init, newsum)

        with self.subTest('Test set_B()'):
            B_init = np.sum(self.data.get_B())
            self.data.set_B(ones_100x6)
            newsum = np.sum(self.data.get_B())
            self.assertEqual(newsum, 100*6)
            self.assertNotEqual(B_init, newsum)
        
        with self.subTest('Test set_significance()'):
            results_init = np.sum(self.data.get_significance())
            rng = np.random.default_rng(1)
            newresults = rng.choice((True, False), 100)
            self.data.set_significance(newresults)
            newsum = np.sum(self.data.get_significance())
            self.assertEqual(newsum, np.sum(newresults))
            self.assertNotEqual(results_init, newsum)
            
        with self.subTest('Test set_score()'):
            results_init = np.sum(np.isfinite(self.data.get_score()))
            rng = np.random.default_rng(1)
            newresults = rng.uniform(0, 1, 100)
            self.data.set_score(newresults)
            newsum = np.sum(np.isfinite(self.data.get_score()))
            self.assertEqual(newsum, np.sum(np.isfinite(newresults)))
            self.assertNotEqual(results_init, newsum)


if __name__ == '__main__':
    import make_test_data
    unittest.main()
