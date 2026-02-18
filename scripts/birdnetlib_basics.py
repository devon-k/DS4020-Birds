from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import csv
import time
import datetime
import os

# Paths relative to this script file
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS_DIR = os.path.join(SCRIPT_DIR, "inputs")
OUTPUTS_DIR = os.path.join(SCRIPT_DIR, "outputs")

# Default filename inside the inputs folder
DEFAULT_AUDIO = "DMWW-EXP_0+1_20200411_062600.wav"

# Full paths used by the script (edit these variables if desired)
file_path = os.path.join(INPUTS_DIR, DEFAULT_AUDIO)
out_path = os.path.join(OUTPUTS_DIR, os.path.splitext(DEFAULT_AUDIO)[0] + ".csv")

os.makedirs(OUTPUTS_DIR, exist_ok=True)

start = time.perf_counter()

try:
    analyzer = Analyzer()

    analyzer_start = time.perf_counter()

    #TODO - get longitude and latitude from file
    #TODO - get date from file
    recording = Recording(
        analyzer,
        file_path,
        min_conf=0.10,
        lat=42.0347,
        lon=-93.6199,
        date=datetime.datetime(year=2015, month=5, day=20),
    )

    recording.analyze()
    end1 = time.perf_counter()
    print(f"Analysis complete: {end1-analyzer_start}")

    with open(out_path, "w", newline="") as csvfile:
        if recording.detections:
            fieldnames = recording.detections[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(recording.detections)
            print(f"Saved {len(recording.detections)} detections to {out_path}")
        else:
            print("No detections found.")

finally:
    end = time.perf_counter()
    print(f"Program complete: {end-start}")
