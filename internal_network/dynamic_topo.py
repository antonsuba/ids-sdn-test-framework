#!/usr/bin/python

class DistributedTopo(object):

    def create_topo(self, mac_ip_list, net, SWITCHES, HOSTS):
        #create nodes
        SWITCHES.append(net.addSwitch('s0'))

        for i in range(0, len(mac_ip_list)):
            mac = mac_ip_list[i][0]
            ip = mac_ip_list[i][1]

            SWITCHES.append(net.addSwitch('s'+str(i+1)))
            HOSTS.append(net.addHost('h'+str(i), ip=ip, mac=mac, defaultRoute='192.168.2.0'))

            net.addLink(SWITCHES[0], SWITCHES[i+1], bw=10, delay='10ms')
            net.addLink(HOSTS[i], SWITCHES[i+1], bw=10, delay='10ms')
