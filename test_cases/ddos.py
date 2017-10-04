#!/usr/bin/python
# -*- coding: utf-8 -*-

class DDOS(object):

    def __init__(self):
        self.name = 'DDOS'
        self.packages = ['apache2-utils']

    def run_test(self, targets, hosts):
        self.check_dependencies(self.packages, hosts[0])
        #self.exec_attack(targets, hosts)

    def check_dependencies(self, packages, host):
        result = host.cmd('dpkg -l %s' % (' '.join(packages)))
        if 'no packages found' in result:
            print 'Please install required dependencies by running:'
            print 'sudo apt-get install %s' % (' '.join(packages))
            # host.cmd('sudo apt-get install %s' % (' '.join(packages)))

    def exec_attack(self, targets, hosts):
        print 'Executing attack: %s' % self.name
        for i in range(0, len(targets)):
            filename = 'sample1.txt'
            hosts[i].cmd('ab -t 20 -c 5 -n 10000000 http://%s/%s' % (targets[i], filename))
