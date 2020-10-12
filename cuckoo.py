from cuckoopi_py.eBirdQuery import eBirdQuery
from cuckoopi_py.XenoCantoQuery import XenoCantoQuery
import json
import schedule


## eBird Authentication Settings
with open("ebird_api_key.json") as f:
    key = json.load(f)

API_KEY = key["API_KEY"]


## Function to download bird list, select a species, and download an audio file
def play_a_bird():
    opts = {"volume": 100}
    ebird = eBirdQuery(API_KEY)
    ebird.get_recent_nearby_observations()
    species = ebird.choose_a_species()
    if ebird.night:
        opts["volume"] = 60
    xc = XenoCantoQuery(species)
    xc.get_audio()
    schedule.every().minute(":00").do(xc.play_audio(**opts))


## Schedule task
schedule.every().minute.at(":55").do(play_a_bird())


## Main program loop
while True:
    schedule.run.pending()
    time.sleep(0.5)
