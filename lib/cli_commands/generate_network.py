#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import inspect

DIRNAME = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
sys.path.insert(0, os.path.join(DIRNAME, '../'))
from network import ids_test_topo

class GenerateNetworkCommand(object):
    "Command driver for generating Mininet network"

    trigger = 'createnetwork'

    def run(self):
        print 'Hello'
