#!/usr/bin/python
# -*- coding: utf-8 -*-
from mininet.log import info


class TestCase1(object):
    def __init__(self):
        self.packages = []

    def run_test(self, targets, int_hosts, ext_hosts, int_switches,
                 ext_switches, int_routers, ext_routers):
        self.check_dependencies(self.packages, int_hosts[0])
        self.exec_attack(targets, int_hosts, ext_hosts, int_switches,
                         ext_switches, int_routers, ext_routers)

    def check_dependencies(self, packages, host):
        result = host.cmd('dpkg -l %s' % (' '.join(packages)))
        if 'no packages found' in result:
            print 'Please install required dependencies by running:'
            print 'sudo apt-get install %s' % (' '.join(packages))

    def exec_attack(self, targets, int_hosts, ext_hosts, int_switches,
                    ext_switches, int_routers, ext_routers):
        host_num = sum(len(lis) for lis in [int_hosts, ext_hosts]) + 2
        eth_intf = 'r%s-eth0' % host_num
        pcap_file = 'pcap/test-15jun.pcap'

        info(ext_routers[0].cmd('tcpreplay --topspeed -i %s %s' % (eth_intf,
                                                                   pcap_file)))
