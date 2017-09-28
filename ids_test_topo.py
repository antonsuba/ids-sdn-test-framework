#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import imp
import argparse
import sys
import inspect
import pkgutil
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel
import test_cases

#Setup arguments
parser = argparse.ArgumentParser(description='Generates n number of hosts to simulate normal and anomalous attack behaviors')
parser.add_argument('-n', '--hosts', dest='hosts', default=3, type=int, 
                    help='Generates an n number of attack hosts based on the quantity specified (default: 3 hosts')
parser.add_argument('-r', '--ratio', dest='ratio', default=0.1, type=int,
                    help='Anomalous to normal hosts ratio. Generates normal traffic hosts based on ratio specified')
parser.add_argument('-t', '--test', dest='test', default='all', type=str,
                    help='Specify tests (Defaults to all)')
args = parser.parse_args()

net = Mininet(controller=RemoteController, link=TCLink)

HOSTS = list()
SWITCHES = list()

TEST_HOSTS = list()
TEST_SWITCHES = list()

#Generate internal network
def create_network(switches):
    SWITCHES.append(net.addSwitch('s0'))

    for i in range(0, switches):
        SWITCHES.append(net.addSwitch('s'+str(i+1)))
        HOSTS.append(net.addHost('h'+str(i)))

        net.addLink(SWITCHES[0], SWITCHES[i+1], bw=10, delay='10ms')
        net.addLink(HOSTS[i], SWITCHES[i+1], bw=10, delay='10ms')

#Generate test network
def create_test_netowrk(hosts, ratio):
    offset = len(SWITCHES)
    # total_hosts = int(hosts + (hosts * ((1 - ratio) * 10)))
    total_hosts = hosts

    for i in range(0, total_hosts):
        TEST_HOSTS.append(net.addHost('h' + str(i + offset - 1)))
        TEST_SWITCHES.append(net.addSwitch('s' + str(i + offset)))

        net.addLink(SWITCHES[0], TEST_SWITCHES[i], bw=10, delay='10ms')
        net.addLink(TEST_HOSTS[i], TEST_SWITCHES[i], bw=10, delay='10ms')

#Generate hosts directory of internal network
def log_target_hosts():
    targets_file = open('target_hosts.txt', 'w+')
    targets_arr = list()

    for i in range(0, len(HOSTS)):
        host = net.get('h' + str(i))
        ipaddr = host.cmd('hostname -I')
        targets_arr.append(ipaddr)
        targets_file.write('h%s_%s' % (str(i), ipaddr))

    return targets_arr

#Run specified test (Defaults to: all tests)
def exec_test_cases(test, targets, package=test_cases):
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        if modname in test_cases.EXCLUDE:
            continue

        module = importer.find_module(modname).load_module(modname)
        test_name, test_class = load_test_class(module)

        try:
            test_class().run_test(targets, TEST_HOSTS)
        except TypeError:
            print '%s must have run_test(targets) method' % (test_name)

#Load test class given a module
def load_test_class(module):
    for name, obj in inspect.getmembers(module, inspect.isclass):
        return name, obj

setLogLevel('info')

c0 = net.addController()
create_network(3)
create_test_netowrk(args.hosts, args.ratio)

net.start()

#Execute framework commands
targets_arr = log_target_hosts()
exec_test_cases(args.test, targets_arr)

CLI(net)
net.stop()
