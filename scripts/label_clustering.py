import pandas as pd
import numpy as np
from haversine import haversine # pip install haversine
import sys
from scipy.cluster.hierarchy import linkage, fcluster, cut_tree, dendrogram
from scipy.spatial.distance import pdist
from collections import Counter
import argparse

GROUND_TRUTH = 1
TURKER = 2
CLUSTER_THRESHOLD = 0.005 # cluster all labels within 5 meter diameter

# read in arguments from command line
parser = argparse.ArgumentParser(description='Takes a set of labels from CSV, and outputs the labels grouped into clusters to a new CSV')
parser.add_argument('data_source', type=str,
                    help='Indicate whether to use ground truth (-gt) or turker (-t) data.')
parser.add_argument('--clust_thresh', type=float, default=0.005,
                    help='Cluster distance threshold (in meters)')
parser.add_argument('--debug', action='store_true',
                    help='Debug mode adds print statements')
parser.add_argument('--to_csv', action='store_true',
                    help='Output results of clustering to CSV')
parser.add_argument('--validate', action='store_true',
                    help='Test many different thesholds and create graphs')
args = parser.parse_args()
DEBUG = args.debug
CLUSTER_THRESHOLD = args.clust_thresh
TO_CSV = args.to_csv
VALIDATE = args.validate
if args.data_source in ['gt', 'GT', 'ground_truth', 'groundTruth', 'groundtruth', 'g',
					   '-gt', '-GT', '-ground_truth', '-groundTruth', '-groundtruth', '-g']:
    data = GROUND_TRUTH
    MAJORITY_THRESHOLD = 2
elif args.data_source in ['turker', 'turk', 't', '-turker', '-turk', '-t']:
	data = TURKER
	MAJORITY_THRESHOLD = 5
else:
	parser.error('Try passing \'gt\' for ground truth labels or \'t\' for turker labels')

# read in data
names = ['lng','lat','label_type', 'label_id','asmt_id','turker_id','route_id','hit_id','pano_id','canvas_x','canvas_y','heading','pitch','completed']
label_data = pd.read_csv('../data/mturk_labels.csv', names=names)

# subset data to remove onboarding pano ids
onboarding_pano_ids = ['stxXyCKAbd73DmkM2vsIHA', 'bdmGHJkiSgmO7_80SnbzXw']
label_data = label_data[~label_data.pano_id.isin(onboarding_pano_ids)]

# more subsetting...
if data == GROUND_TRUTH:
	# subset for the three researchers, on the 9 routes from the experiment, removing 2 duplicates,
	# and only including instances where we completed the route
	included_turkers = ['A2WCCAZBCSIW0R','APQS1PRMDXAFH','A2PWQI6I9D3S6D']
	included_routes = [55, 164, 220, 253, 342, 38, 460, 441, 411]
	excluded_asmt_ids = ['3SBEHTYCWO6AO254M4I2RZCIGBOIYK', '3P4MQ7TPPYF4OMYN62C1X1A40CMBBP ']
	label_data = label_data[label_data.turker_id.isin(included_turkers)]
	label_data = label_data[label_data.route_id.isin(included_routes)]
	label_data = label_data[~label_data.asmt_id.isin(excluded_asmt_ids)]
	label_data = label_data[label_data.completed == 't']
elif data == TURKER:
	# subset for the exact assignment IDs, as provided by results from Amazon
	amazon_results = pd.read_csv('../data/results_16-05-2017_22:27:41.csv')
	label_data = label_data[label_data.asmt_id.isin(amazon_results.AssignmentId)]
	# subset for labels from the 9 HITs in the experiment
	# included_hit_ids = ['3JVP4ZJHDQVB4NBPOU71456F3LMI01',
	# 					'3Z33IC0JC1PYMNJ2NXPDC5X2ERC9V1',
	# 					'3XUSYT70IU4UWCV3WG6QD8Q2BGED0U',
	# 					'3HFWPF5AKAMWFTDICTJYA5A9FV8S3Y',
	# 					'367O8HRHKHBHXPWMC7OHKA2FTV4S4J',
	# 					'32FESTC2NIT07615URPZI9WR656UCE',
	# 					'3UEDKCTP9WTGST1X9WDMW0VF33HK7E',
	# 					'3NCN4N1H1HK42BPQJQHITUYFGODNB8',
	# 					'3YZ7A3YHR6WZT80MQC7RP28TTRZS5O']
	# label_data = label_data[label_data.hit_id.isin(included_hit_ids)]

# remove other, occlusion, and no sidewalk label types to make analysis for the class project easier
included_types = ['CurbRamp', 'SurfaceProblem', 'Obstacle', 'NoCurbRamp']
label_data = label_data[label_data.label_type.isin(included_types)]

# remove NAs
label_data.dropna(inplace=True)

# remove weird entries with longitude values (on the order of 10^14)
if sum(label_data.lng > 360) > 0:
	print 'There are %d invalid longitude values, removing those entries.' % sum(label_data.lng > 360)
	label_data = label_data.drop(label_data[label_data.lng > 360].index)

# print out some useful info
if DEBUG:
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

def cluster(clust_thresh):
	# cuts tree so that only labels less than 5 m apart are clustered, adds a col
	# to dataframe with label for the cluster they are in
	label_data['cluster'] = fcluster(label_link, t=clust_thresh, criterion='distance')
	#print pd.DataFrame(pd.DataFrame(label_data.groupby('cluster').size().rename('points_count')).groupby('points_count').size().rename('points_count_frequency'))

	# Majority vote to decide what is included. If a cluster has at least 3 people agreeing on the type
	# of the label, that is included. Any less, and we add it to the list of problem_clusters, so that
	# we can look at them by hand through the admin interface to decide.
	included_labels = [] # list of tuples (label_type, lat, lng)
	problem_label_indices = [] # list of indices in dataset of labels that need to be verified
	clusters = label_data.groupby('cluster')
	total_dups = 0
	for clust_num, clust in clusters:
		# only include one label type per user per cluster
		no_dups = clust.drop_duplicates(subset=['label_type', 'turker_id'])
		total_dups += (len(clust) - len(no_dups))
		#count up the number of each label type in cluster, any with a majority are included
		for label_type in included_types:
			single_type_clust = no_dups.drop(no_dups[no_dups.label_type != label_type].index)
			if len(single_type_clust) >= MAJORITY_THRESHOLD:
				ave = np.mean(single_type_clust['coords'].tolist(), axis=0) # use ave pos of clusters
				included_labels.append((label_type, ave[0], ave[1]))
			else:
				#print single_type_clust.index
				problem_label_indices.extend(single_type_clust.index)

	if DEBUG:
		print 'total duplicates: ' + str(total_dups)
		print 'Total agreements by label type:'

	included = pd.DataFrame(included_labels, columns=['type', 'lat', 'lng'])
	if DEBUG: print included.iloc[:,0].value_counts()

	# output the labels from majority vote as a csv
	if TO_CSV:
		included = pd.DataFrame(included_labels, columns=['type', 'lat', 'lng'])
		if data == GROUND_TRUTH:
			if DEBUG: print 'We agreed on this many labels: ' + str(len(included))

			#included.to_csv('../data/ground_truth-part1.csv', index=False)
			included.to_csv('../data/ground_truth-final.csv', index=False)

			# order GT labels that we are unsure about by cluster, so they are easier to manually look through.
			problem_labels = label_data.loc[problem_label_indices]
			if DEBUG: print 'We have this many labels that we disagreed on: ' + str(len(problem_labels))

			# output GT labels that we are NOT sure about to another CSV so we can look through them.
			problem_labels.to_csv('../data/ground_truth-problem_labels.csv', index=False)
		elif data == TURKER:
			if DEBUG: print 'Turkers agreed on this many labels: ' + str(len(included))
			if DEBUG: print 'Turkers have this many labels that they disagreed on: ' + str(len(problem_label_indices))
			included.to_csv('../data/turker-final.csv', index=False)

cluster(CLUSTER_THRESHOLD)

sys.exit()
