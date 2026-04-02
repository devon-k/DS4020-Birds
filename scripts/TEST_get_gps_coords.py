from utilities.get_location import get_location
from ARU_DataHelper import ARUDataHelper
import pandas as pd

## 
print("Results should both be lat: 41.3185507636026, lon: -95.17488863552295\n")

print("Base get location function:")
print(get_location("ARM"), "\n")

helper = ARUDataHelper()

helper.input_formatted_filename("ARM_CRP_20160306_072600.flac")

print("Via ARUDataHelper")
print(helper.get_lat(), helper.get_lon())

location_data = pd.read_csv("inputs/STRIPS_site_abbreviation_and_centroid.csv")

locations = location_data["site"].tolist()

print("\n All of the sites:")

for i in locations:
    print(f"{i}: {get_location(i)}")

