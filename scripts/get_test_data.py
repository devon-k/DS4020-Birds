from copy_inputs import get_bird_file_paths, copy_bird_audio
import pandas as pd
from pathlib import Path
import random
from config import LAB_DIRECTORY, NUM_FILES, INPUTS_DIRECTORY

def get_labelled_audio(num_files, destination = None):
    """ Collects a number of audio files from a collection of 106 human labelled examples.

    Copies all files if num_files = -1, uses the config default destination folder if destination is None.

    Does not automatically collect the information on these files, 
    recommended using the data_helper to filter the labelled_bird_audio.csv.
    """

    labelled = pd.read_csv("labelled_bird_audio.csv")
    labelled_list = []

    for i in pd.unique(labelled["Path"]):
        labelled_list.append(Path(LAB_DIRECTORY) / "ARU_data" / Path(i))

    if num_files >= 0:
        sample = random.sample(labelled_list, num_files)
    else:
        sample = labelled_list

    if destination != None:
        copy_bird_audio(sample, destination)
    else:
        copy_bird_audio(sample)

if __name__ == "__main__":
    random.seed(27)
    get_labelled_audio(NUM_FILES)