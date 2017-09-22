#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class TestCase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def run_test(self):
        pass
    