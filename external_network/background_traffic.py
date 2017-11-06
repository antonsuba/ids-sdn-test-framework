class BackgroundTraffic(object):

    def create_topo(self, net, mac_ip_dict, offset, SWITCHES,
                    BACKGROUND_HOSTS, TEST_SWITCHES):

        host_num = 0
        for mac, ip_set in mac_ip_dict.iteritems():
            ip_list = list(ip_set)

            BACKGROUND_HOSTS.append(net.addHost('h' + str(host_num + offset - 1),
                                                ip=ip_list[0] + '/1', mac=mac))
            TEST_SWITCHES.append(net.addSwitch('s' + str(host_num + offset)))

            net.addLink(SWITCHES[0], TEST_SWITCHES[host_num], bw=10, delay='10ms')
            net.addLink(BACKGROUND_HOSTS[host_num], TEST_SWITCHES[host_num], bw=10, delay='10ms')

            for i in range(0, len(ip_list) - 1):
                ip = ip_list[i + 1]
                host = BACKGROUND_HOSTS[host_num]

                host.cmd('ifconfig h%i-eth0:%i %s up' % ((host_num + offset - 1), i, ip))

            host_num += 1
