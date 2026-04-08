library(readxl)
library(writexl)
library(dplyr)
library(ggplot2)
library(patchwork)
library(scales)



df <- read.csv("birdnet_master.csv")



data <- df %>%
  filter(month %in% c(6,7,8), confidence > 0.1) %>%
  mutate(recording_date = as.Date(recording_date),
         conf_pct = confidence * 100,
         week = format(recording_date, "%U")) %>%


#  PREP DATA

data <- df %>%
  filter(month %in% c(6,7,8), confidence > 0.1) %>%
  mutate(
    recording_date = as.Date(recording_date),
    conf_pct = confidence * 100,
    week = format(recording_date, "%U")
  )





# DEFINE ORDER  ( Hight to low)


sorted <- data %>%
  group_by(common_name) %>%
  mutate(count = n()) %>%
  ungroup() %>%
  arrange(desc(count))


species_order <- sorted %>%
  distinct(common_name, count) %>%
  arrange(desc(count)) %>%
  pull(common_name)



# SELECT TOP SPECIES


top_species <- sorted %>%
  group_by(common_name) %>%
  summarise(total_activity = sum(conf_pct, na.rm = TRUE)) %>%
  arrange(desc(total_activity)) %>%
  slice_head(n = 25) %>%   #
  pull(common_name)

data_top <- data %>%
  filter(common_name %in% top_species)



# TIME HEATMAP (WHEN)

heatmap_time <- data_top %>% #group_by(common_name, recorded_date) %>% slice(1) %>%
  group_by(common_name, week) %>%
  summarise(avg_conf = log(sum(conf_pct, na.rm = TRUE)), .groups = "drop") %>%
  mutate(common_name = factor(common_name, levels = species_order))
heatmap_time$common_name <- factor(heatmap_time$common_name, levels = species_order)

p_time <- ggplot(heatmap_time,
                 aes(x = week, y = common_name, fill = avg_conf)) +
  geom_tile() +
  scale_fill_gradient(low = "#edf8fb", high = "#08306b", name = "Activity Score") +
  scale_y_discrete(limits = rev) +   #
  labs(
    title = "Seasonal Patterns (When)",
    x = "Week of Summer",
    y = "Species"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
    axis.text.y = element_text(size = 7),
    plot.title = element_text(size = 10, face = "bold")
  )


# LOCATION HEATMAP (WHERE)

heatmap_loc <- data_top %>%
  group_by(common_name, location) %>%
  summarise(avg_conf = log(sum(conf_pct, na.rm = TRUE)), .groups = "drop") %>%
  mutate(common_name = factor(common_name, levels = species_order))
heatmap_loc$common_name <- factor(heatmap_loc$common_name, levels = species_order)

p_location <- ggplot(heatmap_loc,
                     aes(x = location, y = common_name, fill = avg_conf)) +
  geom_tile() +
  scale_fill_gradient(low = "#edf8fb", high = "#08306b", name = "Activity Score") +
  scale_y_discrete(limits = rev) +   #
  labs(
    title = "Spatial Patterns (Where)",
    x = "Location",
    y = "Species"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
    axis.text.y = element_text(size = 7),
    plot.title = element_text(size = 10, face = "bold")
  )


#COMBINE FINAL FIGURE

final_plot <- p_time / p_location +
  plot_annotation(
    title = "Where and When Are Birds Most Active? (Summer 2015–2020)",
    subtitle = "Bird activity based on confidence scores from audio detections (June–August)",
    theme = theme(
      plot.title = element_text(size = 16, face = "bold"),
      plot.subtitle = element_text(size = 10)
    )
  )

final_plot
