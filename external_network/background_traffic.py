class BackgroundTraffic(object):

    def create_topo(self, net, ip_mac_list, offset, SWITCHES,
                    BACKGROUND_HOSTS, TEST_SWITCHES):

        for i in range(0, len(ip_mac_list)):
            ip = ip_mac_list[i][0]
            mac = ip_mac_list[i][1]

            BACKGROUND_HOSTS.append(net.addHost('h' + str(i + offset - 1), ip=ip, mac=mac))
            TEST_SWITCHES.append(net.addSwitch('s' + str(i + offset)))

            net.addLink(SWITCHES[0], TEST_SWITCHES[i], bw=10, delay='10ms')
            net.addLink(BACKGROUND_HOSTS[i], TEST_SWITCHES[i], bw=10, delay='10ms')
