from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from ARU_DataHelper import ARUDataHelper
import csv
import time
import datetime
import os

# Paths relative to this script file
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS_DIR = os.path.join(SCRIPT_DIR, "inputs")
OUTPUTS_DIR = os.path.join(SCRIPT_DIR, "outputs")

# Audio file extensions to process
AUDIO_EXTENSIONS = {'.wav', '.flac'}

os.makedirs(OUTPUTS_DIR, exist_ok=True)

start = time.perf_counter()

try:
    analyzer = Analyzer()

    # Loop through all files in the inputs directory
    for filename in os.listdir(INPUTS_DIR):
        file_path = os.path.join(INPUTS_DIR, filename)
        
        # Skip directories, only process audio files
        if not os.path.isfile(file_path):
            continue
        
        if os.path.splitext(filename)[1].lower() not in AUDIO_EXTENSIONS:
            continue
        
        analyzer_start = time.perf_counter()
        print(f"\nProcessing: {filename}")

        dataHelper = ARUDataHelper()
        dataHelper.input_formatted_filename(filename)

        #TODO - get longitude and latitude from file

        recording = Recording(
            analyzer,
            file_path,
            min_conf=0.10,
            lat=42.0347,
            lon=-93.6199,
            date= dataHelper.to_datetime(),
        )

        recording.analyze()
        end1 = time.perf_counter()
        print(f"Analysis complete: {end1-analyzer_start}")

        # Delete the audio file after processing
        os.remove(file_path)
        print(f"Deleted: {filename}")

        # Generate output path based on input filename
        out_path = os.path.join(OUTPUTS_DIR, os.path.splitext(filename)[0] + ".csv")
        
        with open(out_path, "w", newline="") as csvfile:
            if recording.detections:
                fieldnames = recording.detections[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(recording.detections)
                print(f"Saved {len(recording.detections)} detections to {out_path}")
            else:
                print("No detections found.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    end = time.perf_counter()
    print(f"Program complete: {end-start}")
