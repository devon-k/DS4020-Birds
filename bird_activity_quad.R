
library(dplyr)
library(plotly)
library(patchwork)
library(ggplot2)


df <- read.csv("compiled/birdnet_master_full.csv")

colnames(df)

# -------------------------------
# PREP DATA
# -------------------------------
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

data = data |> mutate(
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
                      "WET" = "CRP" )

data = data |>
  group_by(location, location_type, recording_date)|> mutate(detections = n()) |> ungroup() |> 
  mutate(# location = factor(location),
          trt = type_conversion[location_type],
          location_type = factor(location_type),
          # month = factor(month),
          # year = factor(year),
          # date = factor(date)
        )

# -------------------------------
# TOP SPECIES (KEEP CLEAN)
# -------------------------------
top_species <- data %>%
  count(common_name, sort = TRUE) %>%
  slice_head(n = 30) %>%
  pull(common_name)

top_data <- data %>%
  filter(common_name %in% top_species)

# -------------------------------
# WHEN (TIME)
# -------------------------------
when_data <- top_data %>%
  group_by(common_name, week, trt) %>%
  summarise(avg_conf = sum(confidence)/length(levels(factor(formatted_filename))), .groups = "drop") |> group_by(common_name) |> 
  mutate(standardized_conf =  (avg_conf - min(avg_conf)) / (max(avg_conf) - min(avg_conf)) 
         )

isu_theme =   theme(
  panel.background = element_rect(fill = "#D0D3D4", color = NA),
  plot.background  = element_rect(fill = "grey20", color = NA),
  axis.text.x      = element_text(angle = 90, hjust = 0.3, color = "white"), 
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

p = when_data %>% group_by(trt) %>% 
  group_map( ~ggplot(., aes(
                      x = week,
                      y = common_name,
                      group_by = common_name,
                      fill = standardized_conf) ) + 
               geom_tile() + 
               scale_fill_gradient(
                 low = "#7C2529",
                 high = "white"
               ) + isu_theme +
               scale_x_date(
                 date_labels = "%b",
                 date_breaks = "1 month",
                 # n.breaks = 12
               )
)

# -------------------------------
# Output
# -------------------------------

# Parameters for outputs
out_height = 1080
out_width = 1080
out_scale = 1.5

p[[1]] + labs(
    title = paste("Seasonal Avian Activity - CRP"),
    fill = "Activity",
    x = "Month",
    y = "Species"
  )
ggsave("Activity - CRP.png", width = out_width, height = out_height, units = "px", scale = out_scale)

p[[2]] + labs(
    title = paste("Seasonal Avian Activity - CTL"),
    fill = "Activity",
    x = "Month",
    y = "Species"
  )
ggsave("Activity - CTL.png", width = out_width, height = out_height, units = "px", scale = out_scale)

p[[3]] + labs(
    title = paste("Seasonal Avian Activity - EXP"),
    fill = "Activity",
    x = "Month",
    y = "Species"
  )
ggsave("Activity - EXP.png", width = out_width, height = out_height, units = "px", scale = out_scale)

p[[4]] + labs(
    title = paste("Seasonal Avian Activity - TER"),
    fill = "Activity",
    x = "Month",
    y = "Species"
  )
ggsave("Activity - TER.png", width = out_width, height = out_height, units = "px", scale = out_scale)
