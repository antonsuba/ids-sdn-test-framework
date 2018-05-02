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
        # filtered_hosts = []
        # filtered_ip = []
        # for host in int_hosts:
        #     if host.IP() not in filtered_ip:
        #         filtered_hosts.append(host)
        #         filtered_ip.append(host.IP())

        # internal_hosts = filtered_hosts[:len(ext_hosts) * 2]
        # target_hosts = internal_hosts[:len(internal_hosts)/2]
        # traffic_hosts = internal_hosts[len(internal_hosts)/2:]

        # popens = {}

        # for ext_host in ext_hosts:
        #     target = target_hosts.pop()
        #     traffic = traffic_hosts.pop()

            # attack_ip = ext_host.cmd('hostname -I').rstrip()            
            # target_ip = target.cmd('hostname -I').rstrip()
            # traffic_ip = traffic.cmd('hostname -I').rstrip()
            # attack_ip = ext_host.IP()
            # target_ip = target.IP()
            # traffic_ip = traffic.IP()

            # print('Generating traffic for %s using %s' % (target_ip, traffic_ip))
            # # traffic.sendCmd('hping3 -c 5000 %s' % target_ip)
            # popens[traffic] = traffic.popen('hping3 -c 5000 %s' % target_ip)

            # print('Attacking %s using %s' % (target_ip, attack_ip))
            # popens[ext_host] = ext_host.popen('hping3 -c 10000000 --faster %s' % target_ip)

        popens = {}

        # popens[ext_hosts[0]] = ext_hosts[0].popen('hping3 -c 10000000 --faster 192.168.2.112')
        # popens[ext_hosts[1]] = ext_hosts[1].popen('hping3 -c 10000000 --faster 192.168.3.114')
        # popens[ext_hosts[2]] = ext_hosts[2].popen('hping3 -c 10000000 --faster 192.168.1.103')
        # popens[ext_hosts[3]] = ext_hosts[3].popen('hping3 -c 10000000 --faster 192.168.2.109')
        # popens[ext_hosts[4]] = ext_hosts[4].popen('hping3 -c 10000000 --faster 192.168.4.119')
        # popens[ext_hosts[5]] = ext_hosts[5].popen('hping3 -c 10000000 --faster 192.168.5.122')        
        
        popens[int_hosts[0]] = int_hosts[0].popen('tcpreplay -i h1-eth0 /media/sf_ids-sdn/pcap/testbed-15jun.pcap')

        # popens[int_hosts[0]] = int_hosts[0].popen('hping3 -c 3000 192.168.2.112')
        # popens[int_hosts[2]] = int_hosts[0].popen('hping3 -c 3000 192.168.3.114')
        # popens[int_hosts[3]] = int_hosts[0].popen('hping3 -c 3000 192.168.1.103')

        # popens[int_hosts[3]] = int_hosts[0].popen('hping3 -c 3000 192.168.2.109')
        # popens[int_hosts[3]] = int_hosts[0].popen('hping3 -c 3000 192.168.5.122')

        for host, line in pmonitor(popens):
            if host:
                info('<%s>: %s' % (host.name, line))
