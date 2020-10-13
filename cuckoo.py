from cuckoopi_py.eBirdQuery import eBirdQuery
from cuckoopi_py.XenoCantoQuery import XenoCantoQuery
import json
import schedule
import time
import os


## Create audio directory, if it doesn't exist
if not os.path_is_dir("audio"):
    os.system("mkdir audio")


## eBird Authentication Settings
with open("ebird_api_key.json") as f:
    key = json.load(f)

API_KEY = key["API_KEY"]


## Function to download bird list, select a species, and download an audio file
def queue_audio():
    global local_file
    global night
    records = 0
    while not records: 
        ebird = eBirdQuery(API_KEY)
        ebird.get_recent_nearby_observations()
        species = ebird.choose_a_species()
        xc = XenoCantoQuery(species)
        records = xc.num_records
    xc.get_audio()
    local_file = xc.local_audio_file
    night = xc.night


# Play downloaded audio file
def play_audio():
    volume = 100
    if night:
        volume = 60
    cmd = f"ffplay {local_file} -nodisp -autoexit -volume {volume}"
    os.system(cmd)


## Schedule tasks
schedule.every().hour.at(":55").do(queue_audio)
schedule.every().hour.at(":00").do(play_audio)


try:

    ## Main program loop
    while True:

        schedule.run_pending()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("CuckooPi has interrupted by a keyboard exit command.")

except:
    print("An error has occurred.")

finally:
    schedule.clear()  # Clean program exit
