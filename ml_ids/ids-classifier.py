import os
import pandas as pd
import json
import glob
import gc
from datetime import datetime
from collections import defaultdict
from sklearn import ensemble
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib

DATA_PATH = os.path.join('../data', 'IDS2012')


def load_data_set(data_path):
    json_path = os.path.join(data_path, '*.json')
    dataset = []
    for file in glob.glob(json_path):
        filename = file.split('/')[-1].split('.')[0]
        json_file = None
        temp = None
        try:
            json_file = open(file, 'r')
            temp = json.load(json_file).get('dataroot').get(filename)

            # Clean dataset
            for item in temp:
                # Delete unnecessary features
                del item['appName']
                del item['sourcePayloadAsBase64']
                del item['sourcePayloadAsUTF']
                del item['destinationPayloadAsBase64']
                del item['destinationPayloadAsUTF']
                del item['sourceTCPFlagsDescription']
                del item['destinationTCPFlagsDescription']

                # Count total number of IP address occurences
                ip_counts['source'][item['source']] += 1
                ip_counts['destination'][item['destination']] += 1

                # Convert into more appropriate features
                item['direction'] = convert_direction(item['direction'])
                item['duration'] = calculate_duration(
                    item.pop('startDateTime'), item.pop('stopDateTime'))
                item['Tag'] = convert_class(item['Tag'])

                # Delete features for prototype
                del item['totalSourceBytes']
                del item['totalDestinationBytes']
                del item['totalDestinationPackets']
                del item['totalSourcePackets']
                del item['direction']

            dataset += temp
        finally:
            if json_file is not None:
                json_file.close()
                json_file = None
                gc.collect()
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
    dt = datetime.strptime(stop, '%Y-%m-%dT%H:%M:%S') - datetime.strptime(
        start, '%Y-%m-%dT%H:%M:%S')
    return dt.total_seconds()


# Load training data
ip_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
flows = load_data_set(DATA_PATH)

for flow in flows:
    flow['source_ip_count'] = ip_counts['source'][flow.pop('source')]
    flow['destination_ip_count'] = ip_counts['destination'][flow.pop(
        'destination')]

temp = pd.DataFrame.from_dict(flows)
data = pd.get_dummies(temp, prefix=['protocol'], columns=['protocolName'])
del data['sensorInterfaceId']
del data['startTime']
print data

train_len = 1500000
packets = data[:train_len]
test_packets = data[train_len:]

# Generate arrays
packets_arr, classification_arr = generate_arr(packets, 'Tag')
test_packets_arr, test_classification_arr = generate_arr(test_packets, 'Tag')

# Train classifier
clf = ensemble.AdaBoostClassifier()
clf.fit(packets_arr, classification_arr)

# Test classifier
pred = clf.predict(test_packets_arr)

# Check accuracy
accuracy = accuracy_score(test_classification_arr, pred)
print 'Accuracy:', accuracy

# Save model
joblib.dump(clf, 'adaboost-ids.pkl')
