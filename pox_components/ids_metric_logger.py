# Import pox libraries
from __future__ import division
import os
from pox.core import core
from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()

ATTACK_HOSTS_FILE = os.path.expanduser(
    '~/ids-sdn-test-framework/config/attack_hosts.txt')
RESULT_FILE = os.path.expanduser(
    '~/ids-sdn-test-framework/results/ids_test_results.txt')

global_blocked_ips = {}


class IDSMetricLogger(object):
    def __init__(self, connection):
        # global_blocked_ips = {}
        connection.addListeners(self)

    def log_blocked_host(self, ip, classification=None):
        log.info('Logged %s' % str(ip))
        global_blocked_ips[str(ip)] = classification

    def write_results(self, filepath):
        attack_hosts = self.get_hosts(ATTACK_HOSTS_FILE)
        attack_hosts = [x.rstrip() for x in attack_hosts[1:]]
        log.info('Attack Hosts: %s' % str(attack_hosts))

        log.debug('Logged Hosts: %s' % str(global_blocked_ips.keys()))

        correct_blocks = [
            x for x in global_blocked_ips.keys() if x in attack_hosts
        ]
        false_positives = [
            x for x in global_blocked_ips.keys() if x not in attack_hosts
        ]
        false_negatives = [
            x for x in attack_hosts if x not in global_blocked_ips.keys()
        ]

        # false_positives_percentage = max(0, 1 - (len(global_blocked_ips) / len(attack_hosts)))
        # false_negatives_percentage = max(0, 1 - (len(global_blocked_ips) / len(attack_hosts)))

        blocked_count = len(global_blocked_ips)

        f = open(filepath, 'w')
        f.write('IDS TEST RESULTS\n\n')

        # f.write('STRESS TEST 1: NORMAL BACKGROUND TRAFFIC\n')

        f.write('TRUE POSITIVES %i / %i attack hosts\n' % (len(correct_blocks),
                                                           len(attack_hosts)))
        for x in correct_blocks:
            f.write('%s\n' % x)

        f.write('\n')

        f.write('TRUE NEGATIVES %i / %i total hosts\n' % (len(correct_blocks),
                                                          len(attack_hosts)))
        for x in correct_blocks:
            f.write('%s\n' % x)

        f.write('\n')

        # f.write('FALSE POSITIVE PERCENTAGE: %s' % false_positives_percentage)
        f.write('FALSE POSITIVES: %i / %i background hosts\n' %
                (len(false_positives), blocked_count))
        for x in false_positives:
            f.write('%s\n' % x)

        f.write('\n')

        # f.write('\nFALSE NEGATIVE PERCENTAGE: %s' % false_negatives_percentage)
        f.write('FALSE NEGATIVES: %i / %i attack hosts\n' %
                (len(false_negatives), len(attack_hosts)))
        for x in false_negatives:
            f.write('%s\n' % x)

        f.write('\n')

        f.write('PRECISION SCORE: %s\n' % 0 if not len(correct_blocks) else str(
            float(len(correct_blocks)) / len(global_blocked_ips)))

        f.write('\n')

        f.write('RECALL SCORE: %s' % 0 if not len(correct_blocks) else str(float(
            len(correct_blocks)) / len(attack_hosts)))

        # f.write('STRESS TEST 2: HIGH CPU LOAD\n')

        # f.write('STRESS TEST 3: HIGH VOLUME TRAFFIC\n')

        f.close()

    def get_hosts(self, filepath):
        hosts = list()

        f = open(filepath, 'r')
        for line in f:
            hosts.append(line)

        f.close()
        return hosts

    def _handle_ConnectionDown(self, event):
        self.write_results(RESULT_FILE)


# Register component to POX core object
def launch():
    """
    Starts the component
    """

    def start_ids_logger(event):
        log.debug('IDS Logger started')
        core.registerNew(IDSMetricLogger, event.connection)

    core.openflow.addListenerByName('ConnectionUp', start_ids_logger)
