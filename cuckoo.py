#!/usr/bin/python3

from cuckoopi.eBirdQuery import eBirdQuery
from cuckoopi.XenoCantoQuery import XenoCantoQuery
from cuckoopi.FlickrQuery import FlickrQuery
from cuckoopi.AllAboutBirdsScraper import AllAboutBirdsScraper
from cuckoopi.text_to_image import text_to_image
from cuckoopi.lcddriver import LCD
import json
import schedule
import time
import os
import RPi.GPIO as GPIO
from multiprocessing import Process
from time import sleep, strftime
from PIL import Image
import pygame


## Global variables (set defaults)
def default_vars():

    global local_audio_file, local_photo_file, local_info_file, queued_species, queued_common_name
    local_audio_file = "config/default_audio.mp3"
    local_photo_file = "config/default_photo.jpg"
    local_info_file = "config/default_info.jpg"
    queued_species = "Strix varia"
    queued_common_name = "Barred Owl"


## Detect when tactile button is pressed, play current audio file when it is
def playback_event():

    GPIO.add_event_detect(PUSH_BUTTON,
                          GPIO.FALLING,
                          callback=lambda x: playback(True),
                          bouncetime=5000)


## Detect when info button is pressed, display text
def information_event():

    GPIO.add_event_detect(INFO_BUTTON,
                          GPIO.FALLING,
                          callback=lambda x: show_info(),
                          bouncetime=15000)
                          

## Clear cache directory periodically
def clear_cache():

    os.system("sudo rm -r cache/")
    os.system("mkdir cache")


## Get a bird species in the local area
def get_bird_observations():

    """
    The function queries eBird to find bird species spotted in the local area within the last two weeks.
    """

    # eBird REST client
    global ebird, queued_common_name, queued_species
    opts = {
        "api_key":EBIRD_API_KEY, 
        "latitude":38.54, 
        "longitude":-121.74,
        "search_radius":20,  # kilometers
        "back":7  # days
        }

    ebird = eBirdQuery(**opts)

    # Search for recent bird observations
    species_found = False
    counter = 0
    while not species_found:

        if counter < 20:
            
            species_found = ebird.get_recent_nearby_observations()
            time.sleep(5) # Check again in 5 seconds
        
        else:

            # If no records are found, return default values:
            default_vars()
            print("eBird records not returned in the maximum number of attempts (20). Using default values")
            return
            
        counter += 1
    
    queued_species, queued_common_name = ebird.choose_a_species()
    return queued_species, queued_common_name


## Get audio recording from xeno-canto
def queue_audio():
    
    global queued_audio_file

    # Check xeno-canto for audio records of the selected bird    
    records = 0
    counter = 0

    while not records:

        if counter < 10:

            xc = XenoCantoQuery(queued_species)
            records = xc.num_records

        else:

            print("No xeno-canto records found in 10 attempts. Selecting default values.")
            queued_audio_file = "config/default_audio.mp3"
            break
        
        counter += 1

    # When found, download the file, normalize the levels, and add fade effects
    if records > 0:

        xc.get_audio()
        queued_audio_file = xc.local_audio_file
    
    path = queued_audio_file.split(".")[0] + "_temp.mp3"
    cmd = f"ffmpeg-normalize {queued_audio_file} -c:a libmp3lame -b:a 192k -f -o {path}" \
          f"&& rm {path}"

    try:

    	os.system(cmd)

    except:

        print("There was an error formating the audio file. Reverting to default")
        queued_audio_file = "config/default_audio.mp3"
    
    return


## Get image of bird species from Flickr
def queue_photo():
    
    global queued_photo_file
    flickr = FlickrQuery(queued_species, FLICKR_API_KEY)
    queued_photo_file = flickr.get_photo()
    #Check aspect ratio of queued file
    im = Image.open(queued_photo_file)
    if im.size[0]/im.size[1] > 1:
        return
    else:
        queue_photo()


## Play downloaded audio file
def play_audio():

    if "ebird" in globals():

        night = ebird.night

    else:

        night = 0

    # Adjust volume depending on the time of day (keep low to prevent clipping)
    volume = 0.8

    if night:

        volume = 0.55
    
    # cmd = f"(sudo amixer cset numid=1 {volume}% && play -q {local_audio_file}) &"
    # os.system(cmd)

    # Now using pygame module for audio playback rather than amixer
    pygame.mixer.init()
    pygame.mixer.music.load(local_audio_file)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.fadeout(3000)  # 3 seconds fade out
    pygame.mixer.music.play()
    
    return


## Display downloaded photo as fullscreen image
def display_photo(sleep: int):
    
    temp_photo_file = local_photo_file.split(".")[0] + "_temp.jpg"
    if os.path.isfile(f"{temp_photo_file}"):
        os.system(f"rm {temp_photo_file}")
    os.system(f"cp {local_photo_file} {temp_photo_file}")
    text_to_image(temp_photo_file, common_name, species)
    
    # Use 'feh' to diplay queued photo file
    os.system(f"feh -F -x -Z -Y -G {temp_photo_file} &")
    os.system("sleep 0.5 && xscreensaver-command -deactivate")    
    os.system(f"sleep {sleep}")  # How long to display before reverting to blank
    os.system("xscreensaver-command -activate")
    os.system("pkill feh")
    
    return


## Show a description of the bird species for 15 seconds
def show_info():

    GPIO.remove_event_detect(INFO_BUTTON)  # temporarily disable event detection to prevent duplicate inputs
    
    # Get information
    global local_info_file
    gen, spec = species.split(" ")
    file_path = f"{os.getcwd()}/cache/{gen.capitalize()}_{spec}/photo/info.jpg"
    
    if not os.path.isfile(file_path):

        aab = AllAboutBirdsScraper(common_name, species)
        aab.request()
        local_info_file = aab.format_description()

    else:

        local_info_file = file_path

    # Screen management
    os.system(f"feh -F -x -Z -Y -G {local_info_file} &")
    os.system("sleep 0.5 && xscreensaver-command -deactivate")    
    os.system(f"sleep 15")  # How long to display before reverting to blank
    os.system("xscreensaver-command -activate")
    os.system("pkill feh")

    information_event()  # re-enable event detection


## Run parallel processes during playback events
def playback(repeat: bool):

    GPIO.remove_event_detect(PUSH_BUTTON)  # temporarily disable event detection to prevent duplicate inputs

    sleep = 45
    if not repeat:

        global species, common_name, local_audio_file, local_photo_file
        species = queued_species
        common_name = queued_common_name
        local_photo_file = queued_photo_file
        local_audio_file = queued_audio_file
        sleep = 120

    functions = [play_audio(), display_photo(sleep)]
    proc = []

    for fxn in functions:

        p = Process(target=fxn)
        p.start()
        proc.append(p)

    for p in proc:

        p.join()
    
    playback_event()


## Queue file function
def queue_files():
    
    global queued_species, queued_common_name
    queued_species, queued_common_name = get_bird_observations()
    queue_audio()
    queue_photo()


try:

    ## Create media file directory, if it doesn't exist
    if not os.path.isdir("cache"):
        
        os.system("mkdir cache")

    ## API authentication keys
    with open("api_keys.json") as f:
        keys = json.load(f)

    EBIRD_API_KEY = keys["EBIRD"]
    FLICKR_API_KEY = keys["FLICKR_KEY"]


    ## GPIO pin settings and options
    PUSH_BUTTON = 8
    INFO_BUTTON = 7
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering scheme
    GPIO.setwarnings(False)  # Disable warnings
    GPIO.setup(PUSH_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Push button input (initial value is up)
    GPIO.setup(INFO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Info button input (initial value is up)

    ## Start up
    os.system("xscreensaver-command -activate")  # Blank screen
    default_vars()  # Set initial globals
    playback_event()  # Start GPIO event listener
    information_event()  # ""
    os.system("python3 display_time.py &")  # start LCD clock

    ## Schedule tasks to run on time
    schedule.every().hour.at(":50").do(queue_files)
    schedule.every().hour.at(":00").do(playback, False)
    schedule.every().sunday.at("00:30").do(clear_cache)

    ## Initialize
    queue_files()
    playback(False)

    ## Main program loop
    while True:

        schedule.run_pending()
        time.sleep(1)

except KeyboardInterrupt:

    print("CuckooPi was interrupted by a keyboard exit command.")

except:

    print("An error has occurred.")

finally:

    # Clean program exit
    GPIO.cleanup()  
    schedule.clear()
    LCD().lcd_clear()
