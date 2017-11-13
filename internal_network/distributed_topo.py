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
        self.mac_ip_list = None
        self.ip_duplicates = dict()

    def create_topo(self, topo, mac_ip_list):
        "Required method, called by main framework class. Generates network topology."

        self.mac_ip_list = mac_ip_list

        ip_tracker = list()
        subnet_count_tracker = dict()

        default_router_ip = '%s/%s' % (mac_ip_list[0][1], self.subnet_mask)
        self.router = topo.addNode('r0', cls=LinuxRouter, ip=default_router_ip)

        mac_ip_counter = 0
        for mac_ip_pair in mac_ip_list:
            mac = mac_ip_pair[0]
            ip = mac_ip_pair[1]
            ip_subnet = (ip.rsplit('.', 1)[:-1])[0]

            #Check if duplicate IP - for virtual mac interface generation
            if ip in ip_tracker:
                host_num = ip_tracker.index(ip)
                try:
                    self.ip_duplicates[host_num].append(mac_ip_pair)
                except KeyError:
                    self.ip_duplicates[host_num] = [mac_ip_pair]
                continue

            #Subnet instance counter - guarantees unique IP interface for routing
            if ip_subnet not in subnet_count_tracker:
                subnet_count_tracker[ip_subnet] = 1

            ip_count = subnet_count_tracker[ip_subnet]

            #Create and link host and switch
            host_ip = '%s/%s' % (ip, self.subnet_mask)
            default_route = ip_subnet + '.' + str(ip_count)
            router_ip = '%s/%s' % (default_route, '32')

            host = topo.addHost('h%i' % mac_ip_counter, ip=host_ip,
                                mac=mac, defaultRoute='via %s' % default_route)
            switch = topo.addSwitch('s%s' % str(mac_ip_counter))

            # print '%s, %s, %s, %s' % (str(switch), 'r0-eth%s' % str(i+1), router_ip, default_route)

            topo.addLink(switch, self.router, intfName2='r0-eth%i' % mac_ip_counter, params2={'ip':router_ip})
            topo.addLink(host, switch)

            subnet_count_tracker[ip_subnet] += 1
            ip_tracker.append(ip)

            self.hosts.append(host)
            self.switches.append(switch)

            mac_ip_counter += 1

        print str(ip_tracker)
        return self.hosts, self.switches, self.router


    def generate_virtual_mac(self, hosts):
        "Generate virtual macs for IPs with multiple mac addresses"

        ip_duplicates = self.ip_duplicates

        print str(ip_duplicates)

        for host_num, mac_ip_list in ip_duplicates.iteritems():

            for i in range(0, len(mac_ip_list)):
                mac = mac_ip_list[i][0]
                ip = mac_ip_list[i][1]

                host = hosts[host_num]
                print 'ip link add link h%i-eth0 address %s h%i-eth0.%i type macvlan' % (host_num, mac, host_num, i+1)
                info(host.cmd('ip link add link h%i-eth0 address %s h%i-eth0.%i type macvlan' % (host_num, mac, host_num, i+1)))
                info(host.cmd('ifconfig h%i-eth0.%i %s netmask 255.255.255.128' % (host_num, i, ip)))


    def configure_router(self, router):
        "Set subnet to interface routing of internal hosts"

        mac_ip_list = self.mac_ip_list

        for i in range(0, len(mac_ip_list)):
            ip = mac_ip_list[i][1] + '/32'
            # print 'ip route add %s dev r0-eth%i' % (ip, i)
            info(router.cmd('ip route add %s dev r0-eth%i' % (ip, i)))
