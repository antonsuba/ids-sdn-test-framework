#!/usr/bin/python

import argparse
import sys
from itertools import combinations
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel

def create_topo(n):
	#create nodes
    c0 = net.addController(port=6634)
    s.append(net.addSwitch('s0'))

    for i in range(0, n):
        s.append(net.addSwitch('s'+str(i+1)))
        h.append(net.addHost('h'+str(i)))
        net.addLink(s[0], s[i+1], bw=10, delay='10ms')
        net.addLink(h[i], s[i+1], bw=10, delay='10ms')
