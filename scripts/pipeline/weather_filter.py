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
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS_DIR = os.path.join(SCRIPT_DIR, "inputs")
SKIPPED_DIR = os.path.join(SCRIPT_DIR, "skipped")
STATION_MAP_PATH = os.path.join(SCRIPT_DIR, "data", "station_mapping.json")
DEVICE_MAP_PATH = os.path.join(SCRIPT_DIR, "data", "device_to_site.json")

AUDIO_EXTENSIONS = {'.wav', '.flac'}

# Thresholds — override these in config.py
MAX_WIND_MPH = getattr(config, 'MAX_WIND_MPH', 20)
MAX_PRECIP_INCHES = getattr(config, 'MAX_PRECIP_INCHES', 0.5)

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
        except (ValueError, TypeError):
            print(f"    Could not parse weather row: {row}")
            return None

    print(f"    No weather data returned for {station} on {date.date()}")
    return None


def check_weather(filename, station_mapping, device_mapping):
    """Check weather for a single audio file.
    
    Returns True if the file should be KEPT (acceptable weather).
    Returns False if it should be SKIPPED (bad weather).
    """
    data_helper = ARUDataHelper()
    data_helper.input_formatted_filename(filename)

    site, mapping = resolve_site(data_helper.location, station_mapping, device_mapping)
    if mapping is None:
        print(f"    ⚠ No station mapping for '{data_helper.location}' — keeping by default")
        print(f"      (If this is a STRIPS recorder, run copy_inputs.py first to rename files)")
        return True

    station = mapping["station"]
    network = mapping["network"]
    date = data_helper.to_datetime()

    print(f"    Site: {data_helper.location} → {site} → Station: {station} ({mapping['county']} Co.) | Date: {date.date()}")

    weather = fetch_weather(station, network, date)
    if weather is None:
        print(f"    Could not retrieve weather — keeping by default")
        return True

    wind = weather["max_wind_mph"]
    precip = weather["precip_inches"]
    print(f"    Wind: {wind} mph | Precip: {precip} in")

    if wind > MAX_WIND_MPH:
        print(f"    ✗ SKIP — wind {wind} mph exceeds {MAX_WIND_MPH} mph threshold")
        return False

    if precip > MAX_PRECIP_INCHES:
        print(f"    ✗ SKIP — precip {precip} in exceeds {MAX_PRECIP_INCHES} in threshold")
        return False

    print(f"    ✓ KEEP")
    return True


def main():
    os.makedirs(SKIPPED_DIR, exist_ok=True)
    station_mapping = load_station_mapping()
    device_mapping = load_device_mapping()

    # Collect audio files first (avoid modifying dir while iterating)
    audio_files = [
        f for f in os.listdir(INPUTS_DIR)
        if os.path.isfile(os.path.join(INPUTS_DIR, f))
        and os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS
    ]

    if not audio_files:
        print("No audio files found in inputs/")
        return

    print(f"Found {len(audio_files)} audio file(s) to check")
    print(f"Thresholds — Max wind: {MAX_WIND_MPH} mph | Max precip: {MAX_PRECIP_INCHES} in\n")

    kept = 0
    skipped = 0

    for filename in audio_files:
        print(f"[{kept + skipped + 1}/{len(audio_files)}] {filename}")

        if check_weather(filename, station_mapping, device_mapping):
            kept += 1
        else:
            src = os.path.join(INPUTS_DIR, filename)
            dst = os.path.join(SKIPPED_DIR, filename)
            shutil.copy2(src, dst)
            os.remove(src)
            skipped += 1

        # Be polite to the IEM API
        time.sleep(0.5)

    print(f"\nDone — Kept: {kept} | Skipped: {skipped}")


if __name__ == "__main__":
    main()
