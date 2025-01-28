#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 15:10:36 2025

@author: 4vt
"""

class Data:
    def __init__(self, options, df):
        self.history = ''
        self.A_cols = list(options.A)
        self.B_cols = list(options.B)
        self.ground_truths = list(options.ground_truths)
        self.data = df
        self.data['result'] = [True]*df.shape[0]
    
    def __hash__(self):
        return hash(self.history)
    
    def get_A(self):
        return self.data[self.A_cols]

    def set_A(self, data):
        self.data[self.A_cols] = data

    def get_B(self):
        return self.data[self.B_cols]

    def set_B(self, data):
        self.data[self.B_cols] = data
    
    def get_data(self):
        return self.data[self.A_cols + self.B_cols]
    
    def set_data(self, data):
        self.data[self.A_cols + self.B_cols] = data
    
    def prune(self, to_keep):
        self.data = self.data[to_keep]

    def get_truths(self):
        return self.data[self.ground_truths]
    
    def get_results(self):
        return self.data['result']

    def set_results(self, results):
        self.data['result'] = results



