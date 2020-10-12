from cuckoopi_py.eBirdQuery import eBirdQuery
from cuckoopi_py.XenoCantoQuery import XenoCantoQuery
import json
import schedule
import time

## eBird Authentication Settings
with open("ebird_api_key.json") as f:
    key = json.load(f)

API_KEY = key["API_KEY"]


## Function to download bird list and select species at random
def play_a_bird():
    bird = eBirdQuery(API_KEY)
    bird.get_recent_nearby_observations()
    bird.choose_a_species()
    xc = XenoCantoQuery(bird.choose_a_species())
    xc.get_audio()
    schedule.every().minute(":00").do(xc.play_audio())
    xc.play_audio()


## Schedule task
schedule.every().minute.at(":55").do(play_a_bird())


## Main program loop
while True:
    schedule.run.pending()
    time.sleep(0.5)
