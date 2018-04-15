#!/usr/bin/python
# -*- coding: utf-8 -*-


class TestCase1(object):
    def __init__(self):
        self.packages = ['hping3']

    def run_test(self, targets, int_hosts, ext_hosts, int_switches,
                 ext_switches, int_routers, ext_routers):
        self._check_dependencies(self.packages, int_hosts[0])
        self._exec_attack(targets, int_hosts, ext_hosts, int_switches,
                         ext_switches, int_routers, ext_routers)

    def _check_dependencies(self, packages, host):
        result = host.cmd('dpkg -l %s' % (' '.join(packages)))
        if 'no packages found' in result:
            print 'Please install required dependencies by running:'
            print 'sudo apt-get install %s' % (' '.join(packages))

    def _exec_attack(self, targets, int_hosts, ext_hosts, int_switches,
                    ext_switches, int_routers, ext_routers):
        host_num = len(targets) + 1
        eth_intf = '%s-eth0' % host_num
        pcap_file = 'pcap/test-15jun.pcap'

        int_hosts[0].cmd('tcpreplay --topspeed -i %s %s' % (eth_intf,
                                                            pcap_file))
