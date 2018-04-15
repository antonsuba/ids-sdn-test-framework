#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import inspect
from importlib import import_module

DIRNAME = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
CONFIG = os.path.join(DIRNAME, '../../config/config.yml')
with open(CONFIG, 'r') as config_file:
    cfg = yaml.load(config_file).get('cli')


class ValidateClassifierCommand(object):
    "Command driver for validating IDS classifiers"

    trigger = 'validate'

    def run(self, args):
        if args:
            print 'No available command args for "validate"'
            return

        validation_module = import_module(
            'ml_ids.%s' % cfg['validation-module'])
        validation_module.main()
