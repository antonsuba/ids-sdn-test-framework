#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import imp
import argparse
import sys
import inspect
import pkgutil
import string
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel
import internal_network
import external_network
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
ROUTERS = list()

BACKGROUND_HOSTS = list()
TEST_SWITCHES = list()

INT_IP_FILE = 'internal_ip_addresses.txt'
EXT_IP_FILE = 'external_ip_addresses.txt'
INT_MAC_FILE = 'internal_mac_addresses.txt'
INT_MAC_FILE = 'external_mac_addresses.txt'

#Temp variables
IP_LIST = ['192.168.1.105', '192.168.2.170', '192.168.5.122', '192.168.9.121']

def read_data_file(filename):
    data_list = list()

    f = open(filename, 'r')
    for line in f:
        data_list.append(line.rstrip())
    f.close()

    return data_list

#Generate internal network
def create_network(switches, package=internal_network):
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

        module = importer.find_module(modname).load_module(modname)
        topo_name, topo_class = load_class(module)

        try:
            topo_class().create_topo(switches, net, SWITCHES, HOSTS)
        except TypeError:
            print '%s must have create_topo(n, Mininet, switches, hosts) method' % topo_name

    print '\n%s generated with:\n' % topo_name
    print 'HOSTS: %s' % str(HOSTS)
    print 'SWITCHES: %s\n' % str(SWITCHES)

#Generate test network
def create_background_network(hosts, ratio, package=external_network):
    offset = len(SWITCHES)
    # total_hosts = int(hosts + (hosts * ((1 - ratio) * 10)))
    total_hosts = hosts

    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):

        module = importer.find_module(modname).load_module(modname)
        topo_name, topo_class = load_class(module)

        try:
            topo_class().create_background_generator(net, total_hosts, offset, SWITCHES,
                                                     BACKGROUND_HOSTS, TEST_SWITCHES)
        except TypeError:
            print '%s must have create_topo(n, Mininet, switches, hosts) method' % topo_name

    print '\n%s generated with:\n' % topo_name
    print 'HOSTS: %s' % str(HOSTS)
    print 'SWITCHES: %s\n' % str(SWITCHES)

def create_router():
    ROUTERS.append(net.addHost('r1', mac='00:00:00:00:01:00'))
    net.addLink(ROUTERS[0], SWITCHES[0])

def configure_router(ip_list):
    r1 = ROUTERS[0]
    r1.cmd('ifconfig r1-eth0 0')
    r1.cmd('ip addr add 192.168.1.0/24 brd + dev r1-eth0')
    r1.cmd('ip addr add 192.168.2.0/24 brd + dev r1-eth0')
    r1.cmd('ip addr add 192.168.3.0/24 brd + dev r1-eth0')
    r1.cmd('ip addr add 192.168.4.0/24 brd + dev r1-eth0')
    r1.cmd('ip addr add 192.168.8.0/20 brd + dev r1-eth0')
    r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")

    all_hosts = HOSTS + BACKGROUND_HOSTS
    print len(ip_list)
    print len(all_hosts)
    for i in range(0, len(ip_list)):
        all_hosts[i].cmd('ip route add default via %s' % ip_list[i])

    s1 = SWITCHES[0]
    s1.cmd("ovs-ofctl add-flow s1 priority=1,arp,actions=flood")
    s1.cmd("ovs-ofctl add-flow s1 priority=65535,ip,dl_dst=00:00:00:00:01:00,actions=output:1")
    s1.cmd("ovs-ofctl add-flow s1 priority=10,ip,nw_dst=192.168.1.0/24,actions=output:2")
    s1.cmd("ovs-ofctl add-flow s1 priority=10,ip,nw_dst=192.168.2.0/24,actions=output:3")
    s1.cmd("ovs-ofctl add-flow s1 priority=10,ip,nw_dst=192.168.3.0/24,actions=output:4")
    s1.cmd("ovs-ofctl add-flow s1 priority=10,ip,nw_dst=192.168.4.0/24,actions=output:5")
    s1.cmd("ovs-ofctl add-flow s1 priority=10,ip,nw_dst=192.168.8.0/20,actions=output:6")

def start_internal_servers(directory, port):
    print '\nStarting internal network hosts servers:'
    for host in HOSTS:
        host.cmd('cd %s' % directory)
        host.cmd('python -m SimpleHTTPServer %s &' % str(port))
        print '%s server started' % str(host)

#Run specified test (Defaults to: all tests)
def exec_test_cases(test, targets, package=test_cases):
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        if modname in test_cases.EXCLUDE:
            continue

        module = importer.find_module(modname).load_module(modname)
        test_name, test_class = load_class(module)

        try:
            print 'Executing %s' % test_name
            generate_background_traffic(BACKGROUND_HOSTS, targets, 8000, 'sample1.txt')
            # test_class().run_test(targets, BACKGROUND_HOSTS)
        except TypeError:
            print 'Error. %s must have run_test(targets) method' % (test_name)

#Generate hosts directory of internal network
def log_target_hosts():
    targets_file = open('target_hosts.txt', 'w+')
    targets_arr = list()

    for i in range(0, len(HOSTS)):
        host = net.get('h' + str(i))
        ipaddr = host.cmd('hostname -I')

        targets_arr.append(ipaddr.rstrip())
        targets_file.write('%i_%s' % (i + 1, ipaddr))

    return targets_arr

def log_attack_hosts():
    attack_file = open('attack_hosts.txt', 'w+')
    attack_hosts_arr = list()

    offset = len(SWITCHES)
    for i in range(offset, len(BACKGROUND_HOSTS) + offset - 1):
        host = net.get('h' + str(i))
        ipaddr = host.cmd('hostname -I')

        attack_hosts_arr.append(ipaddr.rstrip())
        attack_file.write('%s' % (ipaddr))

def generate_background_traffic(hosts, target_hosts, port, filename):
    for i in range(0, len(target_hosts)):
        ab_cmd = 'ab -c 1 -n 10 http://%s:%s/%s &' % (target_hosts[i], port, filename)
        print 'Executing ab command: %s' % ab_cmd
        result = hosts[i].cmd(ab_cmd)

#Load class given a module
def load_class(module):
    for name, obj in inspect.getmembers(module, inspect.isclass):
        return name, obj

setLogLevel('info')

c0 = net.addController()

#Create network topology
create_network(3)
create_background_network(args.hosts, args.ratio)
create_router()

net.start()

#Get IP and MAC address data
int_ip_list = read_data_file(INT_IP_FILE)

#Link subnets to router
configure_router(IP_LIST)

#Start servers of internal network hosts
# start_internal_servers('dummy_files', 8000)

#Execute framework commands
log_attack_hosts()
targets_arr = log_target_hosts()
# exec_test_cases(args.test, targets_arr)

CLI(net)
net.stop()
