import csv
import os
import glob

DATA_PATH = '../training_data/IDS2012'
CLASSIFIER_FILE = './adaboost-ids.pkl'
PROTOCOLS = {'ICMP ': 0, 'IGMP ': 1, 'ICMP6': 3, 'TCP  ': 4, 'UDP  ': 5}


def load_validation_set(data_path):
    csv_path = os.path.join(data_path, '*.csv')
    dataset = []
    classifications = []
    for file in glob.glob(csv_path):
        with open(file, 'r') as csv_file:
            temp = csv.DictReader(csv_file)
            for item in temp:
                correctly_ordered_list = list()
                classifications.append(convert_class(item['label']))
                correctly_ordered_list.append(item['Dst Pt'])
                correctly_ordered_list.append(item['Dst IP Addr'])
                correctly_ordered_list.append(item['Src Pt'])
                correctly_ordered_list.append(item['Src IP Addr'])
                protocol_one_hot = [0, 0, 0, 0, 0, 0]
                protocol_one_hot[PROTOCOLS[item['Proto']]] = 1
                correctly_ordered_list += protocol_one_hot
                print correctly_ordered_list
                dataset.append(correctly_ordered_list)
    return dataset, classifications


def convert_class(x):
    return int(x not in ['normal', 'Normal'])


validation_flows, labels = load_validation_set(DATA_PATH)
