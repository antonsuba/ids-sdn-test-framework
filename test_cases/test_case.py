class TestCase(object):
    packages = []

    def run(self, targets, int_hosts, ext_hosts, int_switches,
                 ext_switches, int_routers, ext_routers):
        self._check_dependencies(self.packages, int_hosts[0])
        self._exec_test(targets, int_hosts, ext_hosts, int_switches,
                          ext_switches, int_routers, ext_routers)

    def _check_dependencies(self, packages, host):
        result = host.cmd('dpkg -l %s' % (' '.join(packages)))
        if 'no packages found' in result:
            print 'Please install required dependencies by running:'
            print 'sudo apt-get install %s' % (' '.join(packages))

    def _exec_test(self, targets, int_hosts, ext_hosts, int_switches,
                          ext_switches, int_routers, ext_routers):
                    raise NotImplementedError()
