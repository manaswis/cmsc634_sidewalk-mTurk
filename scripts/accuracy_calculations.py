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

# binary classification. any direct matches are a true positive, if nothing
# matches some ground truth label it is false negative, any turker labels not
# matched to a ground truth label is a false positive.
turk_left_binary = turker_labels.copy()
true_positive_binary = 0
false_negative_binary = 0
for row in ground_truth.iterrows():
	# get distance from this label in ground truth to every remaining turker label
	dists = turk_left_binary.apply(lambda x: haversine(x.coords, row[1].coords), axis=1)
	# check if the closest one is less than 0.5 meters away, if so it is true pos o/w false neg
	if dists.loc[dists.idxmin()] < 0.5:
		true_positive_binary += 1
		turk_left_binary = turk_left_binary.drop(dists.idxmin())
	else:
		false_negative_binary += 1

false_positive_binary = len(turk_left_binary)

# calculate precision, recall, and f-measure
precision_binary = true_positive_binary / (1.0*true_positive_binary + false_positive_binary)
recall_binary = true_positive_binary / (1.0*true_positive_binary + false_negative_binary)
f_measure_binary = precision_binary * recall_binary / (precision_binary + recall_binary)


# multiclass classification. direct matches with same label type are true
# positive, if nothing is close enough with same label type it is false
# negative, and any turker labels not matched to a ground truth label (including
# the ones that were close enough but had wrong type) are false positives.
turk_left_mutli = turker_labels.copy()
true_positive_multi = 0
false_negative_multi = 0
for row in ground_truth.iterrows():
	# get distance from this label in ground truth to every remaining turker label w/ same type
	same_type_labels = turk_left_mutli[turk_left_mutli.type == row[1].type]
	dists = same_type_labels.apply(lambda x: haversine(x.coords, row[1].coords), axis=1)
	# check if the closest one is less than 0.5 meters away, if so it is true pos o/w false neg
	if dists.loc[dists.idxmin()] < 0.5:
		true_positive_multi += 1
		turk_left_mutli = turk_left_mutli.drop(dists.idxmin())
	else:
		false_negative_multi += 1

false_positive_multi = len(turk_left_mutli)

# calculate precision, recall, and f-measure
precision_multi = true_positive_multi / (1.0*true_positive_multi + false_positive_multi)
recall_multi = true_positive_multi / (1.0*true_positive_multi + false_negative_multi)
f_measure_multi = precision_multi * recall_multi / (precision_multi + recall_multi)


sys.exit()