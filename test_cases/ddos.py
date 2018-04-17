#!/usr/bin/python
# -*- coding: utf-8 -*-
from mininet.log import info
from mininet.util import pmonitor
from test_cases.test_case import TestCase

class DDOS(TestCase):
    trigger = 'ddos'
    packages = ['hping3']

    def _exec_test(self, targets, int_hosts, ext_hosts, int_switches,
                     ext_switches, int_routers, ext_routers):
        internal_hosts = int_hosts[:len(ext_hosts) * 2]
        target_hosts = internal_hosts[:len(internal_hosts)/2]
        traffic_hosts = internal_hosts[len(internal_hosts)/2:]        

        popens = {}

        for ext_host in ext_hosts:
            target = target_hosts.pop()
            traffic = traffic_hosts.pop()

            attack_ip = ext_host.cmd('hostname -I').rstrip()            
            target_ip = target.cmd('hostname -I').rstrip()
            traffic_ip = traffic.cmd('hostname -I').rstrip()

            print('Generating traffic for %s using %s' % (target_ip, traffic_ip))
            # traffic.sendCmd('hping3 -c 5000 %s' % target_ip)
            popens[traffic] = traffic.popen('hping3 -c 5000 %s' % target_ip)

            print('Attacking %s using %s' % (target_ip, attack_ip))
            popens[ext_host] = ext_host.popen('hping3 -c 10000000 --faster %s' % target_ip)

        for host, line in pmonitor(popens):
            if host:
                info('<%s>: %s' % (host.name, line))
