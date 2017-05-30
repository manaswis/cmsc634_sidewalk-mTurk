import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys
from scipy.cluster.hierarchy import linkage, fcluster, cut_tree, dendrogram
from scipy.spatial.distance import pdist
from collections import Counter

CLUSTER_THRESHOLD = 0.020 # cluster all labels within 15 meter diameter


# read in data
label_data = pd.read_csv('../data/ground_truth-problem_labels.csv')

# let's just look at CurbRamp labels
included_types = ['CurbRamp', 'SurfaceProblem', 'Obstacle', 'NoCurbRamp']
label_data = label_data[label_data.label_type.isin(included_types)]

# print out some useful info
print 'labels in dataset: ' + str(len(label_data))
print 'Number of CurbRamp labels: ' + str(sum(label_data.label_type == 'CurbRamp'))
print 'Number of NoCurbRamp labels: ' + str(sum(label_data.label_type == 'NoCurbRamp'))
print 'Number of SurfaceProblem labels: ' + str(sum(label_data.label_type == 'SurfaceProblem'))
print 'Number of Obstacle labels: ' + str(sum(label_data.label_type == 'Obstacle'))

# put lat-lng in a tuple so it plays nice w/ haversine function
label_data['coords'] = label_data.apply(lambda x: (x.lat, x.lng), axis = 1)
label_data['id'] =  label_data.index.values

# create distance matrix between all pairs of labels
latlngs = np.array(label_data[['lat','lng']].as_matrix())
dist_matrix = pdist(latlngs,lambda x,y: haversine(x,y))

# cluster based on distance and maybe label_type
label_link = linkage(dist_matrix, method='complete')

# cuts tree so that only labels less than 20m apart are clustered, adds a col
# to dataframe with label for the cluster they are in
label_data['cluster'] = fcluster(label_link, t=CLUSTER_THRESHOLD, criterion='distance')

# sort by cluster ID
label_data = label_data.sort_values('cluster')

print 'total number of clusters = ' + str(max(label_data['cluster']))

label_data.to_csv('../data/ground_truth-problem_labels-clustered.csv', index=False)


sys.exit()
