
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
    !is.na(recording_datetime)
  ) %>%
  mutate(
    recording_date = as.Date(recording_datetime),
    week = as.numeric(format(recording_date, "%U")),
    week = as.Date("2024-01-01") + (week - 1) * 7
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
                      "WET" = "CRP" )

data = data |>
  group_by(location, location_type, recording_date)|> mutate(detections = n()) |> ungroup() |> 
  mutate(# location = factor(location),
          trt = type_conversion[location_type],
          location_type = factor(location_type),
          # month = factor(month),
          # year = factor(year),
          # date = factor(date)
        ) |> group_by(location, location_type, week, common_name) |> slice(1)

# data = data |> group_by(week, common_name) |> 
#   mutate(confidence =  sum(confidence)) |> ungroup() |> 
#   group_by(common_name) |> 
#   mutate(confidence = confidence/ max(confidence))

isu_theme =   theme(
  panel.background = element_rect(fill = "#D0D3D4", color = NA),
  plot.background  = element_rect(fill = "grey20", color = NA),
  axis.text.x      = element_text( color = "white"), #angle = 90, hjust = 0.3,
  axis.text.y      = element_text(color = "white"),
  axis.title.x     = element_text(color = "#CAC7A7"),
  axis.title.y     = element_text(color = "#CAC7A7"),
  plot.title       = element_text(color = "white", size = 16, face = "bold"),
  
  legend.position = "none",
  legend.background = element_rect(fill = "#D0D3D4"),
  legend.key = element_rect(fill = "white"),
  legend.text = element_text(color = "grey20", size = 6, face = "italic"),
  legend.title = element_text(color = "grey20", size = 8, face = "bold")
)

data |> group_by(trt, common_name) |> summarize(unique_detections = length(unique(common_name)) ) |> 
  ggplot(aes(x = trt, y = unique_detections) ) + 
  geom_col(fill = "#7C2529") + isu_theme + 
  labs(title = "Species per Treatment", y = "Unique Species Detected", x = "Month")
ggsave("Species by treatment.png", width = 940, height = 720, units = "px", scale = 1.5)

data |> group_by(location, common_name) |> summarize(unique_detections = length(unique(common_name)) ) |> 
  ggplot(aes(x = location, y = unique_detections) ) + 
  geom_col(fill = "#7C2529") + isu_theme + 
  labs(title = "Species by Location", y = "Unique Species Detected", x = "Month") + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
ggsave("Species by Location.png", width = 940, height = 720, units = "px", scale = 1.5)

data |> group_by(week, common_name) |> summarize(unique_detections = length(unique(common_name)) ) |>
  ggplot(aes(x = week, y = unique_detections) ) + 
  geom_col(fill = "#7C2529") + isu_theme + 
  labs(title = "Species by Week", y = "Unique Species Detected", x = "Month") +
  scale_x_date(
    date_labels = "%b",
    date_breaks = "1 month",
  )
ggsave("Species by Week.png", width = 940, height = 720, units = "px", scale = 1.5)

data |> group_by(week, trt, common_name) |> summarize(unique_detections = length(unique(common_name)) ) |>
  ggplot(aes(x = week, y = unique_detections) ) + 
  geom_col(fill = "#7C2529") + facet_wrap(~trt) + isu_theme +
  labs(title = "Species by Week by Treatment", y = "Unique Species Detected", x = "Month") +
  scale_x_date(
    date_labels = "%b",
    date_breaks = "1 month",
  ) + theme(axis.text.x = element_text(angle = 90, hjust = 0.3, color = "white"))
ggsave("Species by treatment by week.png", width = 940, height = 720, units = "px", scale = 1.5)

