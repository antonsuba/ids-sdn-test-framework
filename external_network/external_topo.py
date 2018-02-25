from mininet.node import Node
from mininet.log import info
from collections import namedtuple


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


class ExternalTopo(object):
    "Internal network topology class"

    def __init__(self):
        self.subnet_mask = '24'
        self.hosts = list()
        self.switches = dict()
        self.routers = dict()
        self.offset = None
        self.mac_ip_dict = None

    def create_topo(self, topo, main_switch, mac_ip_dict, int_routers, offset):
        "Required method, called by main framework class. Generates network topology."

        self.offset = offset
        self.mac_ip_dict = mac_ip_dict

        mac_ip_counter = 0
        network_addr = None

        for mac, ip_set in mac_ip_dict.iteritems():
            ip_list = list(ip_set)
            ip = '192.168.19.' + str(mac_ip_counter + 1)

            # if not self.routers:
            #     network_addr = (ip.rsplit('.', 1)[:-1])[0] + '.0/' + self.subnet_mask

            aliases = ip_list
            alias_set = set((alias.rsplit('.', 1)[:-1])[0] + '.' +
                            str(int(alias.rsplit('.', 1)[-1]) + 1)
                            for alias in aliases)

            # Create and link host and switch
            router = self.__get_router(topo, main_switch, network_addr,
                                       alias_set, int_routers)

            host_ip = '%s/%s' % (ip, self.subnet_mask)
            host = topo.addHost(
                'h%s' % str(mac_ip_counter + offset),
                ip=host_ip,
                mac=mac,
                defaultRoute='via %s' % router.ip)
            switch_num = len(self.switches) + offset + 1
            switch = topo.addSwitch('s%i' % switch_num)

            topo.addLink(host, switch)
            topo.addLink(switch, self.switches[router.name])

            self.hosts.append(host)
            self.switches[host] = switch

            mac_ip_counter += 1

        # self.__create_tcpreplay_host(topo, mac_ip_counter)

        return self.hosts, self.switches, self.routers

    def __create_tcpreplay_host(self, topo, switch_num):
        replay_host = topo.addHost(
            'rh0',
            ip='192.168.19.%i' % len(self.hosts),
            defaultRoute='via 192.168.19.254')
        switch = topo.addSwitch('s%i' % switch_num)
        router = self.routers.itervalues().next()

        topo.addLink(replay_host, switch)
        topo.addLink(switch, router.name)

    def __get_router(self, topo, main_switch, network_addr, aliases, int_routers):
        counter = len(self.routers)
        try:
            router = self.routers[network_addr]
            router.aliases.update(aliases)
        except KeyError:
            link_subnet = '192.168.20.'
            link_ip = link_subnet + str(counter + len(int_routers))

            # router_ip = network_addr[:-5] + '.1'
            router_ip = '192.168.19.254'
            router_name = topo.addNode(
                'r%i' % (counter + self.offset),
                cls=LinuxRouter, 
                ip=router_ip + '/24')

            Router = namedtuple('Router', 'name, ip, link_ip, aliases')
            router = Router(
                name=router_name,
                ip=router_ip,
                link_ip=link_ip,
                aliases=aliases)
            self.routers[network_addr] = router

            switch_num = len(self.switches) + 1
            switch = topo.addSwitch('s%i' % switch_num)
            self.switches[router_name] = switch

            topo.addLink(router_name, switch)

            for i in range(len(int_routers)):
                link_ip = link_subnet + str(counter + len(int_routers) + i)               
                topo.addLink(
                    router_name, main_switch, params1={'ip': link_ip + '/24'})

        return router

    def generate_ip_aliases(self, routers, hosts):
        "Generate IP aliases for IPs with same MAC"

        offset = self.offset
        mac_ip_dict = self.mac_ip_dict

        host_num = 0
        # router_alias_counter = 0

        router = routers[0]
        router_info = self.routers.itervalues().next()
        aliases = list(router_info.aliases)

        for i in range(len(aliases)):
            alias = aliases[i]
            router_alias_ip = (alias.rsplit(
                '.',
                1)[:-1])[0] + '.' + str(int(alias.rsplit('.', 1)[-1]) + 1)

            print 'ifconfig %s-eth0:%i %s up' % (router.name, i,
                                                 router_alias_ip)
            info(
                router.cmd('ifconfig %s-eth0:%i %s up' % (router_info.name, i,
                                                          router_alias_ip)))

        for mac, ip_set in mac_ip_dict.iteritems():
            ip_list = list(ip_set)
            host = hosts[host_num]

            # print 'ip route add default via %s' % router_info.ip
            # info(host.cmd('ip route add default via %s' % router_info.ip))

            for i in range(0, len(ip_list) - 1):
                ip = ip_list[i + 1]
                info(
                    host.cmd('ifconfig h%i-eth0:%i %s up' % (host_num + offset, i, ip)))
                # info(host.cmd('ip route del '))

            host_num += 1

    def configure_routers(self, routers, int_routers_dict):
        "Add routes to other routers"

        all_routers_dict = dict(self.routers, **int_routers_dict)

        for router in routers:
            for network_addr, dest_router in all_routers_dict.iteritems():
                if dest_router.ip == router.IP():
                    continue

                dest_ip = dest_router.link_ip

                print 'ip route add %s via %s' % (network_addr, dest_ip)
                info(
                    router.cmd('ip route add %s via %s' % (network_addr,
                                                           dest_ip)))

                if dest_router.aliases:
                    for alias in dest_router.aliases:
                        print router.IP()
                        print 'ip route add %s via %s' % (alias, dest_ip)
                        info(
                            router.cmd('ip route add %s via %s' % (alias,
                                                                   dest_ip)))
