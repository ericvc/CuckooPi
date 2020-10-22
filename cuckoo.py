#!/usr/bin/python3

from cuckoopi_py.eBirdQuery import eBirdQuery
from cuckoopi_py.XenoCantoQuery import XenoCantoQuery
from cuckoopi_py.FlickrQuery import FlickrQuery
from cuckoopi_py.AllAboutBirdsScraper import AllAboutBirdsScraper
from cuckoopi_py.text_to_image import text_to_image
from cuckoopi_py.lcddriver import LCD
import json
import schedule
import time
import os
import RPi.GPIO as GPIO
from multiprocessing import Process
from time import sleep, strftime


## Global variables (set defaults)
def default_vars():

    global local_audio_file, local_photo_file, local_info_file, species, common_name
    local_audio_file = "config/default_audio.mp3"
    local_photo_file = "config/default_photo.jpg"
    local_info_file = "config/default_info.jpg"
    species = "Strix varia"
    common_name = "Barred Owl"


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
    global ebird, common_name, species
    lat = 38.54  # 2 decimal limit
    lon = -121.74  # 2 decimal limit
    search_radius = 20  # kilometers
    back = 7  # how many days back to search
    
    ebird = eBirdQuery(EBIRD_API_KEY, latitude=lat, longitude=lon, back=back, search_radius=search_radius)

    # Search for recent bird observations
    species_found = False
    counter = 0
    while not species_found:

        if counter < 20:
            
            species_found = ebird.get_recent_nearby_observations()
            time.sleep(5) # Check again in 5 seconds
        
        else:

            # If no records are found, return default values:
            raise ValueError("eBird records not returned in the maximum number of attempts (20).")

        counter += 1
    
    species, common_name = ebird.choose_a_species()
    return species, common_name


## Get audio recording from xeno-canto
def queue_audio():
    
    global queued_audio_file

    # Check xeno-canto for audio records of the selected bird    
    records = 0
    counter = 0

    while not records:

        if counter < 10:

            xc = XenoCantoQuery(species)
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
          f"&& sox {path} {queued_audio_file} fade h 0:1 0 0:3" \
          f"&& rm {path}"
    os.system(cmd)
    
    return


## Get image of bird species from Flickr
def queue_photo():
    
    global queued_photo_file
    flickr = FlickrQuery(species, FLICKR_API_KEY)
    queued_photo_file = flickr.get_photo()
    
    return


## Play downloaded audio file
def play_audio(repeat: bool):

    if "ebird" in globals():

        night = ebird.night

    else:

        night = 0

    # Adjust volume depending on the time of day
    volume = 100

    if night:

        volume = 65
    
    if not repeat:

        global local_audio_file
        local_audio_file = queued_audio_file

    cmd = f"(sudo amixer cset numid=1 {volume}% && play -q {local_audio_file}) &"
    os.system(cmd)
    
    return


## Display downloaded photo as fullscreen image
def display_photo(repeat: bool):

    global local_photo_file
    temp_photo_file = local_photo_file.split(".")[0] + "_temp.jpg"
    
    if repeat:
        
        sleep = 45

    else:
    
        if os.path.isfile(f"{temp_photo_file}"):
            os.system(f"rm {temp_photo_file}")
        local_photo_file = queued_photo_file
        temp_photo_file = local_photo_file.split(".")[0] + "_temp.jpg"
        os.system(f"cp {local_photo_file} {temp_photo_file}")
        text_to_image(temp_photo_file, common_name, species)
        sleep = 120
    
    # Use 'feh' to diplay queued photo file
    os.system(f"feh -F -x -Z -Y -G {temp_photo_file} &")
    os.system("sleep 0.1 && xscreensaver-command -deactivate")    
    os.system(f"sleep {sleep}")  # How long to display before reverting to blank
    os.system("xscreensaver-command -activate")
    os.system("pkill feh")
    
    return


## Show a description of the bird species for 15 seconds
def show_info():
    
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
    os.system("sleep 0.1 && xscreensaver-command -deactivate")    
    os.system(f"sleep 15")  # How long to display before reverting to blank
    os.system("xscreensaver-command -activate")
    os.system("pkill feh")


## Run parallel processes during playback events
def playback(repeat: bool):

    if repeat:
         
        GPIO.remove_event_detect(PUSH_BUTTON)

    functions = [play_audio(repeat), display_photo(repeat)]
    proc = []

    for fxn in functions:

        p = Process(target=fxn)
        p.start()
        proc.append(p)

    for p in proc:

        p.join()

    if repeat:

        playback_event()


## Queue file function
def queue_files():
    
    get_bird_observations()
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
    lcd = LCD()

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
    playback_event()  # Start GPIO event listeners
    information_event()  # ""
    lcd = LCD()  #  Initialize LCD display driver
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
    lcd.lcd_clear()
