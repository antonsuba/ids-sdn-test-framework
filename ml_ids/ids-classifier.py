import json
import csv
import yaml
import os
import inspect
import glob
import gc
import copy
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict
from sklearn import ensemble
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split

DATA_PATH = 'training_data'
CONFIG = '../config/config.yml'
DIRNAME = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))


def load_data_set(data_path):

    data_path = os.path.join(data_path, cfg['training-dataset-folder'],
                             '*.' + cfg['training-data-filetype'])
    dataset = []
    for file in glob.glob(data_path):
        data_file = None
        temp = None

        with open(file, 'r') as data_file:
            if cfg['training-data-filetype'] == 'json':
                temp = json.load(data_file)
            else:
                temp = csv.DictReader(data_file)
            print 'Reading file:', file.split('/')[-1]

            # Clean dataset
            for item in temp:
                # Delete unnecessary features
                for key in item.keys():
                    if key not in features.values():
                        del item[key]

                # Count total number of IP address and port occurences
                ip_counts['source'][item[features['source-ip']]] += item[
                    features['source-packet-count']]
                ip_counts['destination'][item[features[
                    'destination-ip']]] += item[features[
                        'source-packet-count']]
                port_counts['source'][item[features['source-port']]] += item[
                    features['source-packet-count']]
                port_counts['destination'][item[features[
                    'destination-port']]] += item[features[
                        'source-packet-count']]

                item[features['label']] = convert_class(
                    item[features['label']])

                for p in range(item.pop(features['source-packet-count'])):
                    dataset += [item.copy()]

    return dataset


def convert_class(x):
    return int(x != 'Normal')


with open(os.path.join(DIRNAME, CONFIG), 'r') as config_file:
    cfg = yaml.load(config_file).get('ml_ids').get('ids-classifier')
    features = cfg['feature-names']

# Load training data
ip_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
port_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
flows = load_data_set(os.path.join(DIRNAME, DATA_PATH))
for flow in flows:
    flow['source_ip_count'] = ip_counts['source'][flow.pop('source')]
    flow['destination_ip_count'] = ip_counts['destination'][flow.pop(
        'destination')]

    flow['source_port_count'] = port_counts['source'][flow.pop('sourcePort')]
    flow['destination_port_count'] = port_counts['destination'][flow.pop(
        'destinationPort')]

temp = pd.DataFrame.from_dict(flows)
data = pd.get_dummies(
    temp, prefix=['protocol'], columns=[features['protocol']])
data = data.reindex(
    columns=[
        features['label'], features['destination-ip'],
        features['destination-port'], 'source_ip_count', 'source_port_count',
        'protocol_icmp_ip', 'protocol_igmp', 'protocol_ip',
        'protocol_ipv6icmp', 'protocol_tcp_ip', 'protocol_udp_ip'
    ],
    fill_value=0)
print data
print data.corr()[features['label']].sort_values(ascending=False)

y = data[features['label']].values
del data[features['label']]
X_train, X_test, y_train, y_test = train_test_split(
    data, y, stratify=y, test_size=0.2)

# Train classifier
clf = ensemble.AdaBoostClassifier()
clf.fit(X_train, y_train)

# Test classifier
pred = clf.predict(X_test)
unique, counts = np.unique(pred, return_counts=True)
print dict(zip(unique, counts))

# Check accuracy
accuracy = accuracy_score(y_test, pred)
print 'Accuracy:', accuracy

# Save model
model_filename = raw_input('Save model as: ')
joblib.dump(clf, 'ids_models/%s.pkl', model_filename)
