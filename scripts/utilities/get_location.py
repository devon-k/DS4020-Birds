from utilities.UTM2LatLong import utmToLatLong
from pathlib import Path
from shutil import copy
import pandas as pd

try:
    from config import ARU_COORDS_ADDRESS
except:
    ARU_COORDS_ADDRESS = None
try:
    from config import ARU_DEFAULT_COORDS, INPUTS_DIRECTORY
except:
    ARU_DEFAULT_COORDS = {'lat' : 42.0347, 'lon' : -93.6199}

PARENT_DIR = Path(__file__).parent.parent.parent.resolve()

if ARU_COORDS_ADDRESS is not None:
    COORDS_NETWORK = Path(ARU_COORDS_ADDRESS)
    COORDS_LOCAL = PARENT_DIR / INPUTS_DIRECTORY / COORDS_NETWORK.name
else:
    COORDS_NETWORK = None
    COORDS_LOCAL = None

def get_location_data(source : Path = COORDS_NETWORK, destination : Path = COORDS_LOCAL):
    """Downloads an existing csv index connecting ARU sites to their nad83 coordinates.
    
    By default, looks for the source and destination locations in the config file.

    This function could technically be used to copy any file from a location to a destination.
    """
    source = Path(source)
    destination = Path(destination)

    if ARU_COORDS_ADDRESS is not None:
        tempName = destination.parent / (source.name + ".tmp" )
        finalName = destination.parent / source.name
        try:
            copy(COORDS_NETWORK, tempName)

            tempName.rename(finalName)

        except:
            print("Failed to download ", source)

        finally:
            tempName.unlink(missing_ok= True)

def get_location(location, zone = 15):
    local_coords = None

    try:
        local_coords = pd.read_csv(COORDS_LOCAL, index_col="site")
    except:
        print("No usable coordinate index, loading default coordinates")
        return ARU_DEFAULT_COORDS["lat"], ARU_DEFAULT_COORDS["lon"]
    
    easting = local_coords.at[location, "nad83_easting_centroid"]
    northing = local_coords.at[location, "nad83_northing_centroid"]

    return utmToLatLong(utmNorthing=northing, utmEasting=easting, utmZone=zone)