# read in data
classes <- c("factor", "factor", "character", "character",
             replicate(4, "numeric"))
names <- c("user.id", "street.edge.id", "start.time", "end.time",
           "long1", "lat1", "long2", "lat2")
street.data <- read.csv("../data/street_length_data.csv",
                        colClasses = classes,
                        col.names = names)

# correctly format start and end time from strings
street.data$start.time <- strptime(street.data$start.time,
                                   format = "%Y-%m-%d %H:%M:%OS")
street.data$end.time <- strptime(street.data$end.time,
                                 format = "%Y-%m-%d %H:%M:%OS")

# group by user ID and start time
# TODO group by IP address if anon user (97760883-8ef0-4309-9a5e-0c086ef27573)
street.data$duration <- as.difftime("00:00:00", units = "mins")
split <- split(street.data,
               list(street.data$user.id, as.character(street.data$start.time)),
               drop = TRUE)

# function that calculates the time spent on each street, where each entry in a
# data frame, x, are entries from the same user.id with the same start.time.
calculate.duration <- function(x) {
  # sort the entries by ending time
  x <- x[order(x$end.time),]
  # the first entry has a duration of end.time-start.time
  x[1,"duration"] <- difftime(x[1,"end.time"],
                              x[1,"start.time"],
                              units = "mins")
  # all remaining entries have duration end.time[i]-end.time[i-1]
  if (nrow(x) > 1) {
    x[2:nrow(x),"duration"] <- difftime(x[2:nrow(x),"end.time"],
                                        x[1:(nrow(x)-1),"end.time"],
                                        units = "mins")
  }
  x
}

# calculate duration for first in each group as end.time - start.time, and
# calculate duration for all remaining as end.time[i] - end.time[i-1]
split <- lapply(split, calculate.duration)

# put the data back together
street.data <- unsplit(split,
                       list(street.data$user.id, as.character(street.data$start.time)),
                       drop = TRUE)

# calculate  distance between endpoints of street, minutes per km, and speed
library("geosphere") # for distHaversine
#street.data$duration <- street.data$end.time - street.data$start.time
street.data$dist <- distHaversine(street.data[,c("long1", "lat1")],
                                  street.data[,c("long2","lat2")])
street.data$min.per.km <- (street.data$duration) / (street.data$dist/1000)
street.data$speed <- street.data$dist / (street.data$duration*60)

# throw out the data with unreasonably long time to completion (threw out those
# over 3 hours, but there were a lot that were on the order of a year because of
# a bug manifesting itself in the earlier data) and unreasonably high speeds;
# anything above 7.5m/s (17mph) right now.
street.data <- subset(street.data, duration < 180)
street.data <- subset(street.data, speed < 7.5)

#Also removing entries that have where there are multiple entries that have the
# same user id and the same street id, as I have seen a few entries like that
# and there is clearly something amiss with them. It may be fixed when grouping
# by IP address.
dup.cols <- c("user.id", "street.edge.id")
dups.from.top <- duplicated(street.data[,dup.cols])
dups.from.bottom <- duplicated(street.data[,dup.cols], fromLast=TRUE)
street.data <- street.data[!(dups.from.top | dups.from.bottom),]

# this is the number we care about, average minutes per km, can be used to
# compute how much to pay for missions of a given distance (given a wage)
sum(street.data$dist) / (60*sum(street.data$duration)) # 0.8 m/s
sum(street.data$duration) / (sum(street.data$dist)/1000) # 20.7 min/km
#median(street.data$min.per.km)
#median(street.data$speed)

# these are a few plots to look at the data, uncomment what you care about
#library(ggplot2)
#options(scipen = 5)
#dist.plot <- ggplot(data = street.data, aes(dist)) +
#  geom_histogram() + theme_bw() #+ xlim(0,400)
#dist.plot

#time.plot <- ggplot(data = street.data, aes(duration)) +
#  geom_histogram() + theme_bw() #+ xlim(0,1000)
#time.plot

#speed.plot <- ggplot(data = street.data, aes(speed)) +
#  geom_histogram() + theme_bw()
#speed.plot

#mpk.plot <- ggplot(data = street.data, aes(min.per.km)) +
#  geom_histogram() + theme_bw() + xlim(0,20)
#mpk.plot