#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import inspect
from ml_ids import classifier_validation


class ValidateClassifierCommand(object):
    "Command driver for validating IDS classifiers"

    trigger = 'validate'

    def run(self, args):
        if args:
            print 'No available command args for "validate"'
            return

        classifier_validation.main()
