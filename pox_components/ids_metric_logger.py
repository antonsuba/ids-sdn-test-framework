#Import pox libraries
from __future__ import division
from pox.core import core
from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

ATTACK_HOSTS_FILE = '/media/sf_ids-sdn/attack_hosts.txt'
RESULT_FILE = '/media/sf_ids-sdn/ids_test_results.txt'

class IDSMetricLogger(object):

    def __init__(self, connection):
        self.blocked_ips = {}
        connection.addListeners(self)

    def log_blocked_host(self, ip, classification=None):
        log.info('Logged %s' % str(ip))
        self.blocked_ips[str(ip)] = classification

    def write_results(self, filepath):
        attack_hosts = self.get_attack_hosts(ATTACK_HOSTS_FILE)
        log.info('Attack Hosts: %s' % str(attack_hosts))

        false_positives = [x for x in self.blocked_ips.keys() if x not in attack_hosts]
        false_negatives = [x for x in attack_hosts if x not in self.blocked_ips.keys()]

        # false_positives_percentage = max(0, 1 - (len(self.blocked_ips) / len(attack_hosts)))
        # false_negatives_percentage = max(0, 1 - (len(self.blocked_ips) / len(attack_hosts)))

        blocked_count = len(self.blocked_ips)

        f = open(filepath, 'w')
        f.write('IDS TEST RESULTS\n\n')

        # f.write('FALSE POSITIVE PERCENTAGE: %s' % false_positives_percentage)
        f.write('FALSE POSITIVES: %i / %i blocked hosts\n' % (len(false_positives), blocked_count))
        for x in false_positives:
            f.write('%s\n' % x)

        f.write('\n')

        # f.write('\nFALSE NEGATIVE PERCENTAGE: %s' % false_negatives_percentage)
        f.write('FALSE NEGATIVES: %i / %i blocked hosts\n' % (len(false_negatives), blocked_count))
        for x in false_negatives:
            f.write('%s\n' % x)

        f.close()

    def get_attack_hosts(self, filepath):
        attack_hosts = list()

        f = open(filepath, 'r')
        for line in f:
            attack_hosts.append(line)

        f.close()
        return attack_hosts

    def _handle_ConnectionDown(self, event):
        self.write_results(RESULT_FILE)

#Register component to POX core object
def launch():
    """
    Starts the component
    """
    def start_ids_logger(event):
        log.debug('IDS Logger started')
        core.registerNew(IDSMetricLogger, event.connection)

    core.openflow.addListenerByName('ConnectionUp', start_ids_logger)
