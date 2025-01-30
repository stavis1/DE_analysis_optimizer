#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 15:10:36 2025

@author: 4vt
"""

import numpy as np

class Data:
    def __init__(self, options, df, metadata_df = None):
        self.history = ''
        self.A_cols = list(options.A)
        self.B_cols = list(options.B)
        self.ground_truths = list(options.ground_truths)
        self.proteins = options.proteins_col
        self.protein_metadata = metadata_df
        self.data = df
        self.data['prob_score'] = [np.nan]*df.shape[0]
        self.data['is_significant'] = [True]*df.shape[0]
    
    def __hash__(self):
        return hash(self.history)
    
    def __eq__(self, o):
        return hash(self.history) == hash(o)
    
    def get_A(self):
        return self.data[self.A_cols].to_numpy()

    def set_A(self, data):
        self.data[self.A_cols] = data

    def get_B(self):
        return self.data[self.B_cols].to_numpy()

    def set_B(self, data):
        self.data[self.B_cols] = data
    
    def get_data(self):
        return self.data[self.A_cols + self.B_cols].to_numpy()
    
    def set_data(self, data):
        self.data[self.A_cols + self.B_cols] = data
    
    def prune(self, to_keep):
        self.data = self.data[to_keep]

    def get_truths(self):
        return self.data[self.ground_truths].to_numpy()
    
    def get_significance(self):
        return self.data['is_significant'].to_numpy()

    def set_significance(self, results):
        self.data['is_significant'] = results

    def get_score(self):
        return self.data['prob_score'].to_numpy()

    def set_score(self, results):
        self.data['prob_score'] = results
    
    def get_protiens(self):
        return self.data[self.proteins]

    def get_df(self):
        return self.df
    
    def set_df(self, data):
        self.data = data
        if not 'prob_score' in list(self.data.columns):
            self.data['prob_score'] = [np.nan]*self.data.shape[0]
        if not 'is_significant' in list(self.data.columns):
            self.data['is_significant'] = [True]*self.data.shape[0]
    
    def get_metadata(self):
        return self.protein_metadata

