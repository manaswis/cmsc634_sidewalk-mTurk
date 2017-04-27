import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys
from scipy.cluster.hierarchy import linkage, cut_tree, dendrogram

# read in data
f = open('../data/label_data.csv')
names = ["lng", "lat", "label.type", "user.id"]
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

# cluster based on distance and maybe label type
label_link = linkage(dist_matrix)

# cuts tree so that only labels less than 0.5m apart are clustered, adds a col
# to dataframe with label for the cluster they are in
label_sample['cluster'] = cut_tree(label_link, height = 0.5)

# TODO majority vote to determine what is included

sys.exit()