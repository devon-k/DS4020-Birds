from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import json
import time
import datetime
#import ffmpeg as ff

#ff.input("notepad++ situation is crazy.webm").output("notepad.wav").run()



start = time.perf_counter()

try:
    analyzer = Analyzer()

    analyzer_start = time.perf_counter()

    recording = Recording(
        analyzer,
        "clean_STRIPS2_0+1_20150520_053500.wav",
        min_conf=0.80,
        lat = 42.0347,
        lon = -93.6199,
        date = datetime.datetime(year = 2015, month = 5, day = 20)
    )

    recording.analyze()
    end1 = time.perf_counter()
    print(f"Analysis complete: {end1-analyzer_start}")

    with open("clean_STRIPS2_0+1_20150520_053500.json", "w") as file:
        json.dump(recording.detections, file, indent = 4)

finally:
    end = time.perf_counter()
    print(f"Program complete: {end-start}")