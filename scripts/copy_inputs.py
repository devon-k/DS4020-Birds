from pathlib import Path
from shutil import copy

ROOT = Path("z://").resolve() # This string needs to be the address of the lschulte-lab directory
SCRIPT_DIR = Path(__file__).absolute().parent.parent
DESTINATION = SCRIPT_DIR / "inputs"

def get_bird_file_paths(root_directory = ROOT):
    """ Produces a generator (stream) of paths which contains all 
    the files inside the location-coded folders of the ARU_data.

    Just needs the path to the network folder containing the data.

    The generator currently includes a small number of files (361) which aren't audio.
    I don't think there is a good way around that so it has to be handled by the client taking accepting the generator.
    """

    # Takes either a string or path, needs to convert str to path.
    if type(root_directory) == str:
        root_directory = Path(root_directory).resolve()

    lab_directory = root_directory / "ARU_data"
    return lab_directory.glob("???/*/*")

#TODO - Add filtering options, maybe random selection.

def copy_bird_audio(paths, destination = DESTINATION, num_files = -1):
    """ Copies a number of files from a collection of paths to a destination folder.

    paths can be a path, string, generator, or collection.
    Collects all files if num_files is set to -1.
    """

    #TODO - Add necessary information to filenames OR export an index which contains it.
    #TODO - Add error handling

    # Create destination if it doesn't exist
    if not destination.is_dir():
        destination.mkdir()

    # Handle single paths/strings
    if type(paths) == Path or type(paths) == str:
        if ".wav" in str(path) or ".flac" in str(path):
            copy(path, DESTINATION)
    # Handle collections/generators
    else:
        i = 0
        for path in paths:
            if i == num_files:
                break

            if ".wav" in str(path) or ".flac" in str(path):
                print(f"Copying {str(path)}")
                copy(path, DESTINATION)
                i += 1
            else:
                print(f"Skipping {str(path)}")

if __name__ == "__main__":
    file_paths = get_bird_file_paths()
    copy_bird_audio(file_paths, num_files=10)