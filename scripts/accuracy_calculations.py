import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys
from hopcroftkarp import HopcroftKarp # easy_install hopcroftkarp

# read in ground truth
ground_truth = pd.read_csv('../data/ground_truth-part1.csv')
# read in turker labels
turker_labels = pd.read_csv('../data/turker-final.csv')

# put lat-lng in a tuple so it plays nice w/ haversine function
ground_truth['coords'] = ground_truth.apply(lambda x: (x.lat, x.lng), axis = 1)
turker_labels['coords'] = turker_labels.apply(lambda x: (x.lat, x.lng), axis = 1)

# 
ground_truth['id'] = 'g' + ground_truth.index.astype(str)
turker_labels['id'] = 't' + turker_labels.index.astype(str)

# each graph is a dictionary with the key being the id of label in ground truth, and the value being
# a list of ids for labels in the turker label set that could be matched to it.
binary_graph = dict(zip(ground_truth.id, [[] for i in range(len(ground_truth))]))
multi_graph = dict(zip(ground_truth.id, [[] for i in range(len(ground_truth))]))

# binary: for every ground truth label, find which turker labels are less than 0.5 meters away
for row in ground_truth.iterrows():
	match = turker_labels.apply(lambda x: haversine(x.coords, row[1].coords) < 0.5, axis=1)
	binary_graph[row[1].id].extend(turker_labels.id[match].values)

# compute maximum matching
binary_matching = HopcroftKarp(binary_graph).maximum_matching()

# calculate precision, recall, and f-measure
true_positive_binary = len(binary_matching) / 2 # number of matches
false_positive_binary = len(turker_labels) - true_positive_binary # unmatched turker labels
false_negative_binary = len(ground_truth) - true_positive_binary # unmatched ground truth labels

precision_binary = true_positive_binary / (1.0*true_positive_binary + false_positive_binary)
recall_binary = true_positive_binary / (1.0*true_positive_binary + false_negative_binary)
f_measure_binary = precision_binary * recall_binary / (precision_binary + recall_binary)


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

precision_multi = true_positive_multi / (1.0*true_positive_multi + false_positive_multi)
recall_multi = true_positive_multi / (1.0*true_positive_multi + false_negative_multi)
f_measure_multi = precision_multi * recall_multi / (precision_multi + recall_multi)


sys.exit()