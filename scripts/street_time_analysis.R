# read in data
classes <- c("numeric", "character", "character", replicate(4, "numeric"))
names <- c("street.edge.id", "start.time", "end.time", "long1", "lat1", "long2", "lat2")
street.data <- read.csv("../data/street_length_data.csv", colClasses = classes, col.names = names)

# correctly format start and end time from strings
street.data$start.time <- strptime(street.data$start.time, format = "%Y-%m-%d %H:%M:%OS")
street.data$end.time <- strptime(street.data$end.time, format = "%Y-%m-%d %H:%M:%OS")

# calculate time it took to audit the street (duration), distance between
# endpoints of street, minutes per km, and speed
library("geosphere") # for distHaversine
street.data$duration <- street.data$end.time - street.data$start.time
street.data$dist <- distHaversine(street.data[,c("long1", "lat1")],
                                  street.data[,c("long2","lat2")])
street.data$min.per.km <- (as.numeric(street.data$duration)/60)/(street.data$dist/1000)
street.data$speed <- street.data$dist / as.numeric(street.data$duration)

# throw out the data with unreasonably long time to completion (threw out those
# over an hour, but there were a lot that were on the order of a year because of
# a bug manifesting itself in the earlier data) and unreasonably high speeds
# (anything above 7.5m/s right now)
street.data <- subset(street.data, duration < 3600)
street.data <- subset(street.data, speed < 7.5)

# this is the number we care about, median minutes per km, can be used to
# compute how much to pay for missions of a given distance (given a wage)
median(street.data$min.per.km)



# these are a few plots to look at the data, uncomment what you care about
#library(ggplot2)
#dist.plot <- ggplot(data = street.data, aes(dist)) +
#  geom_histogram() + theme_bw()
#dist.plot

#time.plot <- ggplot(data = street.data, aes(duration)) +
#  geom_histogram() + theme_bw() + xlim(0,1000)
#time.plot

#speed.plot <- ggplot(data = street.data, aes(speed)) +
#  geom_histogram() + theme_bw()
#speed.plot

#mpk.plot <- ggplot(data = street.data, aes(min.per.km)) +
#  geom_histogram() + theme_bw() + xlim(-10,500)
#mpk.plot