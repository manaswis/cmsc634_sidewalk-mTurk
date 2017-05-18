import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys
from hopcroftkarp import HopcroftKarp # easy_install hopcroftkarp
import matplotlib.pyplot as plt
#from ggplot import *

# read in ground truth
ground_truth = pd.read_csv('../data/ground_truth-final.csv')
# read in turker labels
turker_labels = pd.read_csv('../data/turker-final.csv')
# ground_truth = pd.read_csv('../data/test-final.csv')
# turker_labels = pd.read_csv('../data/test-final.csv')

# put lat-lng in a tuple so it plays nice w/ haversine function
ground_truth['coords'] = ground_truth.apply(lambda x: (x.lat, x.lng), axis = 1)
turker_labels['coords'] = turker_labels.apply(lambda x: (x.lat, x.lng), axis = 1)

# add identifiers to the labels to use when matching them
ground_truth['id'] = 'g' + ground_truth.index.astype(str)
turker_labels['id'] = 't' + turker_labels.index.astype(str)

# each graph is a dictionary with the key being the id of label in ground truth, and the value being
# a list of ids for labels in the turker label set that could be matched to it.
binary_graph = dict(zip(ground_truth.id, [[] for i in range(len(ground_truth))]))
multi_graph = dict(zip(ground_truth.id, [[] for i in range(len(ground_truth))]))

# binary: for every ground truth label, find which turker labels are less than 0.5 meters away
for row in ground_truth.iterrows():
	match = turker_labels.apply(lambda x: haversine(x.coords, row[1].coords) < 0.0015, axis=1)
	binary_graph[row[1].id].extend(turker_labels.id[match].values)

# compute maximum matching
binary_matching = HopcroftKarp(binary_graph).maximum_matching()

def precision(true_pos, false_pos):
	if true_pos > 0 or false_pos > 0:
		return true_pos / (1.0 * true_pos + false_pos)
	else:
		return float('NaN')

def recall(true_pos, false_neg):
	if true_pos > 0 or false_neg > 0:
		return true_pos / (1.0 * true_pos + false_neg)
	else:
		return float('NaN')

def f_measure(true_pos, false_pos, false_neg):
	P = precision(true_pos, false_pos)
	R = recall(true_pos, false_neg)
	if P > 0 or R > 0:
		return 2 * P * R / (P + R)
	else:
		return float('NaN')

# calculate precision, recall, and f-measure
true_positive_binary = len(binary_matching) / 2 # number of matches
false_positive_binary = len(turker_labels) - true_positive_binary # unmatched turker labels
false_negative_binary = len(ground_truth) - true_positive_binary # unmatched ground truth labels

precision_binary = true_positive_binary / (1.0*true_positive_binary + false_positive_binary)
recall_binary = true_positive_binary / (1.0*true_positive_binary + false_negative_binary)
f_measure_binary = 2 * precision_binary * recall_binary / (precision_binary + recall_binary)
print precision_binary
print recall_binary
print f_measure_binary


# multiclass: for every ground truth label, find which turker labels have the same label type and
# are less than 0.5 meters away
for row in ground_truth.iterrows():
	match = turker_labels.apply(lambda x: x.type == row[1].type and haversine(x.coords, row[1].coords) < 0.5, axis=1)
	multi_graph[row[1].id].extend(turker_labels.id[match].values)

# compute maximum matching
multi_matching = HopcroftKarp(multi_graph).maximum_matching()

# calculate precision, recall, and f-measure
true_positive_multi = len(multi_matching) / 2 # number of matches
false_positive_multi = len(turker_labels) - true_positive_multi # unmatched turker labels
false_negative_multi = len(ground_truth) - true_positive_multi # unmatched ground truth labels

# calculate accuracies in the different classes
class_accuracies = {}
label_types = ['CurbRamp', 'SurfaceProblem', 'Obstacle', 'NoCurbRamp']
for label_type in label_types:
	gt_this_label = ground_truth[ground_truth.type == label_type]
	turk_this_label = turker_labels[turker_labels.type == label_type]
	true_pos = sum(gt_this_label.id.isin(multi_matching.keys()))
	false_pos = len(turk_this_label) - true_pos
	false_neg = len(gt_this_label) - true_pos
	class_accuracies[label_type] = {'p': precision(true_pos, false_pos),
									'r': recall(true_pos, false_neg),
									'f': f_measure(true_pos, false_pos, false_neg)}


precision_multi = true_positive_multi / (1.0*true_positive_multi + false_positive_multi)
recall_multi = true_positive_multi / (1.0*true_positive_multi + false_negative_multi)
f_measure_multi = 2.0 * precision_multi * recall_multi / (precision_multi + recall_multi)
print precision_multi
print recall_multi
print f_measure_multi

class_accuracies_df = pd.DataFrame.from_dict(class_accuracies, orient='index')
class_accuracies_df['label_type'] = pd.Series(class_accuracies_df.index, index=class_accuracies_df.index).astype('category')
print class_accuracies_df

# plot the accuracies by class as a bar chart
class_accuracies_df.plot(kind='bar',x='label_type')
plt.show()

sys.exit()