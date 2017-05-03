import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys

# read in ground truth
ground_truth = pd.read_csv('../data/ground_truth.csv')
# read in turker labels
turker_labels = pd.read_csv('../data/ground_truth.csv')

# put lat-lng in a tuple so it plays nice w/ haversine function
ground_truth['coords'] = ground_truth.apply(lambda x: (x.lat, x.lng), axis = 1)
turker_labels['coords'] = turker_labels.apply(lambda x: (x.lat, x.lng), axis = 1)

gt_left = ground_truth.copy()
turk_left = turker_labels.copy()

# binary classification. any direct matches are a true positive, if nothing
# matches some ground truth label, it is false_negative, any turker labels not
# matched to a ground truth label is a false positive.
true_positive = 0
false_negative = 0
for row in ground_truth.iterrows():
	dists = turk_left.apply(lambda x: haversine(x.coords, row[1].coords), axis=1)
	if dists.loc[dists.idxmin()] < 0.5:
		true_positive += 1
		turk_left = turk_left.drop(dists.idxmin())
	else:
		false_negative += 1

false_positive = len(turk_left)

sys.exit()