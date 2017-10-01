import os
import pandas as pd
import json
import glob
from datetime import datetime
from collections import defaultdict
from sklearn import ensemble
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib

DATA_PATH = os.path.join('../data', 'IDS2012')

def load_data_set(data_path):
    json_path = os.path.join(data_path, '*.json')
    dataset = []
    for fn in glob.glob(json_path):
        file = fn.split('/')[-1].split('.')[0]
        print file
        dataset += json.load(open(fn, 'r')).get('dataroot').get(file)
    return dataset

def generate_arr(dataset, classification):
    classification_arr = dataset[classification].values
    del dataset[classification]
    dataset_arr = dataset.values

    return dataset_arr, classification_arr

def convert_class(x):
    return int(x != 'Normal')

def convert_direction(x):
    return int(x != 'L2R')

def calculate_duration(start, stop):
    dt = datetime.strptime(stop, '%Y-%m-%dT%H:%M:%S') - datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
    return dt.total_seconds()

#Load training data
flows = load_data_set(DATA_PATH)

#Clean training data
targets = []
features = []
ip_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
for flow in flows:
    # Delete unnecessary features
    del flow['appName']
    del flow['sourcePayloadAsBase64']
    del flow['sourcePayloadAsUTF']
    del flow['destinationPayloadAsBase64']
    del flow['destinationPayloadAsUTF']
    del flow['sourceTCPFlagsDescription']
    del flow['destinationTCPFlagsDescription']

    # Count total number of IP address occurences
    ip_counts['source'][flow['source']] += 1
    ip_counts['destination'][flow['destination']] += 1

    # Convert into more appropriate features
    flow['direction'] = convert_direction(flow['direction'])
    flow['duration'] = calculate_duration(flow.pop('startDateTime'), flow.pop('stopDateTime'))
    flow['Tag'] = convert_class(flow['Tag'])

for flow in flows:
    flow['source_ip_count'] = ip_counts['source'][flow.pop('source')]
    flow['destination_ip_count'] = ip_counts['destination'][flow.pop('destination')]

temp = pd.DataFrame.from_dict(flows)
data = pd.get_dummies(temp, prefix=['protocol'], columns=['protocolName'])
print data

train_len = 95000
packets = data[:train_len]
test_packets = data[train_len:]

#Generate arrays
packets_arr, classification_arr = generate_arr(packets, 'Tag')
test_packets_arr, test_classification_arr = generate_arr(test_packets, 'Tag')

#Train classifier
clf = ensemble.AdaBoostClassifier()
clf.fit(packets_arr, classification_arr)

#Test classifier
pred = clf.predict(test_packets_arr)

#Check accuracy
accuracy = accuracy_score(test_classification_arr, pred)
print(accuracy)

#Save model
joblib.dump(clf, 'adaboost-ids.pkl')
