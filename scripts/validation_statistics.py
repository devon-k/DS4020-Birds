import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).absolute()

class MissingRequiredElementsError(Exception):
    """Raised when a file is syntactically valid but missing required elements"""
    pass

labelled = pd.read_csv( SCRIPT_DIR.parent.parent / "data" / "labelled_bird_audio.dat")
birdnet_results = pd.read_csv(SCRIPT_DIR.parent.parent / "compiled" / "birdnet_master.csv")

birdnet_results2 = pd.DataFrame(birdnet_results)

# This is a diagnostic tool so we'll just ask the user for a desired confidence score for now
confidence = float( input("Input minimum confidence value: ") )

if confidence > .99 or confidence < .01:
    raise ValueError ("Confidence level must be between .01 and .99")


# Get results above the given confidence
birdnet_results2 = birdnet_results2.loc[birdnet_results2['confidence'] > confidence,]

# Remove labelled files which are not represented in results.
filtered_labels = birdnet_results2.groupby(
    ["location", "location_type", "recording_date"]).head(1)[["location", "location_type", "recording_date"]].merge(
        labelled, how="inner", 
        left_on=["location", "location_type", "recording_date"], 
        right_on=["site_abbreviation", "Type", "Record_date"] ).groupby(
    ["location", "location_type", "recording_date", "common_name"]).head(1)

# Check to make sure there are in fact labelled files represented in results. 
if len(filtered_labels) < 1:
    raise MissingRequiredElementsError("birdnet_master.csv does not contain data from any audio which has valid human-determined labels")

# Results are filtered down to the list of species detected in each file
# inner join removes any files in results which don't have a labelled counterpart,
# left-join to keep all remaining results observations - used for determining species in results not in labels. 
all_birdnet = birdnet_results2.groupby(
    ["location", "location_type", "recording_date", "common_name"]).head(1).merge(
        filtered_labels[["location", "location_type", "recording_date"]], how="inner", 
        on=["location", "location_type", "recording_date"]).merge(
        filtered_labels, how="left", 
        on=["location", "location_type", "recording_date", "common_name"])

# Right-join to keep all labelled observations - used for determining species in labels not in results.
all_human = birdnet_results2.groupby(
    ["location", "location_type", "recording_date", "common_name"]).head(1).merge(
        filtered_labels, how="right", 
        on=["location", "location_type", "recording_date", "common_name"])

print("-"*40)
print(f"{'Validation Statistics' :^40}")
print("-"*40)
print(f"For minimum confidence = {confidence}")
print()
print( "False positives: ", round(sum(all_birdnet['genus'].isna())/len(all_birdnet),3) )
print( "False negatives: ", round(sum(all_human['label'].isna())/len(all_human),3) )