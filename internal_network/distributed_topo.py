#!/usr/bin/python

from mininet.node import Node
from mininet.log import info

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
        self.switches = list()
        self.router = None

    def create_topo(self, topo, mac_ip_list):
        "Required method, called by main framework class. Generates network topology."

        default_router_ip = '%s/%s' % (mac_ip_list[0][1], self.subnet_mask)
        self.router = topo.addNode('r0', cls=LinuxRouter, ip=default_router_ip)

        for i in range(0, len(mac_ip_list)):
            mac = mac_ip_list[i][0]
            ip = mac_ip_list[i][1]

            host_ip = '%s/%s' % (ip, self.subnet_mask)
            default_route = (ip.rsplit('.', 1)[:-1])[0] + '.1'
            router_ip = '%s/%s' % (default_route, '32')

            host = topo.addHost('h%i' % i, ip=host_ip,
                                mac=mac, defaultRoute='via %s' % default_route)
            switch = topo.addSwitch('s%s' % str(i))

            # print '%s, %s, %s, %s' % (str(switch), 'r0-eth%s' % str(i+1), router_ip, default_route)

            topo.addLink(switch, self.router, intfName2='r0-eth%i' % i, params2={'ip':router_ip})
            topo.addLink(host, switch)

            # router.cmd('ifconfig r0-eth%i %s netmask %s' % (i, ip, '255.255.255.0'))

            self.hosts.append(host)
            self.switches.append(switch)

        return self.hosts, self.switches, self.router


    def configure_router(self, router, mac_ip_list):
        "Set subnet to interface routing of internal hosts"

        for i in range(0, len(mac_ip_list)):
            ip = mac_ip_list[i][1] + '/32'
            print 'ip route add %s dev r0-eth%i' % (ip, i)
            router.cmd('ip route add %s dev r0-eth%i' % (ip, i))

