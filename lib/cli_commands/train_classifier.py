#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import inspect

DIRNAME = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
sys.path.insert(0, os.path.join(DIRNAME, '../'))
from ml_ids import ids_classifier

class TrainClassifierCommand(object):
    "Command driver for training IDS classifiers"

    trigger = 'train'

    def run(self, args):
        if args:
            print 'No available command args for "train"'
            return

        ids_classifier.main()
