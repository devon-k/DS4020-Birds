import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
import numpy as np

SCRIPT_DIR = Path(__file__).absolute()

class MissingRequiredElementsError(Exception):
    """Raised when a file is syntactically valid but missing required elements"""
    pass

labelled = pd.read_csv( SCRIPT_DIR.parent.parent / "data" / "labelled_bird_audio.dat")
birdnet_results = pd.read_csv(SCRIPT_DIR.parent.parent / "compiled" / "birdnet_master.csv")

# Remove labelled files which are not represented in results.
filtered_labels = labelled.merge(
        birdnet_results, how="inner", 
        left_on=["Site", "Type", "Record_date", 'common_name'], 
        right_on=["location", "location_type", "recording_date", 'common_name'] )

# Check to make sure there are in fact labelled files represented in results. 
if len(filtered_labels) < 1:
    raise MissingRequiredElementsError("birdnet_master.csv does not contain data from any audio which has valid human-determined labels")

# Get aggrigated confidence metrics
aggrigate_confidence = birdnet_results.pivot_table(    values='confidence',
                                            index = ["location", "location_type", "recording_date", "common_name"],
                                            aggfunc= ['sum', 'mean', 'max', 'min'],
                                            fill_value= 0
                                        )

aggrigate_confidence_flat = pd.DataFrame(aggrigate_confidence)
aggrigate_confidence_flat.columns = ['_'.join(col).strip() for col in aggrigate_confidence.columns.to_flat_index()] # flatten multilayer columns


## ---- Create response values using detections table logic ----

training = filtered_labels

# Presence indicator
training["detected"] = 1

# Collapse repeated detections within the same recording
grouped = (
    training.groupby(["location", "location_type", "recording_date", "common_name"], as_index=False)["detected"]
    .max()
)

species_list = pd.unique(grouped["common_name"]).tolist()

# Pivot to wide occupancy table
detections_table = grouped.pivot_table(
    index=["location", "location_type", "recording_date"],
    columns="common_name",
    values="detected",
    fill_value=0
).reset_index()

ungrouped = detections_table.melt(id_vars = ["location", "location_type", "recording_date"], value_vars = species_list)

# Create complete dataframe
combined_df = ungrouped.merge(
    aggrigate_confidence_flat.reset_index(), how="left", 
)

## ---- Train classifier ----

#encoder = OneHotEncoder() -- As long as we use the same list of bird species for the detections table we 
#                               shouldn't have to worry about doing proper one-hot encoding
clf = RandomForestClassifier()

train_y = combined_df["value"]
#train_x = encoder.fit_transform(pd.DataFrame(combined_df["common_name"]))
#train_x = np.concatenate([np.array(combined_df), train_x])

# Create dummy variables, strip out columns we don't need (location, treatment, and date)
train_x = pd.get_dummies(combined_df.fillna(0).loc[:,["common_name", "sum_confidence", "mean_confidence", "max_confidence"]])

clf.fit(train_x, train_y)