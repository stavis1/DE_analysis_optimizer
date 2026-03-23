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
        self.quantcols = self.A_cols + self.B_cols
        self.ground_truths = list(options.ground_truths)
        self.protein_metadata = metadata_df
        self.data = df
        self.data.index = self.data['analyte']
        self.data['prob_score'] = [np.nan]*df.shape[0]
        self.data['is_significant'] = [True]*df.shape[0]
        self.observed = self.data[self.quantcols].copy()
        self.observed[self.quantcols] = np.logical_not(np.isfinite(self.observed.to_numpy()))
    
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
        return self.data[self.quantcols].to_numpy()
    
    def set_data(self, data):
        self.data[self.quantcols] = data
    
    def prune(self, to_keep):
        self.data = self.data[to_keep]
        self.observed = self.observed[to_keep]

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
    
    def get_proteins(self):
        return self.data['proteins']

    def get_df(self):
        return self.data
    
    def set_df(self, data):
        self.data = data
        if not 'prob_score' in list(self.data.columns):
            self.data['prob_score'] = [np.nan]*self.data.shape[0]
        if not 'is_significant' in list(self.data.columns):
            self.data['is_significant'] = [True]*self.data.shape[0]
        
    
    def get_observed(self):
        return self.observed.to_numpy()
    
    def get_observed_A(self):
        return self.observed[self.A_cols].to_numpy()

    def get_observed_B(self):
        return self.observed[self.B_cols].to_numpy()
    
    def recalculate_missingness(self):
        self.observed = self.data[self.quantcols].copy()
        vals = self.observed.to_numpy()
        vals = np.logical_not(np.isfinite(vals))
        self.observed[self.quantcols] = vals
        self.observed.index = self.data['analyte']

        
    def get_metadata(self):
        return self.protein_metadata

