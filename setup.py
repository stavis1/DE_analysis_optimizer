#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 14:06:33 2024

@author: anon
"""

import setuptools

setuptools.setup(name="DE_analysis_optimizer",
                 version="0.0.0",
                 url="https://github.com/stavis1/DE_analysis_optimizer",
                 author="Steven Tavis",
                 author_email="stavis@vols.utk.edu",
                 package_dir={"": "src"},
                 packages=setuptools.find_namespace_packages(where="src"),
                 include_package_data=True,
                 license_files=['LICENSE'],
                 classifiers=['Programming Language :: Python :: 3.11'],
                 python_requires='==3.11.9')
