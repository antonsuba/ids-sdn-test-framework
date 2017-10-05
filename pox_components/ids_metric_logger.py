#Import pox libraries
from pox.core import core
from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

class IDSMetricLogger(object):

    def __init__(self, connection):
        self.connection = connection
        self.blocked_ips = list()
        connection.addListeners(self)

    def log_blocked_host(self, ipaddr):
        self.blocked_ips.append(ipaddr)

    #Register component to POX core object
    def launch(self):
        core.registerNew(IDSMetricLogger)
        