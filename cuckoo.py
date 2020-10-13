from cuckoopi_py.eBirdQuery import eBirdQuery
from cuckoopi_py.XenoCantoQuery import XenoCantoQuery
from cuckoopi_py.FlickrQuery import FlickrQuery
import json
import schedule
import time
import os


## Create audio directory, if it doesn't exist
if not os.path_is_dir("cache"):
    os.system("mkdir cache")


## API Authentication Settings
with open("api_keys.json") as f:
    keys = json.load(f)

EBIRD_API_KEY = keys["EBIRD"]
FLICKR_API_KEY = keys["FLICKR_KEY"]
FLICKR_SECRET_KEY = keys["FLICKR_SECRET"]


## Function to download bird list, select a species, and download an audio file
def queue_audio():
    global local_audio_file
    global night
    global species
    records = 0
    ebird = eBirdQuery(EBIRD_API_KEY)
    ebird.get_recent_nearby_observations()
    while not records: 
        species = ebird.choose_a_species()
        xc = XenoCantoQuery(species)
        records = xc.num_records
    xc.get_audio()
    local_audio_file = xc.local_audio_file
    night = xc.night


## Get image of bird species from Flickr
def queue_photo():
    global local_photo_file
    flickr = FlickrQuery(species, FLICKR_API_KEY)
    flickr.get_photo()

## Play downloaded audio file
def play_audio():
    volume = 100
    if night:
        volume = 60
    cmd = f"ffplay {local_audio_file} -nodisp -autoexit -volume {volume}"
    os.system(cmd)


## Display downloaded photo
def display_image():
    cmd = f"pcmanfm --set-wallpaper {local_photo_file}"
    os.system(cmd)


## Schedule tasks
schedule.every().hour.at(":50").do(queue_audio)
schedule.every().hour.at(":52").do(queue_photo)
schedule.every().hour.at(":00").do(play_audio)
schedule.every().hour.at(":00").do(display_image)


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
