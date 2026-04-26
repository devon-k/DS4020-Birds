library(dplyr)
library(tidyr)
library(ggplot2)

labelled = read.csv("C:/Users/devon/OneDrive/Documents/DS4010/DS4020-Birds/data/labelled_bird_audio.dat")
birdnet_results = read.csv("C:/Users/devon/OneDrive/Documents/DS4010/DS4020-Birds/compiled/birdnet_master.csv")

max_cperfile = birdnet_results %>% group_by(location, location_type, recording_date, common_name) %>% summarize(max_conf = max(confidence), num_det = n(), sum_conf = sum(confidence))
use_labelled = labelled %>% select(Site, Type, Record_date, common_name) %>% group_by(Site, Type, Record_date, common_name) %>% slice(1) %>% mutate(present = 1)


labelled_files = labelled %>% select(Site, Type, Record_date) %>% unique() %>% mutate(sampled = 1)

#detections in labelled files
test = max_cperfile %>% left_join(labelled_files, c("location" = "Site", "location_type" = "Type", "recording_date" = "Record_date")) %>% filter(sampled == 1) %>% select(-sampled)

callibration_set = test %>% full_join(use_labelled, by = c("location" = "Site", "location_type" = "Type", "recording_date" = "Record_date", "common_name" = "common_name")) %>% replace_na(list(present = 0,max_conf = 0,num_det = 0,sum_conf = 0)) %>% ungroup()

dim(callibration_set)

model = glm(present ~ max_conf + num_det + sum_conf, data = callibration_set, family = "binomial")

threshold = 0.5

confusion = callibration_set %>% select(-location, -location_type, -recording_date) %>% group_by(common_name) %>% 
  summarize(fneg = sum(max_conf < threshold & present == 1), 
            fpos = sum(max_conf >= threshold & present == 0), 
            tpos = sum(max_conf >= threshold & present == 1)) %>% 
  mutate(tneg = nrow(labelled_files)-fneg-fpos-tpos)

confusion %>% select(-common_name) %>% colSums()

grid = seq(0, 0.99, 0.01)

thresholds <- data.frame()


for(bird in unique(confusion$common_name)) {
  results <- data.frame()
  
  for(i in grid){
    
    confusion2 = callibration_set %>% filter(common_name == bird) %>% 
      select(-location, -location_type, -recording_date) %>% 
      group_by(common_name) %>% 
      summarize(
        fneg = sum(max_conf < i & present == 1), 
        fpos = sum(max_conf >= i & present == 0), 
        tpos = sum(max_conf >= i & present == 1)
      ) %>% 
      mutate(tneg = nrow(labelled_files) - fneg - fpos - tpos)
    
    totals <- confusion2 %>% 
      select(-common_name) %>% 
      colSums()
    
    results <- rbind(
      results,
      data.frame(
        threshold = i,
        fneg = totals["fneg"],
        fpos = totals["fpos"],
        tpos = totals["tpos"],
        tneg = totals["tneg"]
      )
    )
  }
  
  results <- results %>%
    mutate(
      accuracy  = (tpos + tneg) / (tpos + tneg + fpos + fneg),
      precision = tpos / (tpos + fpos),
      recall    = tpos / (tpos + fneg),
      f1 = 2 * (precision * recall) / (precision + recall)
    )
  
  if(any(!is.na(results$f1))){
    i = which.max(na.omit(results$f1))
    thresholds <- rbind(
      thresholds,
      data.frame(
        bird = bird,
        threshold = results$threshold[i],
        fpos = results$fpos[i],
        fneg = results$fneg[i],
        tpos = results$tpos[i],
        tneg = results$tneg[i],
        f1 = results$f1[i]
      )
    )
  }
}

thresholds

plot(results$fpos, results$tpos, main = paste(bird, "ROC Curve"), type = "l")

