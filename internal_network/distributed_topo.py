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
        self.subnet_mask = '24'
        self.hosts = list()
        self.switches = dict()
        self.routers = dict()

        self.mac_ip_list = None
        self.ip_duplicates = dict()
        self.ip_tracker = list()

    def create_topo(self, topo, mac_ip_list):
        "Required method, called by main framework class. Generates network topology."

        self.mac_ip_list = mac_ip_list

        # subnet_count_tracker = dict()

        mac_ip_counter = 0
        for mac_ip_pair in mac_ip_list:
            mac = mac_ip_pair[0]
            ip = mac_ip_pair[1]
            network_addr = (ip.rsplit('.', 1)[:-1])[0] + '.0/' + self.subnet_mask

            # Subnet instance counter - guarantees unique IP interface for routing
            # if ip_subnet not in subnet_count_tracker:
            #     subnet_count_tracker[ip_subnet] = 1

            # ip_count = subnet_count_tracker[ip_subnet]

            # Create and link host and switch
            router = self.__get_router(topo, network_addr)
            router_ip_subnet = '%s/%s' % (router.ip, self.subnet_mask)

            host_ip = '%s/%s' % (ip, self.subnet_mask)            
            host = topo.addHost('h%i' % mac_ip_counter, ip=host_ip,
                                mac=mac, defaultRoute='via %s' % router.ip)
            switch = topo.addSwitch('s%s' % str(mac_ip_counter))

            topo.addLink(host, switch)
            topo.addLink(switch, self.switches[router.name])

            # subnet_count_tracker[ip_subnet] += 1
            self.ip_tracker.append(ip)

            self.hosts.append(host)
            self.switches[host] = switch

            mac_ip_counter += 1

        return self.hosts, self.switches, self.routers


    def __get_router(self, topo, network_addr):
        counter = len(self.routers)
        try:
            router = self.routers[network_addr]
        except KeyError:
            router_ip = network_addr[:-5] + '.1'
            router_name = topo.addNode('r%i' % counter, cls=LinuxRouter,
                                       ip=router_ip)

            Router = namedtuple('Router', 'name, ip')
            router = Router(name=router_name, ip=router_ip)
            self.routers[network_addr] = router

            switch = topo.addSwitch('ms%i' % counter)
            topo.addLink(router_name, switch)
            self.switches[router_name] = switch

        return router


    def configure_routers(self, routers, ext_routers_dict):
        "Add routes to other routers"

        all_routers_dict = dict(self.routers, **ext_routers_dict)

        for router in routers:
            for network_addr, dest_router in all_routers_dict.iteritems():
                dest_ip = dest_router.ip

                if dest_ip == router.IP():
                    continue

                info(router.cmd('ip route add %s via %s' % (network_addr, dest_ip)))
