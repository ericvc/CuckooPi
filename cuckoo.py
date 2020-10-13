from cuckoopi_py.eBirdQuery import eBirdQuery
from cuckoopi_py.XenoCantoQuery import XenoCantoQuery
from cuckoopi_py.FlickrQuery import FlickrQuery
import json
import schedule
import time
import os


## Create audio directory, if it doesn't exist
if not os.path.isdir("cache"):
    
    os.system("mkdir cache")


## API Authentication Settings
with open("api_keys.json") as f:
    keys = json.load(f)

EBIRD_API_KEY = keys["EBIRD"]
FLICKR_API_KEY = keys["FLICKR_KEY"]


## Function to download bird list, select a species, and download an audio file
def queue_audio():
    
    global local_audio_file
    global night
    global species

    ebird = eBirdQuery(EBIRD_API_KEY)

    species_found = False
    counter = 0
    
    while not species_found:

        if counter < 20:
            
            species_found = ebird.get_recent_nearby_observations()
            time.sleep(10) # Check again in 10 seconds
        
        else:

            print("eBird records not returned in the maximum number of attempts.")
            local_audio_file = "default_audio.mp3"
            night = 0
            break

        counter += 1
    
                
    records = 0
    
    while not records: 
        species = ebird.choose_a_species()
        xc = XenoCantoQuery(species)
        records = xc.num_records
    
    xc.get_audio()
    local_audio_file = xc.local_audio_file
    night = xc.night
    return


## Get image of bird species from Flickr
def queue_photo():
    
    global local_photo_file
    flickr = FlickrQuery(species, FLICKR_API_KEY)
    local_photo_file = flickr.get_photo()
    return


## Play downloaded audio file
def play_audio():

    volume = 100
    if night:
        volume = 60
    cmd = f"ffplay {local_audio_file} -nodisp -autoexit -volume {volume} &"
    os.system(cmd)
    return


## Display downloaded photo as background image
def display_image():
    
    cmd = f"feh --bg-scale {local_photo_file} &"
    os.system(cmd)
    print("Changing background image.\n")
    return


## Schedule tasks
schedule.every().hour.at(":50").do(queue_audio)
schedule.every().hour.at(":50").do(queue_photo)
schedule.every().hour.at(":00").do(play_audio)
schedule.every().hour.at(":00").do(display_image)


try:

    ## Main program loop
    while True:

        schedule.run_pending()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("CuckooPi was interrupted by a keyboard exit command.")

except:
    print("An error has occurred.")

finally:
    schedule.clear()  # Clean program exit
