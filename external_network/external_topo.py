from mininet.log import info

class ExternalTopo(object):
    "Internal network topology class"

    def __init__(self):
        self.subnet_mask = '24'
        self.hosts = list()
        self.switches = list()

        self.offset = None
        self.mac_ip_dict = None

    def create_topo(self, topo, mac_ip_dict, offset, router):
        "Required method, called by main framework class. Generates network topology."

        self.offset = offset
        self.mac_ip_dict = mac_ip_dict

        ip_count_tracker = dict()

        host_num = 0
        for mac, ip_set in mac_ip_dict.iteritems():
            ip_list = list(ip_set)
            ip = ip_list[0]

            if ip not in ip_count_tracker:
                ip_count_tracker[ip] = 1

            ip_count = ip_count_tracker[ip]

            host_ip = '%s/%s' % (ip, self.subnet_mask)
            default_route = (ip.rsplit('.', 1)[:-1])[0] + '.' + str(ip_count)
            router_ip = '%s/%s' % (default_route, '32')

            host = topo.addHost('h%s' % str(host_num + offset), ip=host_ip,
                                mac=mac, defaultRoute='via %s' % default_route)
            switch = topo.addSwitch('s' + str(host_num + offset))

            topo.addLink(switch, router, intfName2='r0-eth%i' % (host_num + offset),
                         params2={'ip':router_ip})
            topo.addLink(host, switch)

            ip_count_tracker[ip] += 1

            self.hosts.append(host)
            self.switches.append(switch)

            host_num += 1

        return self.hosts, self.switches


    def generate_ip_aliases(self, hosts):
        "Generate IP aliases for IPs with same MAC"

        offset = self.offset
        mac_ip_dict = self.mac_ip_dict

        host_num = 0
        for mac, ip_set in mac_ip_dict.iteritems():
            ip_list = list(ip_set)
            host = hosts[host_num]

            for i in range(0, len(ip_list) - 1):
                ip = ip_list[i + 1]
                print 'ifconfig h%i-eth0:%i %s up' % ((host_num + offset), i, ip)
                host.cmd('ifconfig h%i-eth0:%i %s up' % ((host_num + offset), i, ip))

            host_num += 1


    def configure_router(self, router):
        "Set subnet to interface routing of internal hosts"

        host_num = self.offset
        mac_ip_dict = self.mac_ip_dict

        for mac, ip_set in mac_ip_dict.iteritems():
            ip_list = list(ip_set)

            for ip in ip_list:
                ip_subnet = ip + '/32'
                # print 'ip route add %s dev r0-eth%i' % (ip_subnet, host_num)
                info(router.cmd('ip route add %s dev r0-eth%i' % (ip_subnet, host_num)))

            host_num += 1

