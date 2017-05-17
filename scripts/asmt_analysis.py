import pandas as pd
import numpy as np

# read in data
names = ['amt_asmt_id','asmt_id','turker_id','hit_id','asmt_start','asmt_end']
asmt_data = pd.read_csv('../data/asmts.csv', names=names)

# subset for only the 9 HITs from our experiment
included_hit_ids = ['3JVP4ZJHDQVB4NBPOU71456F3LMI01',
					'3Z33IC0JC1PYMNJ2NXPDC5X2ERC9V1',
					'3XUSYT70IU4UWCV3WG6QD8Q2BGED0U',
					'3HFWPF5AKAMWFTDICTJYA5A9FV8S3Y',
					'367O8HRHKHBHXPWMC7OHKA2FTV4S4J',
					'32FESTC2NIT07615URPZI9WR656UCE',
					'3UEDKCTP9WTGST1X9WDMW0VF33HK7E',
					'3NCN4N1H1HK42BPQJQHITUYFGODNB8',
					'3YZ7A3YHR6WZT80MQC7RP28TTRZS5O']
asmt_data = asmt_data[asmt_data.hit_id.isin(included_hit_ids)]

print 'Number of assignments per HIT:'
print asmt_data.groupby('hit_id').apply(lambda x: len(x))

# correctly format start and end time from strings and compute time to complete each assignment
#pd.options.mode.chained_assignment = None # removes warning about assigning to copy of a slice
asmt_data['asmt_start'] = pd.to_datetime(asmt_data['asmt_start'], format='%Y-%m-%d %H:%M:%S')
asmt_data['asmt_end'] = pd.to_datetime(asmt_data['asmt_end'], format='%Y-%m-%d %H:%M:%S')
asmt_data['duration'] = asmt_data['asmt_end'] - asmt_data['asmt_start']
asmt_data['minutes'] = asmt_data.duration / pd.to_timedelta(1, 'm')
#pd.options.mode.chained_assignment = 'warn'

# print out some summary statistics
print 'mean time to complete: %.2f minutes' % asmt_data.minutes.mean()
print 'median time to complete: %.2f minutes' % asmt_data.minutes.median()
print 'last HIT finished at: ' + str(asmt_data.asmt_end.max())

# plot histogram of completion times using ggplot
from ggplot import *
plot = ggplot(asmt_data, aes(x='minutes')) + geom_histogram() + theme_bw() +\
	labs(x='Minutes', y='Frequency') +\
	ggtitle(element_text(text='Turker HIT Completion Times', size=20))
plot.show()

# plot histogram of completion times using pandas
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')
asmt_data.minutes.plot(kind='hist', legend=False, title='Turker HIT Completion Times', yticks=range(0,22,3),bins=13,xlim=[0,30])
plt.show()
