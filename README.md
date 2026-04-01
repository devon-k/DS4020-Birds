# DS4020-Birds

## Pipeline Rough Draft Outline
1. Copy audio files from lss to inputs directory
2. Run audio files through bird net
    * Store outputs in output directory
    * Delete audio file from inputs
    * Clean audio file, if time allows
3. Compile output files into one large csv
    * make visualizations/dashboards from this csv
    * other analyzations of data

## Set up Intructions
1. Clone GitHub
3. Make a copy of "config.py.template" as "config.py"
5. Install Libraries
   * librosa
   * tesorflow
   * resampy
   * birdnetlib
   * pandas
6. Run copy_inputs.py, birdnetlib_basics.py, then consolidate_outputs.py


## Copy_inputs.py: 
Copies bird audio files from the lab storage system (LSS) into the local ‘inputs’ directory and renames them into a standardized format for downstream processing. It will output standardized audio files in ‘/inputs.’

Key Features:
Recursively searches ‘ARU_Data/’ for files
Copies only .wav and .flac files
NUM_FILES -> total files to copy
MAX_FILES -> Max files allowed in inputs at once

Depenencies:
config.py
ARU_DataHelper.py


## ARU_DataHelper.py:
The helper extracts information embedded in file paths or filenames and converts it into structured attributes that can be used throughout the pipeline.

Location (eg ARM)
Location_type
Date (YYYYMMDD)
Year, month, date
File_type

Key Methods:
input_lab_path(path): Extracts metadata from raw lab file path
input_formatted_filename(filename): Extracts metadata from standardized filename
to_formatted_filename(): Returns location_locationType_YYYYMMDD.wav
to_datetime(): Converts date to Python ‘datetime’ object
to_lab_path(root_directory): Finds original file location in lab directory


## weather_filter.py:
Filters recordings based on environmental conditions, such as wind speed and precipitation, using the Iowa Weather Mesonet. Recordings with poor weather conditions that may interfere with bird detections are removed from further processing.
How it works:
Read audio files from ‘/inputs’
Extracts metadata using “ARU_DataHelper’
Maps recording location -> weather station
Calls Iowa Environmental Mesonet API
Evaluates wind speed and precipitation
Moves bad files to ‘/skipped’

Thresholds are set in config.py and can be adjusted
MAX_WIND_MPH
MAX_PRECIP_INCHES

Key Features:
Converts wind from knots -> mph
Clean files remain in ‘/inputs’ and poor-quality files are moved to ‘/skiped’


## Birdnetlib_basics.py:
How it works:
Monitors inputs directory continuously
Detects new audio files
Processes files in paralle using multiprocessing
Runs BirdNET model on each file
Writes detections to CSV

Key Functions:
AnalyzeRecording(filename) -> runs BirdNet
Write_detections_to_csv saves the predictions
runBirdNet() -> continuous monitoring loop

Important Config Options are MIN_CONFIDENCE ad DELETE_INPUTS. The output will be csv files in ‘/outputs (one per audio file)

## Consolidate_outputs.py:
Combines all BirdNet output CSV files into a single master dataset for analysis 

How it works:
Reads all CSV files from outputs
Extracts metadata using ARU_DataHelper
Appedns columns (location, date, year, etc
Concatenates into one DataFrame
Standarsized column names 
Saves finaldataset 




