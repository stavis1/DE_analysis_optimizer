#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 14:55:47 2025

@author: 4vt
"""

import pandas as pd
import numpy as np

class Step():
    def __init__(self, options):
        self.name = NotImplemented
        self.options = options

    def process(self, data):
        data.history += self.name
        return data

class BaseAbundance(Step):
    def duplicate_nonunique(self, data):
        from copy import copy

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
        return data 
    
    def process_abundance(self, data):
        #collect necessary data
        df = data.get_df()
        metadata = data.get_metadata()
        metadata.index = metadata['proteins']
        del metadata['proteins']
        metadata_cols = list(metadata.columns)
        quantcols = list(data.A_cols) + list(data.B_cols)
        
        #merge by proteins
        proteins = df.groupby('proteins')[quantcols].apply(self.rollup_func)
        proteins.columns = quantcols
        proteins = proteins.merge(metadata, 
                                  how = 'left',
                                  left_index = True,
                                  right_index = True)
        proteins.columns = quantcols + metadata_cols
        proteins['analyte'] = proteins.index
        data.set_df(proteins)
        data.recalculate_missingness()
        return data

class BaseFilter(Step):
    def significance_filter(self, data, valid):
        #update significance
        significant = data.get_significance()
        significant = np.logical_and(significant, valid)
        data.set_significance(significant)
        
        #update scores
        scores = data.get_score()
        scores[np.logical_not(valid)] = 1
        data.set_score(scores)
        return data

class Noop(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'noop'
    
    def process(self, data):
        data = super().process(data)
        return data

# =============================================================================
# peptide filter choices
# =============================================================================

class UniquePeptides(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'unique_peptides'
    
    def process(self, data):
        data = super().process(data)
        good_peps = [';' not in pr for pr in data.get_proteins()]
        data.prune(good_peps)
        return data

# =============================================================================
# protein rollup choices
# =============================================================================

class SummedAbundance(BaseAbundance):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'summed_abundance'
    
    def rollup_func(self, rows, *args, **kwargs):
        return pd.Series(np.nansum(rows, axis = 0))
    
    def process(self, data):        
        data = super().process(data)
        data = self.duplicate_nonunique(data)
        data = self.process_abundance(data)
        return data

class MeanAbundance(BaseAbundance):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'mean_abundance'
    
    def rollup_func(self, rows, *args, **kwargs):
        return pd.Series(np.nanmean(rows, axis = 0))
    
    def process(self, data):        
        data = super().process(data)
        data = self.duplicate_nonunique(data)
        data = self.process_abundance(data)
        return data

class MeanZScore(BaseAbundance):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'mean_z_score'
    
    def rollup_func(self, rows, *args, **kwargs):
        return pd.Series(np.nanmean(rows, axis = 0))
    
    def process(self, data):        
        data = super().process(data)

        vals = data.get_data()
        means = np.nanmean(vals, axis = 1)
        stds = np.nanstd(vals, axis = 1)
        vals = (vals - means[:, np.newaxis])/stds[:, np.newaxis]
        data.set_data(vals)

        data = self.duplicate_nonunique(data)
        data = self.process_abundance(data)
        return data
    
class MedianAbundance(BaseAbundance):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'median_abundance'
    
    def rollup_func(self, rows, *args, **kwargs):
        return pd.Series(np.nanmedian(rows, axis = 0))
    
    def process(self, data):        
        data = super().process(data)
        data = self.duplicate_nonunique(data)
        data = self.process_abundance(data)
        return data

# =============================================================================
# normalization choices
# =============================================================================

class MeanCenter(Step):
    def __init__(self, *args):
        super().__init__(*args)
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
    def __init__(self, *args):
        super().__init__(*args)
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
    def __init__(self, *args):
        super().__init__(*args)
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
    def __init__(self, *args):
        super().__init__(*args)
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
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'quantile_norm'
    
    def process(self, data):
        from sklearn.preprocessing import quantile_transform
        data = super().process(data)
        vals = data.get_data()
        allvals = vals.flatten()
        allvals = allvals[np.isfinite(allvals)]
        vals = quantile_transform(vals, n_quantiles = vals.shape[0])
        mask = np.isfinite(vals)
        vals[mask] = np.nanquantile(allvals, vals[mask])
        data.set_data(vals)
        return data        

# =============================================================================
# imputation choices
# =============================================================================
class ZeroFill(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'zero_fill'
    
    def process(self, data):
        data = super().process(data)
        #replace missing values with zero
        vals = data.get_data()
        vals[np.logical_not(np.isfinite(vals))] = 0
        data.set_data(vals)
        return data

class Perseus(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'perseus'
    
    def process(self, data):
        data = super().process(data)
        #transform
        vals = data.get_data()
        vals = np.log2(vals)
        
        #calculate RNG parameters
        mean = np.nanmean(vals)
        std = np.nanstd(vals)
        impute_mean = mean - (1.8*std)
        impute_std = std*0.3
        
        #impute
        mask = np.logical_not(np.isfinite(vals))
        vals[mask] = self.options.rng.normal(impute_mean, impute_std, vals.shape)[mask]
        
        #back-transform
        vals = np.exp2(vals)
        data.set_data(vals)
        return data

class KNN(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'KNN_impute'
    
    def process(self, data):
        data = super().process(data)
        from sklearn.impute import KNNImputer
        vals = data.get_data()
        vals = KNNImputer(keep_empty_features=True).fit_transform(vals.T).T
        data.set_data(vals)
        return data

class MeanImpute(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'mean_impute'
    
    def process(self, data):
        data = super().process(data)
        from sklearn.impute import SimpleImputer
        vals = data.get_data()
        vals = SimpleImputer(strategy='mean', keep_empty_features=True).fit_transform(vals.T).T
        data.set_data(vals)
        return data

# =============================================================================
# statsitical test choices
# =============================================================================
class no_test(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'no_test'
    
    def process(self, data):
        data = super().process(data)
        data.set_score([0]*data.get_df().shape[0])
        return data
    
class Bootstrap(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'bootstrap'
    
    def process(self, data):
        A = data.get_A()
        B = data.get_B()

        def l2fc(a, b):
            return np.log2(np.nanmean(a, axis = 1)/np.nanmean(b, axis = 1))

        observed = l2fc(A, B)

        resamps = 10000
        def sample(a, b):
            N_a = a.shape[1]
            vals = np.concatenate((a, b), axis = 1)
            vals = self.options.rng.choice(vals, (vals.shape[1], resamps), axis = 1)
            a = vals[:, :N_a, :]
            b = vals[:, N_a:, :]
            fc = np.abs(l2fc(a, b))
            lesser = np.sum(np.abs(observed[:, np.newaxis]) <= fc, axis = 1)
            pvals = (lesser + 1)/(resamps  + 1)
            return pvals

        pvals = sample(A, B)
        data.set_score(pvals)
        return data


class StudentT(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'student_t'
    
    def process(self, data):
        data = super().process(data)
        #run a student's t-test
        from scipy.stats import ttest_ind
        results = ttest_ind(data.get_A(),
                            data.get_B(),
                            equal_var = True,
                            nan_policy = 'omit',
                            axis = 1)
        data.set_score(results.pvalue)
        return data

class WelchT(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'welch_t'
    
    def process(self, data):
        data = super().process(data)
        #run a student's t-test
        from scipy.stats import ttest_ind
        results = ttest_ind(data.get_A(),
                            data.get_B(),
                            equal_var = False,
                            nan_policy = 'omit',
                            axis = 1)
        data.set_score(results.pvalue)
        return data

class LogStudentT(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'log_student_t'
    
    def process(self, data):
        data = super().process(data)
        #run a student's t-test
        from scipy.stats import ttest_ind
        results = ttest_ind(np.log2(data.get_A()),
                            np.log2(data.get_B()),
                            equal_var = True,
                            nan_policy = 'omit',
                            axis = 1)
        data.set_score(results.pvalue)
        return data

class LogWelchT(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'log_welch_t'
    
    def process(self, data):
        data = super().process(data)
        #run a student's t-test
        from scipy.stats import ttest_ind
        results = ttest_ind(np.log2(data.get_A()),
                            np.log2(data.get_B()),
                            equal_var = False,
                            nan_policy = 'omit',
                            axis = 1)
        data.set_score(results.pvalue)
        return data

class MannWhitneyU(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'man_whitney_u'
    
    def process(self, data):
        data = super().process(data)
        #run a student's t-test
        from scipy.stats import mannwhitneyu
        results = mannwhitneyu(data.get_A(),
                               data.get_B(),
                               nan_policy = 'omit',
                               axis = 1)
        data.set_score(results.pvalue)
        return data

class MinEffectTest(Step):
    def process(self, data):
        data = super().process(data)
        from statsmodels.stats.weightstats import ttost_ind
        A = data.get_A()
        B = data.get_B()
        mean_B = np.nanmean(B, axis = 1)
        lower_bound = -(mean_B/self.fc_bound)
        upper_bound = mean_B*self.fc_bound - mean_B
        
        def tost(a, b, lb, ub):
            a = a[np.isfinite(a)]
            b = b[np.isfinite(b)]
            results = ttost_ind(x1 = a, 
                                x2 = b, 
                                low = lb, 
                                upp = ub,
                                usevar = 'unequal')
            pval = np.nanmax((results[1][1], results[2][1]))
            return 1 - pval
        
        pvals = [tost(A[i, :], B[i, :], b[0], b[1]) for i,b in enumerate(zip(lower_bound, upper_bound))]
        data.set_score(pvals)
        return data

class MinEffect1_5(MinEffectTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'minimum_effect_test_1.5FC'
        self.fc_bound = 1.5
        
class MinEffect2(MinEffectTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'minimum_effect_test_2FC'
        self.fc_bound = 2

class BootMinEffectTest(Step):
    def process(self, data):
        A = data.get_A()
        B = data.get_B()
        mean_B = np.nanmean(B, axis = 1)
        lower_bound = -(mean_B/self.fc_bound)
        upper_bound = mean_B*self.fc_bound - mean_B

        def l2fc(a, b):
            return np.log2(np.nanmean(a, axis = 1)/np.nanmean(b, axis = 1))

        observed = l2fc(A, B)

        resamps = 10000
        def sample(a, b, offset, direction):
            N_a = a.shape[1]
            vals = np.concatenate((a, b), axis = 1)
            vals = self.options.rng.choice(vals, (vals.shape[1], resamps), axis = 1)
            a = vals[:, :N_a, :]
            b = vals[:, N_a:, :]
            a = a + offset[:, np.newaxis, np.newaxis]
            fc = l2fc(a, b) * direction
            lesser = np.sum(observed[:, np.newaxis] <= fc, axis = 1)
            pvals = (lesser + 1)/(resamps  + 1)
            return pvals

        plow = sample(A, B, lower_bound, -1)
        phigh = sample(A, B, upper_bound, 1)
        pvals = np.nanmin((plow, phigh), axis = 0)
        data.set_score(pvals)
        return data
    
class BootMinEffect1_5(BootMinEffectTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'bootstrap_minimum_effect_test_1.5FC'
        self.fc_bound = 1.5
        
class BootMinEffect2(BootMinEffectTest):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'bootstrap_minimum_effect_test_2FC'
        self.fc_bound = 2

# =============================================================================
# multiplicity correction choices
# =============================================================================
class NoCorrection(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'no_correction'
    
    def process(self, data):
        data = super().process(data)
        pvals = data.get_score()
        significant = pvals < 0.05
        data.set_significance(significant)
        return data

class Bonferroni(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'bonferroni'
    
    def process(self, data):
        data = super().process(data)
        pvals = data.get_score()
        pvals = np.clip(pvals*len(pvals), a_min = 0, a_max = 1)
        significant = pvals < 0.05
        data.set_significance(significant)
        data.set_score(pvals)
        return data

class FDR(Step):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'fdr'

    def process(self, data):
        from scipy.stats import false_discovery_control
        data = super().process(data)
        pvals = data.get_score()
        mask = np.isfinite(pvals)
        qvals = false_discovery_control(pvals[mask])
        pvals[mask] = qvals
        data.set_significance(pvals < 0.01)
        data.set_score(pvals)
        return data

# =============================================================================
# effect size filter choices
# =============================================================================
class Min2FC(BaseFilter):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'min_FC_2'
    
    def process(self, data):
        data = super().process(data)
        mean_A = np.nanmean(data.get_A(), axis = 1)
        mean_B = np.nanmean(data.get_B(), axis = 1)
        l2fc = np.log2(mean_A/mean_B)
        valid = l2fc >= np.log2(2)
        data = self.significance_filter(data, valid)
        return data

class Min15FC(BaseFilter):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'min_FC_1.5'
    
    def process(self, data):
        data = super().process(data)
        mean_A = np.nanmean(data.get_A(), axis = 1)
        mean_B = np.nanmean(data.get_B(), axis = 1)
        l2fc = np.log2(mean_A/mean_B)
        valid = l2fc >= np.log2(1.5)
        data = self.significance_filter(data, valid)
        return data

# =============================================================================
# rules-based filter choices
# =============================================================================
class MinValid50(BaseFilter):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = '50_valid'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_observed()
        n_missing = np.sum(vals, axis = 1)
        valid = (n_missing/vals.shape[1]) < 0.5
        data = self.significance_filter(data, valid)
        return data

class MinValid50PerCond(BaseFilter):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = '50_valid_per_cond'
    
    def process(self, data):
        data = super().process(data)
        vals = data.get_observed_A()
        n_missing = np.sum(vals, axis = 1)
        valid = (n_missing/vals.shape[1]) < 0.5
        vals = data.get_observed_B()
        n_missing = np.sum(vals, axis = 1)
        valid = np.logical_and((n_missing/vals.shape[1]) < 0.5, valid)
        data = self.significance_filter(data, valid)
        return data

class Min1Unique(BaseFilter):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'min_1_unique'
    
    def process(self, data):
        data = super().process(data)
        df = data.get_df()
        valid = df['N_unique_peptides'] >= 1
        data = self.significance_filter(data, valid)
        return data

class Min1Unique2Total(BaseFilter):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = 'min_1_unique_2_total'
    
    def process(self, data):
        data = super().process(data)
        data = Min1Unique(self.options).process(data)
        df = data.get_df()
        valid = df['N_peptides'] >= 2
        data = self.significance_filter(data, valid)
        return data




