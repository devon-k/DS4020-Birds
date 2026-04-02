library(dplyr)
library(tidyr)
library(ggplot2)

labelled = read.csv("labelled_bird_audio.dat")
birdnet_results = read.csv("compiled/birdnet_master.csv")

birdnet_results2 = birdnet_results |> mutate(start_time = round(start_time/60) ) |> filter(confidence > 0.10)

# colnames(labelled)
# colnames(birdnet_results2)

# Inner join to cut labelled data down to only those present in results data
filtered_labels = birdnet_results2 |> group_by(location, location_type, recording_date) |> slice(1) |> ungroup() |> select(location, location_type, recording_date) |> 
  inner_join(labelled, by = c("location" = "site_abbreviation", "location_type" = "Type", "recording_date" = "Record_date")) |> 
  group_by(location, location_type, recording_date, common_name) |> slice(1) |> ungroup()

# Left join to retain all results data, for type I error
joined = birdnet_results2 |> group_by(location, location_type, recording_date, common_name) |> slice(1) |> ungroup() |> 
  left_join(filtered_labels, by = c("location", "location_type", "recording_date", "common_name"))

# Right join to retain all labelled data, for type II error
joined2 = birdnet_results2 |> group_by(location, location_type, recording_date, common_name) |> slice(1) |> ungroup() |> 
  right_join(filtered_labels, by = c("location", "location_type", "recording_date", "common_name"))

paste("False positive rate: ", round(nrow(joined |> filter(is.na(genus))) / nrow(joined), 3 ) )
paste("False negative rate: ", round(nrow(joined2 |> filter(is.na(label))) / nrow(joined2), 3 ) )

joined |> filter(is.na(genus)) |> select(common_name) |> table()
joined2 |> filter(is.na(label)) |> select(common_name) |> table()

