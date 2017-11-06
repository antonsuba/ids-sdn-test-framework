#!/usr/bin/python

class DistributedTopo(object):
    "Internal network topology class"

    def __init__(self):
        self.subnet_mask = '24'

    def create_topo(self, mac_ip_list, topo):
        "Required method, called by main framework class. Generates network topology."

        hosts = list()
        switches = list()

        #create nodes
        switches.append(topo.addSwitch('s0'))

        for i in range(0, len(mac_ip_list)):
            mac = mac_ip_list[i][0]
            ip = mac_ip_list[i][1]
            default_route = (ip.rsplit('.', 1)[:-1])[0] + '.1'

            switches.append(topo.addSwitch('s%i' % i+1))
            hosts.append(topo.addHost('h%i' % i, ip='%s/%s' % (ip, self.subnet_mask),
                                      mac=mac, defaultRoute='via %s' % default_route))

            topo.addLink(switches[0], switches[i+1], bw=10, delay='10ms')
            topo.addLink(hosts[i], switches[i+1], bw=10, delay='10ms')

        return hosts, switches
