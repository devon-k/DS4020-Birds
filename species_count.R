
library(dplyr)
library(plotly)
library(patchwork)
library(ggplot2)


df <- read.csv("compiled/birdnet_master_full.csv")

# -------------------------------
# PREP DATA
# -------------------------------

df = df |> mutate(
  loc_type = paste(location, location_type, sep="_"),
  location_type = ifelse(location_type == "CTL-0423-07102015", "CTL", location_type)
)

data <- df |> #[sample(nrow(df), 100000),] %>%
  filter(
    confidence >= 0.5,
    !is.na(common_name),
    !is.na(location_type),
    !is.na(recording_date)
  ) %>%
  mutate(
    recording_date = as.Date(recording_date),
    week = as.numeric(format(recording_date, "%U"))
  )

type_conversion <- c("CRP" = "CRP",
                      "CRP1" = "CRP",
                      "CRP2" = "CRP",
                      "CTL" = "CTL",
                      "CTLN" = "CTL",
                      "CTLS" = "CTL",
                      "EXP" = "EXP",
                      "EXP1" = "EXP",
                      "EXP2" = "EXP",
                      "EXPN" = "EXP",
                      "EXPS" = "EXP",
                      "TER" = "TER",
                      "WET" = "WET" )

data = data |>
  group_by(location, location_type, recording_date)|> mutate(detections = n()) |> ungroup() |> 
  mutate(# location = factor(location),
          trt = type_conversion[location_type],
          location_type = factor(location_type),
          # month = factor(month),
          # year = factor(year),
          # date = factor(date)
        ) |> group_by(location, location_type, recording_date, common_name) |> slice(1)

# data = data |> group_by(week, common_name) |> 
#   mutate(confidence =  sum(confidence)) |> ungroup() |> 
#   group_by(common_name) |> 
#   mutate(confidence = confidence/ max(confidence))

data |> group_by(trt, common_name) |> summarize(unique_detections = length(unique(common_name)) ) |> 
  ggplot(aes(x = trt, y = unique_detections) ) + 
  geom_col()

data |> group_by(week, common_name) |> summarize(unique_detections = length(unique(common_name)) ) |>
  ggplot(aes(x = week, y = unique_detections) ) + 
  geom_col()

data |> group_by(week, trt, common_name) |> summarize(unique_detections = length(unique(common_name)) ) |>
  ggplot(aes(x = week, y = unique_detections) ) + 
  geom_col() + facet_wrap(~trt)

