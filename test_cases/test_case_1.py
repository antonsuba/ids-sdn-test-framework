#!/usr/bin/python
# -*- coding: utf-8 -*-

class TestCase1(object):

    def __init__(self):
        self.packages = []

    def run_test(self, targets, hosts):
        self.check_dependencies(self.packages, hosts[0])
        self.exec_attack(targets, hosts)

    def check_dependencies(self, packages, host):
        result = host.cmd('dpkg -l %s' % (' '.join(packages)))
        if 'no packages found' in result:
            print 'Please install required dependencies by running:'
            print 'sudo apt-get install %s' % (' '.join(packages))
            # host.cmd('sudo apt-get install %s' % (' '.join(packages)))

    def exec_attack(self, targets, hosts):
        host_num = len(targets) + 1
        eth_intf = '%s-eth0' % host_num
        pcap_file = 'pcap/test-15jun.pcap'

        hosts[0].cmd('tcpreplay --topspeed -i %s %s' % (eth_intf, pcap_file))
