import pandas as pd

labelled = pd.read_csv("data\\labelled_bird_audio.dat")
birdnet_results = pd.read_csv("compiled/birdnet_master.csv")

birdnet_results2 = pd.DataFrame(birdnet_results)

confidence = float( input("Input minimum confidence value: ") )
birdnet_results2 = birdnet_results2.loc[birdnet_results2['confidence'] > confidence,]

# filtered_labels = birdnet_results2 |> group_by(recording_date) |> slice(1) |> ungroup() |> select(location, location_type, recording_date) |> 
#   inner_join(labelled, by = c("location" = "site_abbreviation", "location_type" = "Type", "recording_date" = "Record_date")) |> 
#   group_by(location, location_type, recording_date, common_name) |> slice(1) |> ungroup()

filtered_labels = birdnet_results2.groupby(
    ["location", "location_type", "recording_date"]).head(1)[["location", "location_type", "recording_date"]].merge(
        labelled, how="inner", 
        left_on=["location", "location_type", "recording_date"], 
        right_on=["site_abbreviation", "Type", "Record_date"] ).groupby(
    ["location", "location_type", "recording_date", "common_name"]).head(1)

all_birdnet = birdnet_results2.groupby(
    ["location", "location_type", "recording_date", "common_name"]).head(1).merge(
        filtered_labels, how="left", 
        on=["location", "location_type", "recording_date", "common_name"])

all_human = birdnet_results2.groupby(
    ["location", "location_type", "recording_date", "common_name"]).head(1).merge(
        filtered_labels, how="right", 
        on=["location", "location_type", "recording_date", "common_name"])

print("-"*40)
print(f"{"Validation Statistics" :^40}")
print("-"*40)
print(f"For minimum confidence = {confidence}")
print()
print( "False positives: ", round(sum(all_birdnet['genus'].isna())/len(all_birdnet),3) )
print( "False negatives: ", round(sum(all_human['label'].isna())/len(all_human),3) )

