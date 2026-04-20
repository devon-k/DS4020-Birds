
library(dplyr)
library(plotly)
library(patchwork)


df <- read.csv("compiled/birdnet_master_full.csv")

# -------------------------------
# PREP DATA
# -------------------------------
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

df = df |> mutate(
  loc_type = paste(location, location_type, sep="_"),
  location_type = ifelse(location_type == "CTL-0423-07102015", "CTL", location_type)
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
        )

# data = data |> group_by(week, common_name) |> 
#   mutate(confidence =  sum(confidence)) |> ungroup() |> 
#   group_by(common_name) |> 
#   mutate(confidence = confidence/ max(confidence))

# -------------------------------
# TOP SPECIES (KEEP CLEAN)
# -------------------------------
top_species <- data %>%
  count(common_name, sort = TRUE) %>%
  slice_head(n = 20) %>%
  pull(common_name)

data <- data %>%
  filter(common_name %in% top_species)

# -------------------------------
# WHERE (TREATMENT)
# -------------------------------
where_data <- data %>%
  group_by(common_name, trt) %>%
  summarise(avg_conf = sum(confidence)/length(levels(factor(formatted_filename))), .groups = "drop") |> group_by(common_name) |> 
  mutate(standardized_conf = ((avg_conf - mean(avg_conf))/sd(avg_conf)) )

p_where <- plot_ly(
  where_data,
  x = ~trt,
  y = ~common_name,
  z = ~standardized_conf,
  type = "heatmap",
  colorscale = "Blues"
) %>%
  layout(
    title = "WHERE: Activity by Treatment",
    xaxis = list(title = "Treatment"),
    yaxis = list(title = "Species")
  )

# -------------------------------
# WHEN (TIME)
# -------------------------------
when_data <- data %>%
  group_by(common_name, week) %>%
  summarise(avg_conf = sum(confidence)/length(levels(factor(formatted_filename))), .groups = "drop") |> group_by(common_name) |> 
  mutate(standardized_conf = ((avg_conf - mean(avg_conf))/sd(avg_conf)) )

p_when <- plot_ly(
  when_data,
  x = ~week,
  y = ~common_name,
  z = ~standardized_conf,
  type = "heatmap",
  colorscale = "Blues"
) %>%
  layout(
    title = "WHEN: Activity Over Weeks",
    xaxis = list(title = "Week"),
    yaxis = list(title = "Species")
  )

# -------------------------------
# COMBINE (SIDE BY SIDE)
# -------------------------------
subplot(
  p_where, p_when,
  nrows = 1,
  shareY = TRUE,
  titleX = TRUE,
  titleY = TRUE
)

