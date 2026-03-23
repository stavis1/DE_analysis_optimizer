#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 14:55:47 2025

@author: 4vt
"""

import pandas as pd
import numpy as np
import warnings

class Step():
    def __init__(self):
        self.name = NotImplemented

    def process(self, data):
        data.history += self.name
        return data

class BaseSummedAbundance(Step):
    def sum_abundance(self, data):
        df = data.get_df()
        metadata = data.get_metadata()
        metadata.index = metadata['proteins']
        del metadata['proteins']
        metadata_cols = list(metadata.columns)
        quantcols = list(data.A_cols) + list(data.B_cols)
        proteins = df[['proteins'] + quantcols].groupby('proteins').sum()
        proteins = proteins.merge(metadata, 
                                  how = 'left',
                                  left_index = True,
                                  right_index = True)
        proteins.columns = quantcols + metadata_cols
        proteins['analyte'] = proteins.index
        data.set_df(proteins)
        return data


class Noop(Step):
    def __init__(self):
        self.name = 'noop'
    
    def process(self, data):
        data = super().process(data)
        return data

# =============================================================================
# protein rollup choices
# =============================================================================

class UniqueSummedAbundance(BaseSummedAbundance):
    def __init__(self):
        self.name = 'unique_summed_abundance'
    
    def process(self, data):
        data = super().process(data)
        good_peps = [';' not in pr for pr in data.get_proteins()]
        data.prune(good_peps)
        data = self.sum_abundance(data)
        return data
        
class AllSummedAbundance(BaseSummedAbundance):
    def __init__(self):
        self.name = 'all_summed_abundance'
    
    def process(self, data):
        from copy import copy
        
        data = super().process(data)
        df = data.get_df()
        dup_rows = []
        nonunique = [';' in pr for pr in data.get_proteins()]
        for _, row in df[nonunique].iterrows():
            prots = row['proteins'].split(';')
            for prot in prots:
                newrow = copy(row)
                newrow['proteins'] = prot
                dup_rows.append(newrow)
        df = df[[';' not in pr for pr in data.get_proteins()]]
        df = pd.concat([df] + dup_rows)
        data.set_df(df)
        data = self.sum_abundance(data)
        return data

# =============================================================================
# normalization choices
# =============================================================================

class MeanCenter(Step):
    def __init__(self):
        self.name = 'mean_centering'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_data()
        means = np.nanmean(vals, axis = 0)
        grand_mean = np.nanmean(vals)
        vals = (vals/means[np.newaxis, :])*grand_mean
        data.set_data(vals)
        return data

class LogMeanCenter(Step):
    def __init__(self):
        self.name = 'log_mean_centering'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_data()
        vals = np.log(vals)
        means = np.nanmean(vals, axis = 0)
        grand_mean = np.nanmean(vals)
        vals = (vals/means[np.newaxis, :])*grand_mean
        vals = np.exp(vals)
        data.set_data(vals)
        return data

class MedianCenter(Step):
    def __init__(self):
        self.name = 'median_centering'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_data()
        medians = np.nanmean(vals, axis = 0)
        grand_median = np.nanmedian(vals)
        vals = (vals/medians[np.newaxis, :])*grand_median
        data.set_data(vals)
        return data

class LogMedianCenter(Step):
    def __init__(self):
        self.name = 'log_median_centering'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_data()
        vals = np.log(vals)
        medians = np.nanmean(vals, axis = 0)
        grand_median = np.nanmedian(vals)
        vals = (vals/medians[np.newaxis, :])*grand_median
        vals = np.exp(vals)
        data.set_data(vals)
        return data

class QuantileNorm(Step):
    def __init__(self):
        self.name = 'quantile_norm'
    
    def process(self, data):
        from sortedcontainers import SortedList
        
        data = super().process(data)
        vals = data.get_data()
        allvals = vals.flatten()
        newvals = []
        for i in range(vals.shape[0]):
            idx = SortedList(vals[i,np.isfinite(vals[i,:])])
            nvals = len(idx)
            newvals.append([idx.index(i)/nvals if np.isfinite(i) else np.nan for i in vals[i,:]])
        vals = np.array(newvals)



# =============================================================================
# imputation choices
# =============================================================================
class ZeroFill(Step):
    def __init__(self):
        self.name = 'zero_fill'
    
    def process(self, data):
        data = super().process(data)
        #replace missing values with zero
        vals = data.get_data()
        vals[np.logical_not(np.isfinite(vals))] = 0
        data.set_data(vals)
        return data

# =============================================================================
# statsitical test choices
# =============================================================================
class StudentT(Step):
    def __init__(self):
        self.name = 'student_t'
    
    def process(self, data):
        data = super().process(data)
        #run a student's t-test
        from scipy.stats import ttest_ind
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results = ttest_ind(data.get_A(),
                                data.get_B(),
                                equal_var = True,
                                nan_policy = 'omit',
                                axis = 1)
        data.set_score(results.pvalue)
        return data

# =============================================================================
# multiplicity correction choices
# =============================================================================
class Bonferroni(Step):
    def __init__(self):
        self.name = 'bonferroni'
    
    def process(self, data):
        data = super().process(data)
        pvals = data.get_score()
        pvals = pvals/len(pvals)
        significant = pvals < 0.05
        data.set_significance(significant)
        return data

# =============================================================================
# effect size filter choices
# =============================================================================
class Min2FC(Step):
    def __init__(self):
        self.name = 'min_FC_2'
    
    def process(self, data):
        data = super().process(data)
        mean_A = np.nanmean(data.get_A(), axis = 1)
        mean_B = np.nanmean(data.get_B(), axis = 1)
        l2fc = np.log2(mean_A/mean_B)
        valid = l2fc >= np.log2(2)
        significant = data.get_significance()
        significant = np.logical_and(significant, valid)
        data.set_significance(significant)
        return data


# =============================================================================
# rules-based filter choices
# =============================================================================
class MinValid50(Step):
    def __init__(self):
        self.name = '50_valid'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_data()
        n_missing = np.sum(np.logical_not(np.isfinite(vals)), axis = 1)
        valid = (n_missing/vals.shape[1]) > 0.5
        significant = data.get_significance()
        significant = np.logical_and(significant, valid)
        data.set_significance(significant)
        return data

class MinValid50PerCond(Step):
    def __init__(self):
        self.name = '50_valid_per_cond'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_A()
        n_missing = np.sum(np.logical_not(np.isfinite(vals)), axis = 1)
        valid = (n_missing/vals.shape[1]) > 0.5

        vals = data.get_B()
        n_missing = np.sum(np.logical_not(np.isfinite(vals)), axis = 1)
        valid = np.logical_and((n_missing/vals.shape[1]) > 0.5, valid)

        significant = data.get_significance()
        significant = np.logical_and(significant, valid)
        data.set_significance(significant)
        return data


