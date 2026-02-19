from pathlib import Path
from shutil import copy

ROOT = Path("z://").resolve()
LAB_DIRECTORY = ROOT / "ARU_data"
DESTINATION = Path("inputs")

def get_bird_file_paths(root_directory = LAB_DIRECTORY):
    """ Generates a collection of paths which contains all 
    the files inside the location-coded folders of the ARU_data.

    You'll need to create the proper root directory path for your own computer.
    """
    return root_directory.glob("???/*/*")

def copy_bird_audio(paths, destination = DESTINATION, num_files = -1):
    """ Copies a number of files from a collection of paths to a destination folder.

    Collects all files if num_files is set to -1.
    """
    
    for i, path in enumerate(paths):
        if i == num_files:
            break
        copy(path, DESTINATION)

if __name__ == "__main__":
    file_paths = get_bird_file_paths()
    copy_bird_audio(file_paths, num_files=1)