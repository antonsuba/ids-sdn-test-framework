import os
import json
import glob
import gc

DATA_PATH = os.path.join('../training_data', 'DDOS-Flows')
ATTACK_HOSTS_FILE = '../config/attack_hosts.txt'

def extract_attack_hosts(data_path):
    json_path = os.path.join(data_path, '*.json')
    attack_hosts = set()
    attack_file = open(ATTACK_HOSTS_FILE, 'w')
    total_hosts = 0

    for file in glob.glob(json_path):
        filename = file.split('/')[-1].split('.')[0]
        json_file = None
        temp = None
        try:
            json_file = open(file, 'r')
            temp = json.load(json_file).get('dataroot').get(filename)

            for item in temp:
                total_hosts += 1
                if item['Tag'] == 'Attack':
                    attack_hosts.add(str(item['source']))

        finally:
            if json_file is not None:
                json_file.close()
                json_file = None

    attack_file.write(total_hosts + '\n')
    for ip in attack_hosts:
        attack_file.write(ip + '\n')

    attack_file.close()

extract_attack_hosts(DATA_PATH)
