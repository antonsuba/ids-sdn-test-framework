#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import imp
import argparse
import sys
import inspect
import pkgutil
import re
import traceback
from collections import defaultdict
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel, info
from mininet.topo import Topo
from mininet.node import Node
import internal_network
import external_network
import test_cases

# Setup arguments
parser = argparse.ArgumentParser(
    description=
    'Generates n number of hosts to simulate normal and anomalous attack behaviors'
)
parser.add_argument(
    '-n',
    '--hosts',
    dest='hosts',
    default=3,
    type=int,
    help=
    'Generates an n number of attack hosts based on the quantity specified (default: 3 hosts'
)
parser.add_argument(
    '-r',
    '--ratio',
    dest='ratio',
    default=0.1,
    type=int,
    help=
    'Anomalous to normal hosts ratio. Generates normal traffic hosts based on ratio specified'
)
parser.add_argument(
    '-t',
    '--test',
    dest='test',
    default='all',
    type=str,
    help='Specify tests (Defaults to all)')
args = parser.parse_args()

HOSTS = list()
SWITCHES = list()

BACKGROUND_HOSTS = list()
TEST_SWITCHES = list()

MAC_IP_FILE = 'config/mac_ip.txt'
TARGET_HOSTS_FILE = 'config/target_hosts.txt'
ATTACK_HOSTS_FILE = 'config/attack_hosts.txt'


class IDSTestFramework(Topo):
    "IDS Testing Framework Main Class"


    def __init__(self):
        print 'IDS Testing Started'

        self.int_topo_class = None
        self.ext_topo_class = None
        
        self.int_mac_ip = None
        self.ext_mac_ip = None
        self.ext_mac_ip_dict = None

        self.main_node = None

        self.int_hosts = list()
        self.ext_hosts = list()
        self.int_switches = list()
        self.ext_switches = list()

        super(IDSTestFramework, self).__init__()


    def build(self, **_opts):
        # router_ip = '192.168.1.1'

        # Get IP and MAC address data
        mac_ip_set = self.read_mac_ip_file(MAC_IP_FILE)
        self.int_mac_ip, self.ext_mac_ip = self.split_mac_ip(mac_ip_set, '192.168')
        self.ext_mac_ip_dict = self.aggregate_mac_ip(self.ext_mac_ip)

        print 'Int net length: %i' % len(self.int_mac_ip)
        print 'Ext net length: %i' % len(self.ext_mac_ip_dict)

        #Create network topology
        # self.create_router(int_mac_ip[0][1])
        self.create_internal_network(self.int_mac_ip)
        self.create_external_network(self.ext_mac_ip_dict)


    # Generate internal network
    def create_internal_network(self, mac_ip_set, package=internal_network):
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

            module = importer.find_module(modname).load_module(modname)
            topo_name, topo_class = self.__load_class(module)

            self.int_topo_class = topo_class

            try:
                self.int_hosts, self.int_switches, self.main_node = topo_class().create_topo(self, mac_ip_set)
            except TypeError as e:
                traceback.print_exc()
                print '%s must have create_topo(mac_ip_set, topo) method' % topo_name

        print '\n%s generated with:\n' % topo_name
        print 'HOSTS: %s' % str(self.int_hosts)
        print 'SWITCHES: %s\n' % str(self.int_switches)


    # Generate test network
    def create_external_network(self, ext_mac_set, package=external_network):
        offset = len(self.int_switches)

        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

            module = importer.find_module(modname).load_module(modname)
            topo_name, topo_class = self.__load_class(module)

            self.ext_topo_class = topo_class

            try:
                self.ext_hosts, self.ext_switches = topo_class().create_topo(self, ext_mac_set,
                                                                             offset, self.main_node)
                print 'External Hosts'
            except TypeError:
                print '%s must have create_topo(Mininet, mac_ip_set, offset, switches, test_hosts, test_switches) method' % topo_name

        print '\n%s generated with:\n' % topo_name
        print 'HOSTS: %s' % str(self.ext_hosts)
        print 'SWITCHES: %s\n' % str(self.ext_switches)


    def generate_ip_aliases(self, hosts):
        print 'Generate Aliases'
        offset = len(self.int_switches)
        self.ext_topo_class().generate_ip_aliases(hosts, self.ext_mac_ip_dict, offset)


    def configure_router(self, router):
        print 'Configuring Router'
        offset = len(self.int_switches)        
        self.int_topo_class().configure_router(router, self.int_mac_ip)
        self.ext_topo_class().configure_router(router, self.ext_mac_ip_dict, offset)


    def start_internal_servers(self, directory, port):
        print '\nStarting internal network hosts servers:'
        for host in self.ext_hosts:
            host.cmd('cd %s' % directory)
            host.cmd('python -m SimpleHTTPServer %s &' % str(port))
            print '%s server started' % str(host)


    # Run specified test (Defaults to: all tests)
    def exec_test_cases(self, test, targets, package=test_cases):
        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
            if modname in test_cases.EXCLUDE:
                continue

            module = importer.find_module(modname).load_module(modname)
            test_name, test_class = self.__load_class(module)

            try:
                print 'Executing %s' % test_name
                self.generate_background_traffic(BACKGROUND_HOSTS, targets, 8000,
                                                 'sample1.txt')
                # test_class().run_test(targets, BACKGROUND_HOSTS)
            except TypeError:
                print 'Error. %s must have run_test(targets) method' % (test_name)


    # def log_target_hosts(self):
    #     targets_file = open(TARGET_HOSTS_FILE, 'w+')
    #     targets_arr = list()

    #     for i in range(0, len(HOSTS)):
    #         host = net.get('h' + str(i))
    #         ipaddr = host.cmd('hostname -I')

    #         targets_arr.append(ipaddr.rstrip())
    #         targets_file.write('%i_%s' % (i + 1, ipaddr))

    #     return targets_arr


    # def log_attack_hosts(self):
    #     attack_file = open(ATTACK_HOSTS_FILE, 'w+')
    #     attack_hosts_arr = list()

    #     offset = len(SWITCHES)
    #     for i in range(offset, len(BACKGROUND_HOSTS) + offset - 1):
    #         host = net.get('h' + str(i))
    #         ipaddr = host.cmd('hostname -I')

    #         attack_hosts_arr.append(ipaddr.rstrip())
    #         attack_file.write('%s' % (ipaddr))

    #     return attack_hosts_arr


    def generate_background_traffic(self, hosts, target_hosts, port, filename):
        for i in range(0, len(target_hosts)):
            ab_cmd = 'ab -c 1 -n 10 http://%s:%s/%s &' % (target_hosts[i], port, filename)
            print 'Executing ab command: %s' % ab_cmd
            info(hosts[i].cmd(ab_cmd))


    # Load class given a module
    def __load_class(self, module):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            return name, obj


    # Read file then append to list
    def read_data_file(self, filename):
        data_list = list()

        f = open(filename, 'r')
        for line in f:
            data_list.append(line.rstrip())
        f.close()

        return data_list


    # Generate set of MAC - IP pairs from file
    def read_mac_ip_file(self, filename):

        mac_ip_set = set()

        with open(filename, 'r') as f:
            p = '\w+:\w+:\w+:\w+:\w+:\w+\s\d+\.\d+\.\d+\.\d+'
            pairs = re.findall(p, f.read())
            for pair in pairs:
                mac, ip = pair.split()
                mac_ip_set.add((mac, ip))

        return mac_ip_set


    # Split MAC - IP set
    def split_mac_ip(self, mac_ip_set, int_net_ip_pattern):
        int_mac_ip = list()
        ext_mac_ip = list()

        for pair in mac_ip_set:
            if int_net_ip_pattern in pair[1]:
                int_mac_ip.append(pair)
            else:
                ext_mac_ip.append(pair)

        return int_mac_ip, ext_mac_ip


    # Generate dictionary with MAC as key and set of IP as value
    def aggregate_mac_ip(self, mac_ip_set):
        mac_ips = defaultdict(set)

        for pair in mac_ip_set:
            mac_address, ip = pair[0], pair[1]
            mac_ips[mac_address] |= set([ip])

        return mac_ips


def main():
    setLogLevel('info')

    #Instantiate IDS Test Framework
    ids_test = IDSTestFramework()
    net = Mininet(topo=ids_test, controller=RemoteController)

    net.start()

    ext_hosts = [net.get(host) for host in ids_test.ext_hosts]
    ids_test.generate_ip_aliases(ext_hosts)

    router = net.get('r0')
    ids_test.configure_router(router)

    # Start servers of internal network hosts
    # start_internal_servers('dummy_files', 8000)

    # Execute framework commands
    # log_attack_hosts()
    # targets_arr = ids_test.log_target_hosts()
    # exec_test_cases(args.test, targets_arr)

    CLI(net)
    net.stop()


if __name__ == "__main__":
    main()
