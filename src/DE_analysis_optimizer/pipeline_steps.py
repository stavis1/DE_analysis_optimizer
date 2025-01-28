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


class Noop(Step):
    def __init__(self):
        self.name = 'noop'
    
    def process(self, data):
        return data
