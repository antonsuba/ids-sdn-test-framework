#!/usr/bin/python
# -*- coding: utf-8 -*-
from mininet.log import info
from test_case import TestCase

class DDOS(TestCase):
    trigger = 'ddos'
    packages = ['hping3']

    def _exec_test(self, targets, int_hosts, ext_hosts, int_switches,
                     ext_switches, int_routers, ext_routers):
        internal_ips = [host.cmd('hostname -I').rstrip() for host in int_hosts]

        for ext_host in ext_hosts:
            target_ip = internal_ips.pop()
            attack_ip = ext_host.cmd('hostname -I').rstrip()

            print('Attacking %s using %s' % (target_ip, attack_ip))
            ext_host.sendCmd('hping3 -c 10000000 --faster %s' % target_ip)
