from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import dpidToStr
from pox.lib.revent import EventHalt
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from sklearn.externals import joblib

CLASSIFIER_FILE = 'adaboost-ids.pkl'

log = core.getLogger()
checker = list()

class PacketChecker(object):

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

        self.number = switch_number
        self.attached_host = "10.0.0." + str(self.number)
        self.mac_to_port = {}
        self.enable_checker = False
        self.srcip_list = {}
        self.black_list = list()
        self.timestamp_log = list()
        self.count = 0
        log.info("Switch active")
        log.info("Switch number: " + str(self.number))

        self.clf = joblib.load(CLASSIFIER_FILE)
        log.info('Classifier loaded')

        log.info('Switch active')
        log.info('Switch number:' +  str(self.number))

    def set_checker(self, enable):
        self.enable_checker = enable
        print 'This checker has been set to: ' + str(enable)

    def _handle_PacketIn(self, event):
        log.info('IDS Packet In')

        if self.enable_checker == True:
            packet = event.parsed

            self.count += 1
            log.info("Switch#" + str(self.number) + " packet# " + str(self.count))
            ip = packet.find('ipv4')

            if ip is None:
                log.info("Switch# " + str(self.number) + " This isn't IP!")
            else:

                log.info("Switch# " + str(self.number) + " Source IP: " +  str(ip.srcip))

                if str(ip.srcip) in self.black_list:
                    log.info(str(ip.srcip) + "BLOCKED!")

                    msg = of.ofp_flow_mod()
                    msg.priority = 30000
                    msg.match.dl_type = pkt.ethernet.IP_TYPE
                    msg.match.nw_dst = IPAddr(self.attached_host)
                    msg.match.nw_src = ip.srcip
                    msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
                    self.connection.send(msg)
                    return EventHalt

                pred = self.clf.predict()

                if pred:
                    print("Added to blacklist: " + str(ip.srcip) + "Reason: " + str(len(self.srcip_list[ip.srcip])))
                    self.black_list.append(str(ip.srcip))

                    #Create openflow message to set block rule
                    msg = of.ofp_flow_mod()
                    msg.priority = 30000
                    msg.match.dl_type = pkt.ethernet.IP_TYPE
                    msg.match.nw_dst = IPAddr(self.attached_host)
                    msg.match.nw_src = ip.srcip
                    msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
                    self.connection.send(msg)

    #Start Component
    def launch(self):

        def start_switch (event):
            global switch_number
            switch_number += 1
            log.debug("Controlling %s" % (event.connection,))
            checker.append(PacketChecker(event.connection))
            core.Interactive.variables['checker'] = checker

        core.openflow.addListenerByName("Connection Up", start_switch)
