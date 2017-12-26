import csv
import os
import glob
from collections import defaultdict
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score

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
                correctly_ordered_list.append(item.pop('Dst Pt'))
                correctly_ordered_list.append(item.pop('Dst IP Addr'))
                correctly_ordered_list.append(item.pop('Src Pt'))
                correctly_ordered_list.append(item.pop('Src IP Addr'))
                protocol_one_hot = [0, 0, 0, 0, 0, 0]
                protocol_one_hot[PROTOCOLS[item['Proto']]] = 1
                correctly_ordered_list += protocol_one_hot
                ip_counts['source'][correctly_ordered_list[3]] += 1
                ip_counts['destination'][correctly_ordered_list[1]] += 1
                port_counts['source'][correctly_ordered_list[2]] += 1
                port_counts['destination'][correctly_ordered_list[0]] += 1
                dataset.append(correctly_ordered_list)
    return dataset, classifications


def convert_class(x):
    return int(x not in ['normal', 'Normal'])


ip_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
port_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
validation_flows, labels = load_validation_set(DATA_PATH)

for flow in validation_flows:
    flow[3] = ip_counts['source'][flow[3]]
    flow[1] = ip_counts['destination'][flow[1]]
    flow[2] = port_counts['source'][flow[2]]
    flow[0] = port_counts['destination'][flow[0]]

clf = joblib.load(CLASSIFIER_FILE)
pred = clf.predict(validation_flows)
print 'Accuracy:', accuracy_score(labels, pred)
