import pandas as pd
import numpy as np
import sys

# read in ground truth
gtp1 = pd.read_csv('../data/ground_truth-part1.csv')
gtp2 = pd.read_csv('../data/problem_labels.csv')

# convert coords from string to tuple of floats
gtp1.coords = gtp1.apply(lambda x: tuple(map(float, x.coords[1:-1].split(', '))), axis=1)
gtp2.coords = gtp2.apply(lambda x: tuple(map(float, x.coords[1:-1].split(', '))), axis=1)

# gets average lat-long position from labels in a data frame
# return: tuple (label_type, lat, long)
def average_label(df):
	average_latlng = np.mean(df['coords'].tolist(), axis=0)
	return (df.label_type.iloc[0], average_latlng[0], average_latlng[1])

# get representative point for each cluster from average
gtp2 = gtp2.groupby('cluster').apply(average_label)
#gtp2.groupby('cluster', as_index=False, group_keys=False).apply(average_label)

# combine the two ground truth data sets
ground_truth = pd.concat(gtp1, gtp2)

# output combined ground truth labels as a CSV
included.to_csv('../data/ground_truth-final.csv', index=False)

sys.exit()
