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

    def create_topo(self, topo, main_switch, mac_ip_list):
        "Required method, called by main framework class. Generates network topology."

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
                defaultRoute='via %s' %
                router.ip)  # TODO: Change default route
            switch = topo.addSwitch('s%s' % str(len(self.switches) + 1))

            topo.addLink(host, switch)
            topo.addLink(switch, main_switch)

            self.hosts.append(host)
            self.switches[host] = switch

            mac_ip_counter += 1

        # print self.switches

        return self.hosts, self.switches

    def configure_routers(self, routers, ext_routers_dict):
        "Add routes to other routers"

        print str(ext_routers_dict)
        ext_router = ext_routers_dict.itervalues().next()

        for router in routers:
            info(
                router.cmd('ip route add default via %s' % ext_router.link_ip))

            for network_addr, dest_router in self.routers.iteritems():
                if dest_router.ip == router.IP():
                    continue

                dest_ip = dest_router.link_ip

                # print 'ip route add %s via %s' % (network_addr, dest_ip)
                info(
                    router.cmd('ip route add %s via %s' % (network_addr,
                                                           dest_ip)))
