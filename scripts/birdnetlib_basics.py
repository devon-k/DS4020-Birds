from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from ARU_DataHelper import ARUDataHelper
import csv
import time
import os
import config
import multiprocessing

# Paths relative to this script file
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS_DIR = os.path.join(SCRIPT_DIR, "inputs")
OUTPUTS_DIR = os.path.join(SCRIPT_DIR, "outputs")

# Audio file extensions to process
AUDIO_EXTENSIONS = {'.wav', '.flac'}

def AnalyzeRecording(filename):
            file_path = os.path.join(INPUTS_DIR, filename)
            analyzer = Analyzer()
            analyzer_start = time.perf_counter()
            print(f"\nProcessing: {filename}")

            dataHelper = ARUDataHelper()
            dataHelper.input_formatted_filename(filename)

            #TODO - get longitude and latitude from file

            recording = Recording(
                analyzer,
                file_path,
                min_conf=config.MIN_CONFIDENCE,
                lat=42.0347,
                lon=-93.6199,
                date= dataHelper.to_datetime(),
                overlap=config.OVERLAP
            )

            recording.analyze()
            end1 = time.perf_counter()
            print(f"Analysis complete: {end1-analyzer_start}")

            return recording

def deleteAudioFile(filename):
    file_path = os.path.join(INPUTS_DIR, filename)
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")
        import traceback
        traceback.print_exc()

def write_detections_to_csv(recording, filename):
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

def process_file(filename):
    try:
        recording = AnalyzeRecording(filename)
        #deleteAudioFile(filename)
        write_detections_to_csv(recording, filename)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        import traceback
        traceback.print_exc()

def runBirdNet():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    start = time.perf_counter()

    try:
        # Get list of audio files
        files = [f for f in os.listdir(INPUTS_DIR) if os.path.isfile(os.path.join(INPUTS_DIR, f)) and os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS]
        
        if not files:
            print("No audio files found in inputs directory.")
            return

        # Use multiprocessing to process files in parallel
        num_processes = min(multiprocessing.cpu_count(), len(files), config.MAX_PROCESSES if config.MAX_PROCESSES else 0)  # Use available CPUs, number of files, or Max Processes config setting
        print(f"Processing {len(files)} files using {num_processes} processes.")
        
        with multiprocessing.Pool(processes=num_processes) as pool:
            pool.map(process_file, files)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        end = time.perf_counter()
        print(f"Program complete: {end-start}")

if __name__ == "__main__":
    runBirdNet()
