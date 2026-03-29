from utilities.UTM2LatLong import utmToLatLong
from pathlib import Path
from shutil import copy
import pandas as pd

try:
    from config import ARU_COORDS_ADDRESS
except:
    ARU_COORDS_ADDRESS = None
try:
    from scripts.config import ARU_DEFAULT_COORDS
except:
    ARU_DEFAULT_COORDS = {'lat' : 42.0347, 'lon' : -93.6199}

PARENT_DIR = Path(__file__).parent.parent.parent.resolve()
if ARU_COORDS_ADDRESS is not None:
    COORDS_NETWORK = Path(ARU_COORDS_ADDRESS)
    COORDS_LOCAL = PARENT_DIR / "data" / COORDS_NETWORK.name
else:
    COORDS_NETWORK = None
    COORDS_LOCAL = None


def get_location(location, zone = 15):
    local_coords = None

    # if ARU_COORDS_ADDRESS is not None:
    #     tempName = COORDS_LOCAL.parent / (COORDS_NETWORK.name + ".tmp" )
    #     finalName = COORDS_LOCAL.parent / COORDS_NETWORK.name
    #     try:
    #         copy(COORDS_NETWORK, tempName)

    #         tempName.rename(finalName)

    #     except:
    #         print("Failed to download ", COORDS_NETWORK)

    #     finally:
    #         tempName.unlink(missing_ok= True)

    try:
        local_coords = pd.read_csv(COORDS_LOCAL, index_col="site")
    except:
        print("No usable coordinate index, loading default coordinates")
        return ARU_DEFAULT_COORDS["lat"], ARU_DEFAULT_COORDS["lon"]
    
    easting = local_coords.at[location, "nad83_easting_centroid"]
    northing = local_coords.at[location, "nad83_northing_centroid"]

    print(northing, easting)

    return utmToLatLong(utmNorthing=northing, utmEasting=easting, utmZone=zone)