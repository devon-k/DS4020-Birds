from pathlib import Path
from shutil import copy
from birdnetDataHelper import BirdnetDataHelper

ROOT = Path("z://").resolve() # This string needs to be the address of the lschulte-lab directory
SCRIPT_DIR = Path(__file__).absolute().parent.parent
DESTINATION = SCRIPT_DIR / "inputs"

def get_bird_file_paths(root_directory = ROOT, location : str = None, location_type : str = None, 
                        year : int = None, month : int = None, day : int = None ):
    """ Produces a generator (stream) of paths which contains all 
    the files inside the location-coded folders of the ARU_data.

    root_directory must be the path/address to the lshulte-lab directory.

    The generator currently includes a small number of files (361) which aren't audio.
    I don't think there is a good way around that so it has to be handled by the client 
    taking accepting the generator.
    """

    # Takes either a string or path, needs to convert str to path.
    if type(root_directory) == str:
        root_directory = Path(root_directory).resolve()

    lab_directory = root_directory / "ARU_data"

    glob_string = ""
    glob_string += (location if location != None else "???") + "/"
    glob_string += (f"*{location_type}*" if location_type != None else "*") + "/"
    glob_string += f"*{year or "????"}{month or "??"}{day or "??"}*"

    return lab_directory.glob(glob_string) #"???/*/*"

def copy_bird_audio(paths, destination = DESTINATION, num_files = -1):
    """ Copies a number of files from a collection of paths to a destination folder.

    paths can be a path, string, generator, or collection.
    
    Collects all files if num_files is set to -1.

    Filetames are changed to reflect their identifying values:
    [location]_[location_type]_[yyyymmdd][filetype]

    ex: ARM_CTL_20180301.wav
    """

    # Create destination if it doesn't exist
    if not destination.is_dir():
        destination.mkdir()

    # Handle single paths/strings
    if type(paths) == Path or type(paths) == str:
        if ".wav" in str(paths) or ".flac" in str(paths):
            print(f"Copying {str(paths)}")
            try:
                data_helper = BirdnetDataHelper()
                data_helper.input_lab_path(paths)
                new_file_name = data_helper.to_formatted_filename()
                
                copy(paths, destination + "/" + new_file_name)
            except Exception as e:
                print(f"Ran into a problem copying {str(paths)}")
                print(e)
                import traceback
                traceback.print_exc()
        else:
            print(f"Skipping {str(paths)}, not a compatible audio file.")

    # Handle collections/generators
    else:
        i = 0
        for path in paths:
            if i == num_files:
                break

            if ".wav" in str(path) or ".flac" in str(path):
                print(f"Copying {str(path)}")
                try:
                    data_helper = BirdnetDataHelper()
                    data_helper.input_lab_path(path)
                    new_file_name = data_helper.to_formatted_filename()
                    copy(path, destination / new_file_name)

                    i += 1
                except Exception as e:
                    print(f"Ran into a problem copying {str(path)}")
                    print(e)
                    import traceback
                    traceback.print_exc()
                    
            else:
                print(f"Skipping {str(path)}, not a compatible audio file.")

if __name__ == "__main__":
    file_paths = get_bird_file_paths()
    copy_bird_audio(file_paths, num_files=10)