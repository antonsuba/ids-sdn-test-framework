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


class TrainClassifierCommand(object):
    "Command driver for training IDS classifiers"

    trigger = 'train'

    def run(self, args):
        if args:
            print 'No available command args for "train"'
            return

        training_module = import_module('ml_ids.%s' % cfg['training-module'])
        training_module.main()
