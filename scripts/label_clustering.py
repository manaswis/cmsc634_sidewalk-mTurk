import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys
from scipy.cluster.hierarchy import linkage, cut_tree, dendrogram

from collections import Counter

# read in data
f = open('../data/label_data.csv')
names = ["lng", "lat", "label_type", "user_id"]
data = np.genfromtxt(f, delimiter=',', names=names, case_sensitive=True, dtype=None)
f.close()

label_data = pd.DataFrame(data, columns=data.dtype.names)

# remove weird entries with longitude values on the order of 10^14
label_data = label_data.drop(label_data[label_data.lng > 360].index)

# put lat-lng in a tuple so it plays nice w/ haversine function
label_data['coords'] = label_data.apply(lambda x: (x.lat, x.lng), axis = 1)
label_data['id'] =  label_data.index.values

# sample data so that distance matrix isn't too large to fit in memory
label_sample = label_data.sample(1000)

# create distance matrix between all pairs of labels
haver_vec = np.vectorize(haversine, otypes=[np.float64])
dist_matrix = label_sample.groupby('id').apply(lambda x: pd.Series(haver_vec(label_sample.coords, x.coords)))

# cluster based on distance and maybe label_type
# TODO decided on a method of clustering
label_link = linkage(dist_matrix)

# cuts tree so that only labels less than 0.5m apart are clustered, adds a col
# to dataframe with label for the cluster they are in
label_sample['cluster'] = cut_tree(label_link, height = 0.5)

# Majority vote to decide what is included. If a cluster has at least 3 people agreeing on the type
# of the label, that is included. Any less, and we add it to the list of problem_clusters, so that
# we can look at them by hand through the admin interface to decide.
included_labels = {} # key: cluster_number, value: (label_type, lat, lng)
problem_clusters = {} # key: cluster_number, value: indices or labels in the cluster
clusters = label_sample.groupby('cluster')
for clust_num, clust in clusters:
	# TODO check for and remove duplicate labels from same user (prob need to check if same session)
	# if at least 3 out of the 5 had this label, include it
	label_type, num_of_label_type = Counter(clust['label_type']).most_common(1)[0]
	if num_of_label_type > 2:
		ave = np.mean(clust['coords'].tolist(), axis=0)
		included_labels[clust_num] = (label_type, ave[0], ave[1])
	else:
		problem_clusters[clust_num] = clust.index

# output the labels that we are sure are in the ground truth as a csv
included = pd.DataFrame(included_labels.values(), columns=['type', 'lat', 'lng'])
included.to_csv('../data/ground_truth.csv', index=False)

sys.exit()