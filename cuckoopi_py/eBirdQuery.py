import urllib
import requests
import json
import pandas as pd


class eBirdQuery:

    def __init__(self, api_key):
        self.location_lookup()
        self.api_key = api_key
        self.headers = {'X-eBirdApiToken': self.api_key}

    ## Get Location Information from IP Address
    def location_lookup(self):
        try:
            location = json.load(urllib.request.urlopen('http://ipinfo.io/json'))
            lat, lon = location["loc"].split(",")
            self.lat = float(lat)
            self.lon = float(lon)
            print(f"Approximate location: Latitude: {self.lat}, Longitude: {self.lon}")
        except urllib.error.HTTPError:
            print("Error: could not determine location.")

    ## Get recent nearby observations of birds
    def get_recent_nearby_observations(self):
        url = "https://api.ebird.org/v2/data/obs/geo/recent?lat=%.2f&lng=%.2f&sort=species" % (self.lat, self.lon)
        response = requests.request("GET", url, headers=self.headers, data={})
        self.recent_nearby_obs = pd.DataFrame(response.json())

    ## Get recent nearby observations of birds
    def choose_a_species(self):
        row = self.recent_nearby_obs.sample()
        common_name = row["comName"].values[0]
        sci_name = row["sciName"].values[0]
        print(f"Species selected: {sci_name} - {common_name}")
        return sci_name
