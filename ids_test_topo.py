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

MAC_IP_FILE = 'config/mac_ip_full.txt'
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

        self.main_switch = None
        self.int_routers = dict()
        self.ext_routers = dict()
        self.int_hosts = list()
        self.ext_hosts = list()
        self.int_switches = dict()
        self.ext_switches = dict()

        super(IDSTestFramework, self).__init__()

    def build(self, **_opts):
        "Build hook for Topo class"

        # Get IP and MAC address data
        mac_ip_set = self.read_mac_ip_file(MAC_IP_FILE)
        self.int_mac_ip, self.ext_mac_ip = self.split_mac_ip(
            mac_ip_set, '^192.168')
        self.ext_mac_ip_dict = self.aggregate_mac_ip(self.ext_mac_ip)

        print 'Int net length: %i' % len(self.int_mac_ip)
        print 'Ext net length: %i' % len(self.ext_mac_ip_dict)

        # Create network topology
        self.__create_main_switch()
        self.create_internal_network(self.main_switch, self.int_mac_ip)
        self.create_external_network(self.main_switch, self.ext_mac_ip_dict)

    def __create_main_switch(self):
        main_switch = self.addSwitch('s0')
        self.main_switch = main_switch

    # Generate internal network
    def create_internal_network(self,
                                main_switch,
                                mac_ip_set,
                                package=internal_network):
        "Module loader for internal network generator"

        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

            module = importer.find_module(modname).load_module(modname)
            topo_name, topo_class = self.__load_class(module)

            int_topo = topo_class()
            self.int_topo_class = int_topo

            try:
                hosts, switches, routers = int_topo.create_topo(
                    self, main_switch, mac_ip_set)
                self.int_hosts, self.int_switches, self.int_routers = hosts, switches, routers
            except TypeError as e:
                traceback.print_exc()
                print '%s must have create_topo(topo, mac_ip_set) method' % topo_name

        print '\n%s generated with:\n' % topo_name
        print 'HOSTS: %s' % str(self.int_hosts)
        print 'SWITCHES: %s\n' % str(self.int_switches)
        print 'ROUTERS: %s\n' % str(self.int_routers)

    # Generate test network
    def create_external_network(self,
                                main_switch,
                                ext_mac_set,
                                package=external_network):
        "Module loader for external network generator"

        offset = len(self.int_switches)

        for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

            module = importer.find_module(modname).load_module(modname)
            topo_name, topo_class = self.__load_class(module)

            ext_topo = topo_class()
            self.ext_topo_class = ext_topo

            try:
                hosts, switches, routers = ext_topo.create_topo(
                    self, main_switch, ext_mac_set, offset)
                self.ext_hosts, self.ext_switches, self.ext_routers = hosts, switches, routers
            except TypeError:
                traceback.print_exc()
                print '%s must have create_topo(Mininet, mac_ip_set, offset, switches, test_hosts, test_switches) method' % topo_name

        print '\n%s generated with:\n' % topo_name
        print 'HOSTS: %s' % str(self.ext_hosts)
        print 'SWITCHES: %s\n' % str(self.ext_switches)
        print 'ROUTERS: %s\n' % str(self.ext_routers)

    # def generate_ip_aliases(self, hosts):
    #     print 'Generate Aliases'
    #     offset = len(self.int_switches)
    #     self.ext_topo_class().generate_ip_aliases(hosts, self.ext_mac_ip_dict, offset)

    # def configure_routers(net):
    #     "Set subnet to interface routing of internal hosts"

    #     routers = dict(int_routers, **ext_routers)

    #     for key in routers:
    #         router_name = routers[key].name
    #         for network_addr, dest_router in routers.iteritems():
    #             info()

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
                self.generate_background_traffic(BACKGROUND_HOSTS, targets,
                                                 8000, 'sample1.txt')
                # test_class().run_test(targets, BACKGROUND_HOSTS)
            except TypeError:
                print 'Error. %s must have run_test(targets) method' % (
                    test_name)

    def log_target_hosts(self, net):
        targets_file = open(TARGET_HOSTS_FILE, 'w+')
        targets_arr = list()

        for i in range(len(self.int_hosts)):
            host_name = 'h%i' % i
            host = net.get(host_name)
            ipaddr = host.cmd('hostname -I')

            switch_num = int(self.int_switches[host_name][1:])

            targets_arr.append(ipaddr.rstrip())
            targets_file.write('%i_%i_%s' % (i, switch_num, ipaddr))

        return targets_arr

    def log_attack_hosts(self):
        attack_file = open(ATTACK_HOSTS_FILE, 'w+')
        attack_hosts_arr = list()

        offset = len(self.int_switches) + len(self.ext_switches)
        for i in range(offset, len(self.ext_hosts) + offset - 1):
            host = net.get('h' + str(i))
            switch = net.get('s' + str(i))
            switch.attached
            ipaddr = host.cmd('hostname -I')

            attack_hosts_arr.append(ipaddr.rstrip())
            attack_file.write('%s' % (ipaddr))

        return attack_hosts_arr

    def generate_background_traffic(self, hosts, target_hosts, port, filename):
        for i in range(0, len(target_hosts)):
            ab_cmd = 'ab -c 1 -n 10 http://%s:%s/%s &' % (target_hosts[i],
                                                          port, filename)
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

        # ip_tracker = list()
        mac_ip_set = set()

        with open(filename, 'r') as f:
            p = '\w+:\w+:\w+:\w+:\w+:\w+\s+\d+\.\d+\.\d+\.\d+'
            pairs = re.findall(p, f.read())
            for pair in pairs:
                mac, ip = pair.split()
                # if ip in ip_tracker:
                # continue

                mac_ip_set.add((mac, ip))
                # ip_tracker.append(ip)

        return mac_ip_set

    # Split MAC - IP set
    def split_mac_ip(self, mac_ip_set, int_net_ip_pattern):
        int_mac_ip = list()
        ext_mac_ip = list()

        for pair in mac_ip_set:
            if bool(re.match(int_net_ip_pattern, pair[1])):
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

    # Instantiate IDS Test Framework
    ids_test = IDSTestFramework()
    net = Mininet(topo=ids_test, controller=RemoteController)

    net.start()

    # int_hosts = [net.get(host) for host in ids_test.int_hosts]
    # ids_test.int_topo_class.generate_virtual_mac(int_hosts)

    int_routers = [
        net.get(router.name)
        for key, router in ids_test.int_routers.iteritems()
    ]
    ext_routers = [
        net.get(router.name)
        for key, router in ids_test.ext_routers.iteritems()
    ]
    ids_test.int_topo_class.configure_routers(int_routers,
                                              ids_test.ext_routers)
    ids_test.ext_topo_class.configure_routers(ext_routers,
                                              ids_test.int_routers)

    ext_hosts = [net.get(host) for host in ids_test.ext_hosts]
    ids_test.ext_topo_class.generate_ip_aliases(ext_routers, ext_hosts)

    # Start servers of internal network hosts
    # start_internal_servers('dummy_files', 8000)

    # Execute framework commands
    # log_attack_hosts()
    targets_arr = ids_test.log_target_hosts(net)
    # exec_test_cases(args.test, targets_arr)

    CLI(net)
    net.stop()


if __name__ == "__main__":
    main()
