import urllib
import requests
import json
import pandas as pd
from datetime import datetime
from pvlib.solarposition import get_solarposition


class eBirdQuery:

    def __init__(self, api_key):
        self.location_lookup()
        self.check_time_of_day()
        self.headers = {'X-eBirdApiToken': api_key}

    ## Check whether it is day or night
    def check_time_of_day(self):
        current_time = "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())
        time = pd.DatetimeIndex([current_time], tz=self.tz)
        pos = get_solarposition(time, self.lat, self.lon)
        if pos["elevation"][0] < 0:
            self.night = 1
        else:
            self.night =0

    def night_birds(self):
        ebird_taxonomy = pd.read_csv("eBird_Taxonomy_v2019.csv").query(
            "ORDER1 in 'Strigiformes' or ORDER1 in 'Caprimulgiformes'")
        return list(ebird_taxonomy["SPECIES_CODE"])

    ## Get Location Information from IP Address
    def location_lookup(self):
        try:
            location = json.load(urllib.request.urlopen('http://ipinfo.io/json'))
            lat, lon = location["loc"].split(",")
            self.lat = float(lat)
            self.lon = float(lon)
            self.tz = location["timezone"]
            print(f"Approximate location: Latitude: {self.lat}, Longitude: {self.lon}")
        except urllib.error.HTTPError:
            print("Error: could not determine location.")

    ## Get recent nearby observations of birds
    def get_recent_nearby_observations(self):
        url = "https://api.ebird.org/v2/data/obs/geo/recent?lat=%.2f&lng=%.2f&sort=species&dist=50" % (self.lat, self.lon)
        response = requests.request("GET", url, headers=self.headers, data={})
        self.recent_nearby_obs = pd.DataFrame(response.json())
        if self.night == 1:
            self.recent_nearby_obs = self.recent_nearby_obs.query(f"speciesCode in {self.night_birds()}")
        self.num_nearby_records = self.recent_nearby_obs.shape[0]
        print(f"{self.num_nearby_records} records returned.")
    
    ## Get notable nearby observations of birds
    def get_recent_notable_nearby_observations(self):
        url = "https://api.ebird.org/v2/data/obs/geo/recent/notable?lat=%.2f&lng=%.2f&sort=species&dist=50" % (self.lat, self.lon)
        response = requests.request("GET", url, headers=self.headers, data={})
        self.recent_nearby_notable_obs = pd.DataFrame(response.json())
        self.num_nearby_notable_records = self.recent_nearby_obs.shape[0]
        print(f"{self.num_nearby_notable_records} notable records returned.")

    ## Get recent nearby observations of birds
    def choose_a_species(self):
        row = self.recent_nearby_obs.sample()
        common_name = row["comName"].values[0]
        sci_name = row["sciName"].values[0]
        print(f"Species selected: {sci_name} - {common_name}")
        return sci_name

    ## Get recent nearby observations of birds
    def choose_a_notable_species(self):
        row = self.recent_nearby_notable_obs.sample()
        common_name = row["comName"].values[0]
        sci_name = row["sciName"].values[0]
        print(f"Species selected: {sci_name} - {common_name}")
        return sci_name
