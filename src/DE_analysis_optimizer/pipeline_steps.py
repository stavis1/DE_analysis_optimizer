#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 14:55:47 2025

@author: 4vt
"""

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
        metadata.index = metadata[data.proteins]
        del metadata[data.proteins]
        quantcols = list(data.A_cols) + list(data.B_cols)
        proteins = df[[data.proteins] + quantcols].groupby(data.proteins).sum()
        proteins = proteins.merge(metadata, 
                                  how = 'left',
                                  left_index = True,
                                  right_index = True)
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
        data = data.prune(good_peps)
        data = self.sum_abundance(data)
        return data
        
class AllSummedAbundance(BaseSummedAbundance):
    def __init__(self):
        self.name = 'unique_summed_abundance'
    
    def process(self, data):
        from copy import copy
        from pandas import pd
        
        data = super().process(data)
        df = data.get_df()
        dup_rows = []
        nonunique = [';' in pr for pr in data.get_proteins()]
        for _, row in df[nonunique].iterrows():
            prots = row[data.proteins].split(';')
            for prot in prots:
                newrow = copy(row)
                newrow[data.proteins] = prot
                dup_rows.append(newrow)
        df = df[[';' not in pr for pr in data.get_proteins]]
        df = pd.concat([df] + dup_rows)
        data.set_df(df)
        data = self.sum_abundance(data)
        return data

# =============================================================================
# normalization choices
# =============================================================================


# =============================================================================
# imputation choices
# =============================================================================


# =============================================================================
# statsitical test choices
# =============================================================================


# =============================================================================
# multiplicity correction choices
# =============================================================================


# =============================================================================
# effect size filter choices
# =============================================================================


# =============================================================================
# rules-based filter choices
# =============================================================================


