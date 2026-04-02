from pathlib import Path
from datetime import datetime

class ARUDataHelper():
    """A helper object which collects and translates information about STRIPS ARU audio files.

    Used extensively by the ARU Bird Audio project to pass information through the pipeline.

    Attributes:
        lab_path (Path)
        formatted_filename (str)
        file_type (str)
        location (str)
        location_type (str)
        date (str)
        year (str)
        month (str)
        day (str)
        hour (str)
        minute (str)

    """
        
    def __init__(self):
        self.lab_path = None
        self.formatted_filename = None

        self.file_type = None
        self.location = None
        self.location_type = None
        self.date = None
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None

    def input_lab_path(self, path):
        """Takes a path for a STRIPS ARU audio file to load the dataHelper.
        
        The format of compatible paths are <site> / <sub_site_type> / <audio_file>
        
        """

        if type(path) == str:
            path = Path(path)

        self.lab_path = path

        filename = path.name
        self.file_type = "." + filename.split(".")[-1]
        self.location = path.parent.parent.name
        self.location_type = path.parent.name.split("_")[1]
        self.date = filename.split("_")[-2]
        self.time = filename.split("_")[-1].split('.')[0]
        self.year = filename.split("_")[-2][0:4]
        self.month = filename.split("_")[-2][4:6]
        self.day = filename.split("_")[-2][6:8]
        self.hour = filename.split("_")[-1][0:2]
        self.minute = filename.split("_")[-1][2:4]

        self.to_formatted_filename()

    def input_formatted_filename(self, filename):
        """Takes a formatted filename (from this class) for an STRIPS ARU audio file to load the dataHelper.

        This input is friendly to inputs from older versions of this handler which don't include time data.

        """

        filename = Path(filename).name

        self.formatted_filename = filename
        self.file_type = "." + self.formatted_filename.split(".")[-1]

        split_filename = self.formatted_filename.split("_")
        self.location = split_filename[0]
        self.location_type = split_filename[1]
        self.date = split_filename[2]
        self.year = self.date[0:4]
        self.month = self.date[4:6]
        self.day = self.date[6:8]

        try:
            self.time = split_filename[3].split('.')[0]
            self.hour = self.time[0:2]
            self.minute = self.time[2:4]
        except:
            self.legacy = True
            self.time = "000000"
            self.hour = "00"
            self.minute = "00"

        self.lab_path = None

    def to_formatted_filename(self) -> str:
        """Generates a filename which encodes the relevant data about the loaded file."""

        if self.file_type == None:
            raise Exception("Cannot create formatted filename, BirdnetDataHelper is missing required data or is empty.")

        self.formatted_filename = self.location + "_" + self.location_type + "_" + self.date + "_" + self.time + self.file_type
        return self.formatted_filename

    def to_lab_path(self, root_directory):
        """Performs a search to find the path to the original location of a file with a formatted filename.

        Requires the local root directory to do perform the search, returns a path if one file is found,
        a list of paths if more than one possible path is found (this should only happen if the input data 
        is incomplete somehow), or None if no path is found.
        """

        if self.file_type == None:
            raise Exception("Error: BirdnetDataHelper is missing required data or is empty.")
        
        if type(root_directory) == str:
            root_directory = Path(root_directory).resolve()

        lab_directory = root_directory / "ARU_data"

        glob_string = ""
        glob_string += (self.location if self.location != None else "???") + "/"
        glob_string += (f"*{self.location_type}*" if self.location_type != None else "*") + "/"
        glob_string += f"*{self.year or '????'}{self.month or '??'}{self.day or '??'}*"

        possible_paths = list(lab_directory.glob(glob_string))

        if len(possible_paths) == 0:
            # print("Lab path not found")
            return None
        elif len(possible_paths) == 1:
            self.lab_path = possible_paths[0]
            return possible_paths[0]
        else:
            # print("Many possible paths found")
            return possible_paths
        
    def to_datetime(self):
        return datetime(year = int(self.year), month = int(self.month), day = int(self.day), 
                        hour= int(self.hour), minute = int(self.minute))