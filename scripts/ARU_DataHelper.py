from pathlib import Path

class BirdnetDataHelper():
        
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

    def input_lab_path(self, path):
        """
        Takes a path for an ARU birds audio file to load the dataHelper.

        * location
        * location_type
        * date
        * year
        * month
        * day
        * file_type
        """

        if type(path) == str:
            path = Path(path)

        self.lab_path = path

        split_path = str(path).split("\\")
        self.file_type = "." + split_path[-1].split(".")[-1]
        self.location = split_path[-3]
        self.location_type = split_path[-2].split("_")[1]
        self.date = split_path[-1].split("_")[-2]
        self.year = split_path[-1].split("_")[-2][0:4]
        self.month = split_path[-1].split("_")[-2][4:6]
        self.day = split_path[-1].split("_")[-2][6:8]

        self.to_formatted_filename()

    def input_formatted_filename(self, filename):
        """
        Takes a formatted filename for an ARU birds audio file to load the dataHelper.
        * location
        * location_type
        * date
        * year
        * month
        * day
        * file_type
        """

        filename = str(filename)

        self.formatted_filename = filename.split("\\")[-1]
        self.file_type = "." + self.formatted_filename.split(".")[-1]

        split_filename = self.formatted_filename.split("_")
        self.location = split_filename[0]
        self.location_type = split_filename[1]
        self.date = split_filename[2]
        self.year = self.date[0:4]
        self.month = self.date[4:6]
        self.day = self.date[6:8]

    def to_formatted_filename(self):
        if self.file_type == None:
            raise Exception("Cannot create formatted filename, BirdnetDataHelper is missing required data or is empty.")

        self.formatted_filename = self.location + "_" + self.location_type + "_" + self.date + self.file_type
        return self.formatted_filename

    def to_lab_path(self, root_directory):
        """
        Performs a search to find the path to the original location of a file with a formatted filename.

        Requires the local lshulte-lab root directory to do perform the search.

        Docstring for to_lab_path
        
        :param self: Description
        :param root_directory: The path or address to the lshulte-lab directory.
        :type root_directory: Path
        """

        if self.file_type == None:
            raise Exception("Cannot find lab_path, BirdnetDataHelper is missing required data or is empty.")
        
        if type(root_directory) == str:
            root_directory = Path(root_directory).resolve()

        lab_directory = root_directory / "ARU_data"

        glob_string = ""
        glob_string += (self.location if self.location != None else "???") + "/"
        glob_string += (f"*{self.location_type}*" if self.location_type != None else "*") + "/"
        glob_string += f"*{self.year or "????"}{self.month or "??"}{self.day or "??"}*"

        possible_paths = list(lab_directory.glob(glob_string))

        if len(possible_paths) == 0:
            print("Lab path not found")
            return None
        elif len(possible_paths) == 1:
            self.lab_path = possible_paths[0]
            return possible_paths[0]
        else:
            print("Many possibilities found")
            return possible_paths