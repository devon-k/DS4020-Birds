from birdnetlib_basics import OUTPUTS_DIR, INPUTS_DIR, AnalyzeRecording, write_detections_to_csv, deleteAudioFile, write_detections_to_csv
from copy_inputs import get_bird_file_paths, copy_bird_audio
import consolidate_outputs
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path
import config
import time

inputs_dir = Path(INPUTS_DIR)
outputs_dir = Path(OUTPUTS_DIR)

def download_handler():
    filepaths = get_bird_file_paths()

    count = 0

    for a in filepaths:
        if count >= config.NUM_FILES:
            return False
        time.sleep(1)
        while ( sum(1 for i in Path(INPUTS_DIR).glob("*.flac")) + sum(1 for i in Path(INPUTS_DIR).glob("*.wav")) ) >= config.MAX_PROCESSES*2:
            print("\rDownloader is sleeping...", end = "\r")
            time.sleep(10)
        copy_bird_audio(a)
        # with open(Path("data\\" + a.name), "w"):
        #     pass
        count +=1
            

def process_audio(path : Path):
    # File processing thread
    filename = path.name

    try:
        recording = AnalyzeRecording(filename)
        #deleteAudioFile(filename)
        write_detections_to_csv(recording, filename.replace("res_",""))
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        import traceback
        traceback.print_exc()

    deleteAudioFile(filename)

def main():
    # Create output directory
    Path(OUTPUTS_DIR).mkdir(exist_ok=True)

    # Create ThreadPoolExecutor
    max_workers = min(cpu_count, config.MAX_PROCESSES+1) # Max_processes + 1 because the download handler isn't resource intensive.
    with ThreadPoolExecutor(max_workers = max_workers) as executor: 

        # Create downloader process
        executor.submit(download_handler)
        time.sleep(5)

        timer = time.time()
        while True:
            if len( list(inputs_dir.glob("*.flac") ) + list(inputs_dir.glob("*.wav")) ) < 1:
                # Kill program statement, I wasn't able to find another way to achieve this. 
                # We can adjust this, I figured this was an overly safe cut-off.
                if time.time() - timer > 30: 
                    print("Program complete, terminating.")
                    executor.shutdown()
                    exit()
                continue
            else:
                timer = time.time() # Resets timer if theres any files still to be processed
                for a in ( list(inputs_dir.glob("*.flac") ) + list(inputs_dir.glob("*.wav")) ):
                    if "res_" in str(a.name): # Skip reserved files
                        continue
                    try:
                        a = a.rename(a.parent / ("res_" + str(a.name)) ) # Reserve file
                        executor.submit(process_audio, a)
                    except FileNotFoundError: pass

if __name__ == "__main__":
    BASE_DIR = Path(__file__).absolute().parent.parent
    main()
      
    consolidate_outputs.consolidate_outputs(
        outputs_dir=BASE_DIR / "outputs",
        compiled_dir=BASE_DIR / "compiled",
        min_confidence=config.MIN_CONFIDENCE
    )

# asyncronus
