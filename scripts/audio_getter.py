from ARU_DataHelper import ARUDataHelper
from copy_inputs import copy_bird_audio
import config

print("_"*40,"\n")
print("Welcome to Nick's bird audio file-getter!")
print("_"*40)

print("\nType 'Help' for instructions\n")

name = input("Copy paste the formatted_filename':" ).replace(".csv", "").upper()

if "HELP" in name:
    print("""There are no rules, good luck""")
    exit()

if " " in name:
    names = name.split(" ")
else:
    names = [name]

# if len(names) > 1:
#     print(f"Getting {len(names)} files")
# else


for name in names:
    helper = ARUDataHelper()
    helper.input_formatted_filename(name)
    file_path = helper.to_lab_path(config.LAB_DIRECTORY)

    if file_path == None:
        print("Path not found, maybe you misspelled something?")

    helper = ARUDataHelper()
    helper.input_lab_path(file_path)

    print("Getting", file_path.name)

    try: 
        copy_bird_audio(file_path, max_files= None)
        print("\tSuccess: Name reformatted to:", helper.to_formatted_filename())
    except:
        print(file_path.name, "Not got for some reason :(")