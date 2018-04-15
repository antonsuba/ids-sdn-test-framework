import os
from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import dpidToStr
from pox.lib.revent import EventHalt
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from sklearn.externals import joblib
from switch_pt import Switch

CLASSIFIER_FILE = os.path.expanduser(
    '~/ml-ids-test-environment-sdn/ml_ids/ids_models/%s.pkl' %
    'adaboost-ids')  # TODO: Let user pick on startup
TARGET_HOSTS_FILE = os.path.expanduser(
    '~/ml-ids-test-environment-sdn/config/target_hosts.txt')

log = core.getLogger()
checker = list()
switch_number = -1
global_black_list = list()
global_packet_count = 0

PROTOCOLS = {
    pkt.ipv4.ICMP_PROTOCOL: 0,
    pkt.ipv4.IGMP_PROTOCOL: 1,
    pkt.ipv6.ICMP6_PROTOCOL: 3,
    pkt.ipv4.TCP_PROTOCOL: 4,
    pkt.ipv4.UDP_PROTOCOL: 5
}


class PacketChecker(object):
    def __init__(self, connection, dpid):
        self.connection = connection
        connection.addListeners(self)

        self.number = dpid
        self.attached_host = None
        self.attached_host_num = None
        self.enable_checker = False
        self.srcip_list = {}
        self.black_list = list()
        self.timestamp_log = list()
        self.source_ip_count_list = {}
        self.source_port_count_list = {}
        self.destination_ip_count_list = {}
        self.destination_port_count_list = {}
        self.count = 0

        self.clf = joblib.load(CLASSIFIER_FILE)
        log.info('Classifier loaded')

        log.info('Connection:')
        log.info(connection)

        log.info('Switch active')
        log.info('Switch number:' + str(self.number))

        self.activate_ids()

    def activate_ids(self, filepath=TARGET_HOSTS_FILE):
        f = open(filepath, 'r')
        for line in f:
            host = line.split('_')
            host_num = int(host[0])
            switch_num = int(host[1])
            ip = host[2].split()[0]

            if switch_num == self.number:
                self.set_checker(True)
                self.attached_host = ip
                self.attached_host_num = host_num
                log.debug('IDS Switch %i activated with IP %s' % (switch_num,
                                                                  ip))

    def set_checker(self, enable):
        self.enable_checker = bool(enable)
        print 'This checker has been set to: ' + str(enable)

    def get_global_blacklist(self):
        print 'Blacklist: %s' % str(global_black_list)

    def generate_prediction_entry(self, ip, dst_ip, dst_port, packet,
                                  packet_in):
        entry = list()

        entry.append(self.destination_port_count_list[dst_port])
        entry.append(self.destination_ip_count_list[dst_ip])
        entry.append(self.source_port_count_list[packet_in.in_port])
        entry.append(self.source_ip_count_list[ip.srcip])

        protocol_one_hot = [0, 0, 0, 0, 0, 0]

        protocol_num = PROTOCOLS[ip.protocol]
        protocol_one_hot[protocol_num] = 1
        entry.extend(protocol_one_hot)

        return [entry]

    def set_block_rule(self, ip):
        msg = of.ofp_flow_mod()
        msg.priority = 30000
        msg.match.dl_type = pkt.ethernet.IP_TYPE
        msg.match.nw_dst = IPAddr(self.attached_host)
        msg.match.nw_src = ip.srcip
        msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
        self.connection.send(msg)

    def _handle_PacketIn(self, event):
        if self.enable_checker is True:
            packet = event.parsed
            packet_in = event.ofp

            self.count += 1
            log.info('Host#%i - %s' % (self.attached_host_num,
                                       self.attached_host))
            # log.info('Switch#%i - packet#%i' % (self.number, self.count))

            ip = packet.find('ipv4')
            if ip is None:
                log.info("Switch# " + str(self.number) + " This isn't IP!\n")
            else:

                log.info("Switch#" + str(self.number) + " Source IP: " +
                         str(ip.srcip) + 'Destination IP:' + str(ip.dstip))

                # Do nothing if packet came from host
                if self.attached_host == ip.srcip:
                    log.info('Packet from attached host\n')
                    return

                if self.attached_host != ip.dstip:
                    log.info('Packet not for this host\n')
                    return

                # Check if IP is already blocked
                if str(ip.srcip) in self.black_list:
                    log.info("%s BLOCKED!" % str(ip.srcip))

                    # Create openflow message to set block rule
                    self.set_block_rule(ip)
                    return EventHalt

                # Check if destination port is recorded as a table rule
                mac_to_port = Switch.get_mac_to_port(self.number)
                # log.info('Adaboost PID: %s' % str(id(mac_to_port)))

                # log.info(mac_to_port)
                log.info('Packet dst: %s' % packet)
                if packet.dst not in mac_to_port:
                    log.info('Skip packet. Not in mac_to_port')
                    log.info('\n')
                    # return
                else:
                    global global_packet_count
                    global_packet_count += 1
                    log.debug('Packet count: %s' % global_packet_count)

                    # Check and update count of destination port
                    dst_port = mac_to_port[packet.dst]

                    dst_ip = IPAddr(self.attached_host)
                    if dst_ip in self.destination_ip_count_list:
                        self.destination_ip_count_list[dst_ip] += 1
                    else:
                        self.destination_ip_count_list[dst_ip] = 1

                    if dst_port in self.destination_port_count_list:
                        self.destination_port_count_list[dst_port] += 1
                    else:
                        self.destination_port_count_list[dst_port] = 1

                    # Check and update count of source IP
                    if ip.srcip in self.source_ip_count_list:
                        self.source_ip_count_list[ip.srcip] += 1
                    else:
                        self.source_ip_count_list[ip.srcip] = 1

                    if packet_in.in_port in self.source_port_count_list:
                        self.source_port_count_list[packet_in.in_port] += 1
                    else:
                        self.source_port_count_list[packet_in.in_port] = 1

                    # Generate array for prediction then classify
                    entry = self.generate_prediction_entry(
                        ip, dst_ip, dst_port, packet, packet_in)
                    log.info(str(entry))
                    pred = self.clf.predict(entry)

                    log.debug('%s - classification: %i' % (str(ip.srcip),
                                                           pred))

                    if pred:
                        log.info("Added to blacklist: %s" % str(ip.srcip))
                        self.black_list.append(str(ip.srcip))
                        global_black_list.append(str(ip.srcip))

                        # Create openflow message to set block rule
                        self.set_block_rule(ip)

                        # Log IP of anomalous host
                        core.IDSMetricLogger.log_blocked_host(ip.srcip)

                    log.info('\n')


# Start Component
def launch():
    def start_switch(event):
        global switch_number
        switch_number += 1
        log.debug("Controlling %s" % (event.connection, ))
        checker.append(PacketChecker(event.connection, event.dpid))
        core.Interactive.variables['checker'] = checker

    core.openflow.addListenerByName("ConnectionUp", start_switch)
