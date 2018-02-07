import os
import pandas as pd
import json
import glob
import gc
import numpy as np
from datetime import datetime
from collections import defaultdict
from sklearn import ensemble
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split

DATA_PATH = '../training_data/IDS2012'


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

                # Count total number of IP address and port occurences
                ip_counts['source'][item['source']] += item[
                    'totalSourcePackets']
                ip_counts['destination'][item['destination']] += item[
                    'totalSourcePackets']
                port_counts['source'][item['sourcePort']] += item[
                    'totalSourcePackets']
                port_counts['destination'][item['destinationPort']] += item[
                    'totalSourcePackets']

                item['Tag'] = convert_class(item['Tag'])

                # Delete features for prototype
                del item['totalSourceBytes']
                del item['totalDestinationBytes']
                del item['totalDestinationPackets']
                del item['direction']
                del item['startDateTime']
                del item['stopDateTime']

            dataset += temp
        finally:
            if json_file is not None:
                json_file.close()
                json_file = None
                gc.collect()
    return dataset


def convert_class(x):
    return int(x != 'Normal')


# Load training data
ip_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
port_counts = {'source': defaultdict(int), 'destination': defaultdict(int)}
flows = load_data_set(DATA_PATH)

for flow in flows:
    flow['source_ip_count'] = ip_counts['source'][flow.pop('source')]
    flow['destination_ip_count'] = ip_counts['destination'][flow.pop(
        'destination')]

    flow['source_port_count'] = port_counts['source'][flow.pop('sourcePort')]
    flow['destination_port_count'] = port_counts['destination'][flow.pop(
        'destinationPort')]

temp = pd.DataFrame.from_dict(flows)
data = pd.get_dummies(temp, prefix=['protocol'], columns=['protocolName'])
del data['sensorInterfaceId']
del data['startTime']
print data

y = data['Tag'].values
del data['Tag']
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
joblib.dump(clf, 'adaboost-ids.pkl')
