#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import imp
import argparse
import sys
import inspect
import pkgutil
import string
import csv
import re
from collections import defaultdict
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel
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

net = Mininet(controller=RemoteController, link=TCLink)

HOSTS = list()
SWITCHES = list()
ROUTERS = list()

BACKGROUND_HOSTS = list()
TEST_SWITCHES = list()

MAC_IP_FILE = 'config/mac_ip.txt'
TARGET_HOSTS_FILE = 'config/target_hosts.txt'
ATTACK_HOSTS_FILE = 'config/attack_hosts.txt'


# Generate internal network
def create_network(mac_ip_set, package=internal_network):
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

        module = importer.find_module(modname).load_module(modname)
        topo_name, topo_class = load_class(module)

        try:
            topo_class().create_topo(mac_ip_set, net, SWITCHES, HOSTS)
        except TypeError:
            print '%s must have create_topo(n, Mininet, switches, hosts) method' % topo_name

    print '\n%s generated with:\n' % topo_name
    print 'HOSTS: %s' % str(HOSTS)
    print 'SWITCHES: %s\n' % str(SWITCHES)


# Generate test network
def create_background_network(ext_mac_list, package=external_network):
    offset = len(SWITCHES)

    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

        module = importer.find_module(modname).load_module(modname)
        topo_name, topo_class = load_class(module)

        try:
            topo_class().create_topo(net, ext_mac_list, offset, SWITCHES,
                                     BACKGROUND_HOSTS, TEST_SWITCHES)
        except TypeError:
            print '%s must have create_topo(Mininet, mac_ip_set, offset, switches, test_hosts, test_switches) method' % topo_name

    print '\n%s generated with:\n' % topo_name
    print 'HOSTS: %s' % str(BACKGROUND_HOSTS)
    print 'SWITCHES: %s\n' % str(TEST_SWITCHES)


def create_router():
    ROUTERS.append(net.addHost('r1', mac='00:00:00:00:01:00'))
    net.addLink(ROUTERS[0], SWITCHES[0])


def configure_router(int_mac_ip, ext_mac_ip, ext_mac_ip_dict=None):
    subnets = set()

    mac_ip = int_mac_ip + ext_mac_ip

    r1 = ROUTERS[0]
    r1.cmd('ifconfig r1-eth0 0')

    for pair in mac_ip:
        subnet = (pair[1].rsplit('.', 1)[:-1])[0] + '.0/24'
        print subnet
        if subnet not in subnets:
            r1.cmd('ip addr add %s brd + dev r1-eth0' % subnet)

    r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")

    for host in BACKGROUND_HOSTS:
        print str(host)
        host.cmd('ip route add default via 192.168.2.0')

    s1 = SWITCHES[0]
    s1.cmd("ovs-ofctl add-flow s1 priority=1,arp,actions=flood")
    s1.cmd(
        "ovs-ofctl add-flow s1 priority=65535,ip,dl_dst=00:00:00:00:01:00,actions=output:1"
    )

    for i in range(0, len(subnets)):
        subnet = subnets.pop()
        s1.cmd(
            "ovs-ofctl add-flow s1 priority=10,ip,nw_dst=%s,actions=output:%i"
            % (subnet, i + 2))


def start_internal_servers(directory, port):
    print '\nStarting internal network hosts servers:'
    for host in HOSTS:
        host.cmd('cd %s' % directory)
        host.cmd('python -m SimpleHTTPServer %s &' % str(port))
        print '%s server started' % str(host)


# Run specified test (Defaults to: all tests)
def exec_test_cases(test, targets, package=test_cases):
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        if modname in test_cases.EXCLUDE:
            continue

        module = importer.find_module(modname).load_module(modname)
        test_name, test_class = load_class(module)

        try:
            print 'Executing %s' % test_name
            generate_background_traffic(BACKGROUND_HOSTS, targets, 8000,
                                        'sample1.txt')
            # test_class().run_test(targets, BACKGROUND_HOSTS)
        except TypeError:
            print 'Error. %s must have run_test(targets) method' % (test_name)


def log_target_hosts():
    targets_file = open(TARGET_HOSTS_FILE, 'w+')
    targets_arr = list()

    for i in range(0, len(HOSTS)):
        host = net.get('h' + str(i))
        ipaddr = host.cmd('hostname -I')

        targets_arr.append(ipaddr.rstrip())
        targets_file.write('%i_%s' % (i + 1, ipaddr))

    return targets_arr


def log_attack_hosts():
    attack_file = open(ATTACK_HOSTS_FILE, 'w+')
    attack_hosts_arr = list()

    offset = len(SWITCHES)
    for i in range(offset, len(BACKGROUND_HOSTS) + offset - 1):
        host = net.get('h' + str(i))
        ipaddr = host.cmd('hostname -I')

        attack_hosts_arr.append(ipaddr.rstrip())
        attack_file.write('%s' % (ipaddr))

    return attack_hosts_arr


def generate_background_traffic(hosts, target_hosts, port, filename):
    for i in range(0, len(target_hosts)):
        ab_cmd = 'ab -c 1 -n 10 http://%s:%s/%s &' % (target_hosts[i], port,
                                                      filename)
        print 'Executing ab command: %s' % ab_cmd
        result = hosts[i].cmd(ab_cmd)


# Load class given a module
def load_class(module):
    for name, obj in inspect.getmembers(module, inspect.isclass):
        return name, obj


# Read file then append to list
def read_data_file(filename):
    data_list = list()

    f = open(filename, 'r')
    for line in f:
        data_list.append(line.rstrip())
    f.close()

    return data_list


# Generate set of MAC - IP pairs from file
def read_mac_ip_file(filename):

    mac_ip_set = set()

    with open(filename, 'r') as f:
        p = '\w+:\w+:\w+:\w+:\w+:\w+\s\d+\.\d+\.\d+\.\d+'
        pairs = re.findall(p, f.read())
        for pair in pairs:
            mac, ip = pair.split()
            mac_ip_set.add((mac, ip))

    return mac_ip_set


# Split MAC - IP set
def split_mac_ip(mac_ip_set, int_net_ip_pattern):
    int_mac_ip = list()
    ext_mac_ip = list()

    for pair in mac_ip_set:
        if int_net_ip_pattern in pair[1]:
            int_mac_ip.append(pair)
        else:
            ext_mac_ip.append(pair)

    return int_mac_ip, ext_mac_ip


# Generate dictionary with MAC as key and set of IP as value
def aggregate_mac_ip(mac_ip_set):
    mac_ips = defaultdict(set)

    for pair in mac_ip_set:
        mac_address, ip = pair[0], pair[1]
        mac_ips[mac_address] |= set([ip])

    return mac_ips


def main():
    setLogLevel('info')

    # Create remote controller
    c0 = net.addController()

    # Get IP and MAC address data
    mac_ip_set = read_mac_ip_file(MAC_IP_FILE)
    int_mac_ip, ext_mac_ip = split_mac_ip(mac_ip_set, '192.168')
    ext_mac_ip_dict = aggregate_mac_ip(ext_mac_ip)

    print 'Int net length: %i' % len(int_mac_ip)
    print 'Ext net length: %i' % len(ext_mac_ip_dict)

    #Create network topology
    create_network(int_mac_ip)
    create_background_network(ext_mac_ip_dict)
    create_router()

    net.start()

    # Link subnets to router
    configure_router(int_mac_ip, ext_mac_ip, ext_mac_ip_dict)

    # Start servers of internal network hosts
    # start_internal_servers('dummy_files', 8000)

    # Execute framework commands
    # log_attack_hosts()
    targets_arr = log_target_hosts()
    # exec_test_cases(args.test, targets_arr)

    CLI(net)
    net.stop()


if __name__ == "__main__":
    main()
