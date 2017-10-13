#!/usr/bin/python

class DistributedTopo(object):

    def create_topo(self, n, net, SWITCHES, HOSTS):
        #create nodes
        SWITCHES.append(net.addSwitch('s0'))

        for i in range(0, n):
            SWITCHES.append(net.addSwitch('s'+str(i+1)))
            HOSTS.append(net.addHost('h'+str(i)))
            net.addLink(SWITCHES[0], SWITCHES[i+1], bw=10, delay='10ms')
            net.addLink(HOSTS[i], SWITCHES[i+1], bw=10, delay='10ms')
