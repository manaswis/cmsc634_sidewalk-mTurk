import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys
from scipy.cluster.hierarchy import linkage, cut_tree, dendrogram
from collections import Counter


MAJORITY_THRESHOLD = 3

# read in data
label_data = pd.read_csv('../data/ground_truth-problem_labels.csv')

# let's just look at CurbRamp labels
included_types = ['CurbRamp']
label_data = label_data[label_data.label_type.isin(included_types)]

# print out some useful info
print 'Number of CurbRamp labels: ' + str(sum(label_data.label_type == 'CurbRamp'))

# put lat-lng in a tuple so it plays nice w/ haversine function
label_data['coords'] = label_data.apply(lambda x: (x.lat, x.lng), axis = 1)
label_data['id'] =  label_data.index.values

# create distance matrix between all pairs of labels
haver_vec = np.vectorize(haversine, otypes=[np.float64])
dist_matrix = label_data.groupby('id').apply(lambda x: pd.Series(haver_vec(label_data.coords, x.coords)))

# cluster based on distance and maybe label_type
label_link = linkage(dist_matrix, method='complete')

# cuts tree so that only labels less than 0.5m apart are clustered, adds a col
# to dataframe with label for the cluster they are in
label_data['cluster'] = cut_tree(label_link, height = 0.025) # clusters w/ 25m diameters

# Majority vote to decide what is included. If a cluster has at least 3 people agreeing on the type
# of the label, that is included. Any less, and we add it to the list of problem_clusters, so that
# we can look at them by hand through the admin interface to decide.
included_labels = [] # list of tuples (label_type, lat, lng)
problem_label_indices = [] # list of indices in dataset of labels that need to be verified
clusters = label_data.groupby('cluster')
total_dups = 0
for clust_num, clust in clusters:
	#count up the number of each label type in cluster, any with a majority are included
	for label_type in included_types:
		if len(clust) >= MAJORITY_THRESHOLD:
			ave = np.mean(clust['coords'].tolist(), axis=0) # use ave pos of clusters
			included_labels.append((label_type, ave[0], ave[1]))
			print 'Here is a new cluster:'
			print clust[['label_id','turker_id','route_id','pano_id']] #no_dups #clust
			print
		else:
			problem_label_indices.extend(clust.index)

print 'total number of clusters = ' + str(len(included_labels))


sys.exit()
