"""
Weather-based audio file filter.

For each audio file in inputs/, checks the Iowa Environmental Mesonet (IEM)
for weather conditions on the recording date at the nearest station.
Files recorded during high wind or heavy rain are moved to skipped/.

Usage:
    python weather_filter.py

Thresholds are configured in config.py (MAX_WIND_MPH, MAX_PRECIP_INCHES).
Station mappings are in data/station_mapping.json.
"""
from pathlib import Path
import pandas as pd
import os
import json
import shutil
import urllib.request
import csv
import io
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ARU_DataHelper import ARUDataHelper
import config

# Paths relative to the project root (one level up from scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent.parent
INPUTS_DIR = SCRIPT_DIR / "inputs"
DATA_DIR = SCRIPT_DIR / "data"
OUTPUT_CSV = DATA_DIR / "weather_data.csv"

STATION_MAP_PATH = os.path.join(SCRIPT_DIR, "data", "station_mapping.json")
DEVICE_MAP_PATH = os.path.join(SCRIPT_DIR, "data", "device_to_site.json")

AUDIO_EXTENSIONS = {'.wav', '.flac'}

# IEM wind data is reported in knots
KNOTS_TO_MPH = 1.15078


def load_station_mapping():
    """Load the site abbreviation -> IEM station mapping from JSON."""
    with open(STATION_MAP_PATH, "r") as f:
        return json.load(f)


def load_device_mapping():
    """Load the device/recorder prefix -> site abbreviation mapping from JSON."""
    with open(DEVICE_MAP_PATH, "r") as f:
        raw = json.load(f)
    # Filter out comments and ambiguous entries (lists)
    return {k: v for k, v in raw.items() if isinstance(v, str) and not k.startswith("_")}


def resolve_site(location, station_mapping, device_mapping):
    """Match an ARU location string to a station mapping entry.
    
    Resolution order:
      1. Exact match in station_mapping (e.g. "KAL")
      2. Exact match in device_mapping (e.g. "KALD-CTL" → "KAL" → station)
      3. First 3 chars in station_mapping (e.g. "KALD" → "KAL")
    
    Returns (site_abbrev, mapping_dict) or (None, None).
    """
    # 1. Direct match in station mapping (standard pipeline filenames)
    if location in station_mapping:
        return location, station_mapping[location]

    # 2. Device/recorder name lookup (raw lab filenames like "STRIPS2", "KALD-CTL")
    if location in device_mapping:
        site = device_mapping[location]
        if site in station_mapping:
            return site, station_mapping[site]

    # 3. First 3 chars (covers cases like "KALD" → "KAL")
    prefix = location[:3]
    if prefix in station_mapping:
        return prefix, station_mapping[prefix]

    return None, None


def fetch_weather(station, network, date):
    """Fetch daily weather summary from the Iowa Environmental Mesonet.
    
    Returns dict with 'max_wind_mph' and 'precip_inches', or None on failure.
    IEM docs: https://mesonet.agron.iastate.edu/request/daily.phtml
    """
    url = (
        f"https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?"
        f"network={network}&stations={station}"
        f"&year1={date.year}&month1={date.month}&day1={date.day}"
        f"&year2={date.year}&month2={date.month}&day2={date.day}"
        f"&format=csv"
    )

    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            text = response.read().decode("utf-8")
    except Exception as e:
        print(f"    API request failed: {e}")
        return None

    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        try:
            # IEM returns wind in knots — convert to mph
            gust_kts = float(row.get("max_wind_gust_kts", 0) or 0)
            precip = float(row.get("precip_in", 0) or 0)
            return {
                "max_wind_mph": round(gust_kts * KNOTS_TO_MPH, 1),
                "precip_inches": precip,
            }
        except:
            return None

    return None


def main():
    station_mapping = load_station_mapping()
    device_mapping = load_device_mapping()

    # Collect audio files first (avoid modifying dir while iterating)
    audio_files = [
    f.name for f in INPUTS_DIR.iterdir()
    if f.suffix.lower() in AUDIO_EXTENSIONS
]

    if not audio_files:
        print("No audio files found in inputs/")
        return

    print(f"Processing {len(audio_files)} file ...")

    unique_requests = {}
    #Step 1: collect unique (station, date) combonations
    for filename in audio_files: 
        helper = ARUDataHelper()
        helper.input_formatted_filename(filename)

        site, mapping = resolve_site(helper.location, station_mapping, device_mapping)

        if mapping is None: 
            continue
        station  = mapping["station"]
        network = mapping["network"]
        date = helper.to_datetime()

        key = (station, date)

        unique_requests[key] = {
            "location":helper.location, 
            "station": station, 
            "network": network, 
            "date": date, 
            "year": helper.year,
            "month": helper.month, 
            "day": helper.day, 
            "formatted_filename": helper.formatted_filename
        }

    print(f"Unique station-date combos: {len(unique_requests)}")

    #Step 2: Fetch weather
    results = []

    for i, ((station, date), meta) in enumerate(unique_requests.items(), start=1): 
        print(f"[{i}/{len(unique_requests)}] {station} - {date.date()}")

        weather = fetch_weather(station, meta["network"], date)

        if weather: 
            results.append({
                **meta, 
                "max_wind_mph": weather [ "max_wind_mph"], 
                "precip_inches": weather["precip_inches"]
            })
        time.sleep(0.5)

    df = pd.DataFrame(results)

    OUTPUT_CSV.parent.mkdir(exist_ok = True)
    df.to_csv(OUTPUT_CSV, index = False)

    print(f"\nSaved weather data to: {OUTPUT_CSV}")
    print(f"Total rows: {len(df)}")

    

if __name__ == "__main__":
    main()
