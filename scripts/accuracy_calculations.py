import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys

# read in ground truth
f = open('../data/ground_truth.csv')
names = ["label_type", "lng", "lat"]
data = np.genfromtxt(f, delimiter=',', names=names, case_sensitive=True, dtype=None)
f.close()
ground_truth = pd.DataFrame(data, columns=data.dtype.names)
# read in turker labels
f = open('../data/ground_truth.csv')
names = ["label_type", "lng", "lat"]
data = np.genfromtxt(f, delimiter=',', names=names, case_sensitive=True, dtype=None)
f.close()
turker_labels = pd.DataFrame(data, columns=data.dtype.names)

sys.exit()