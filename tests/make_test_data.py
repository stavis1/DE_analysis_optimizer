#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 16:34:06 2025

@author: 4vt
"""

import pandas as pd
import numpy as np

#parameters
rng = np.random.default_rng(1)
p = 100
p_prot = 50
N = 3

#make analyte intensity data
#means are lognormally distributed
data = pd.DataFrame({'analyte':[f'peptide{i}' for i in range(p)],
                     'proteins':[f'protein{i%(p_prot)}' for i in range(p)]})
means = np.abs(np.exp2(rng.normal(18, 5, p)))
#apply multiplicative noise
noise = np.abs(rng.normal(1, 0.1, (p,N*2)))
values = noise*means[:, np.newaxis]
#simple missing completely at random model
missingness_prob = rng.uniform(0,1,(p,N*2))
values[missingness_prob < 0.2] = np.nan

#write protein data
data[[f'{c}{i}' for c in 'AB' for i in range(N)]] = values
data.to_csv('data.tsv', sep = '\t')
metadata = pd.DataFrame({'proteins':[f'protein{i}' for i in range(p_prot)],
                         'truth1':[False]*(p_prot//2) + [True]*(p_prot//2),
                         'truth2':rng.choice((True, False), p_prot),
                         'N_peptides':[2]*p_prot,
                         'N_unique_peptides':[2]*p_prot})
metadata.to_csv('metadata.tsv', sep = '\t')

#write lipid data
del data['proteins']
data['truth1'] = [False]*(p//2) + [True]*(p//2)
data['truth2'] = rng.choice((True, False), p)
data.to_csv('lipid_data.tsv', sep = '\t')



