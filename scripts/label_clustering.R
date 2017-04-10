# read in data
classes <- c("numeric", "numeric", "factor", "factor")
names <- c("lng", "lat", "label.type", "user.id")
label.data <- read.csv("../data/label_data.csv", colClasses = classes, col.names = names)

# remove weird entries with longitude values on the order of 10^14
label.data <- label.data[label.data$lng < 360,]

# sample data so that distance matrix isn't too large to fit in memory
sample.label.data <- label.data[sample(nrow(label.data), 5000),]


# cluster based on distance and maybe label type
library("geosphere")
dist.matrix <- distm(x = sample.label.data[,c("lng","lat")], fun = distHaversine) # get distance matrix b/w all labels
hc <- hclust(as.dist(dist.matrix)) # do clustering
#plot(hc) # not really useful unless using to visualize small number of labels
cut <- cutree(hc, h = 0.5) # cuts tree so that only labels less than 0.5m apart are clustered
max(cut) # shows total number of clusters
sort(table(cut), decreasing=TRUE)[1:3] # shows largest clusters (top row is cluster "id", bottom is number of labels in cluster)
sample.label.data[cut %in% names(sort(table(cut), decreasing=TRUE)[1]),] # shows csv entries for biggest cluster


# majority vote to determine what is included
