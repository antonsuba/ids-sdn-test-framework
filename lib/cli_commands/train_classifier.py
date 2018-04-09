#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import inspect
from ml_ids import ids_classifier


class TrainClassifierCommand(object):
    "Command driver for training IDS classifiers"

    trigger = 'train'

    def run(self, args):
        if args:
            print 'No available command args for "train"'
            return

        ids_classifier.main()
