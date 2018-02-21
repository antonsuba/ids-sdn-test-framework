#!/usr/bin/python

from mininet.node import Node
from mininet.log import info
from collections import namedtuple


class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        print 'Router Config'
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class DistributedTopo(object):
    "Internal network topology class"

    def __init__(self):
        self.subnet_mask = '16'
        self.hosts = list()
        self.switches = dict()
        self.mac_ip_list = None
        self.ext_router_ip = '192.168.20.1'

    def create_topo(self, topo, main_switch, mac_ip_list):
        "Required method, called by main framework class. Generates network" \
            " topology."

        self.mac_ip_list = mac_ip_list

        mac_ip_counter = 0
        for mac_ip_pair in mac_ip_list:
            mac = mac_ip_pair[0]
            ip = mac_ip_pair[1]

            # Skip broadcast addresses
            if ip[-3:] == '255':
                continue

            # Create and link host and switch
            host_ip = '%s/%s' % (ip, self.subnet_mask)
            host = topo.addHost(
                'h%i' % mac_ip_counter,
                ip=host_ip,
                mac=mac,
                defaultRoute='via %s' % self.ext_router_ip)
            switch = topo.addSwitch('s%s' % str(len(self.switches) + 1))

            topo.addLink(host, switch)
            topo.addLink(switch, main_switch)

            self.hosts.append(host)
            self.switches[host] = switch

            mac_ip_counter += 1

        return self.hosts, self.switches
