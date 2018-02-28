#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import inspect

DIRNAME = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
sys.path.insert(0, os.path.join(DIRNAME, '../'))
from ml_ids import classifier_validation

class ValidateClassifierCommand(object):
    "Command driver for validating IDS classifiers"

    trigger = 'validate'

    def run(self, args):
        if args:
            print 'No available command args for "validate"'
            return

        classifier_validation.main()
