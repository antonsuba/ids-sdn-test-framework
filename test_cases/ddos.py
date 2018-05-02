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

        popens = {}

        popens[ext_hosts[0]] = ext_hosts[0].popen(
            'hping3 -c 10000000 --faster 192.168.2.112')
        popens[ext_hosts[1]] = ext_hosts[1].popen(
            'hping3 -c 10000000 --faster 192.168.3.114')
        popens[ext_hosts[2]] = ext_hosts[2].popen(
            'hping3 -c 10000000 --faster 192.168.1.103')
        popens[ext_hosts[3]] = ext_hosts[3].popen(
            'hping3 -c 10000000 --faster 192.168.2.109')
        popens[ext_hosts[4]] = ext_hosts[4].popen(
            'hping3 -c 10000000 --faster 192.168.4.119')
        popens[ext_hosts[5]] = ext_hosts[5].popen(
            'hping3 -c 10000000 --faster 192.168.5.122')

        popens[int_hosts[0]] = int_hosts[0].popen(
            'tcpreplay --topspeed -i h1-eth0 /media/sf_ids-sdn/pcap/testbed-15jun.pcap'
        )

        for host, line in pmonitor(popens):
            if host:
                info('<%s>: %s' % (host.name, line))
