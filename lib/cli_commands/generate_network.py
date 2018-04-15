#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import inspect
from network import ids_test_topo  # noqa


class GenerateNetworkCommand(object):
    "Command driver for generating Mininet network"

    trigger = 'createnetwork'
    exec_test_trigger = 'exectest'

    def run(self, args):
        if not args:
            ids_test_topo.main()
            return

        if args[0] != GenerateNetworkCommand.exec_test_trigger:
            print 'Invalid command. Use "exectest" arg to initiate tests'
            return

        tests = []
        if len(args) >= 2:
            tests = args[1:]

        ids_test_topo.main(exec_tests=True, tests=tests)
