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
    exec_test_trigger = 'exectest'

    def run(self, args):
        if args[0] and args[0] == GenerateNetworkCommand.exec_test_trigger:
            print 'Invalid command arg. Use "exectest" to initiate testing'
            return

        ids_test_topo.main(args[0], args[1])
