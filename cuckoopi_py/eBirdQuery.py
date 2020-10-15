import urllib
import requests
import json
import pandas as pd
from datetime import datetime
from pvlib.solarposition import get_solarposition


class eBirdQuery:

    def __init__(self, api_key, latitude: float=-999., longitude: float=-999.):

        self.lat = latitude
        self.lon = longitude
        self.api_key = api_key
        self.location_lookup()
        self.check_time_of_day()

    ## Check whether it is day or night
    def check_time_of_day(self):

        current_time = "{:%Y-%m-%d %H:%M:%S}".format(datetime.utcnow())
        time = pd.DatetimeIndex([current_time], tz='utc')
        pos = get_solarposition(time, self.lat, self.lon)
        if pos["elevation"][0] < 0:

            self.night = 1
            print("Auto-detect thinks it is night time.")
            
        else:

            print("Auto-detect thinks it is day time.")
            self.night = 0

    def night_birds(self):
        
        nocturnal_taxa = [
            "ORDER1 in 'Strigiformes'",
            "or FAMILY in 'Caprimulgidae (Nightjars and Allies)'",
            "or FAMILY in 'Aegothelidae (Owlet-nightjars)'",
            "or FAMILY in 'Podargidae (Frogmouths)'",
            "or FAMILY in 'Nyctibiidae (Potoos)'"
            ]
        ebird_taxonomy = pd.read_csv("eBird_Taxonomy_v2019.csv").query(" ".join(nocturnal_taxa))
        return list(ebird_taxonomy["SPECIES_CODE"])

    ## Get Location Information from IP Address
    def location_lookup(self):

        if self.lon != -999 and self.lon != -999:
            assert -180. < self.lon < 180.
            assert -90. < self.lat < 90.
            location = json.load(urllib.request.urlopen('http://ipinfo.io/json'))
            self.tz = location["timezone"]
            print(f"Local timezone determined from IP address: {self.tz}")
            return

        else:

            print("No coordinates provided. Determining approximate location from IP address.")

            try:
                
                location = json.load(urllib.request.urlopen('http://ipinfo.io/json'))
                lat, lon = location["loc"].split(",")
                self.lat = float(lat)
                self.lon = float(lon)
                self.tz = location["timezone"]
                self.city = location["city"]
                print(f"Approximate location from IP address: City: {self.city} - Latitude: {self.lat}, Longitude: {self.lon}\n")
                
            except urllib.error.HTTPError:
                
                print("Error: could not determine your approximate location.")

    ## Get recent nearby observations of birds
    def get_recent_nearby_observations(self):
        
        url = "https://api.ebird.org/v2/data/obs/geo/recent?lat=%.2f&lng=%.2f&sort=species&dist=50" % (self.lat, self.lon)
        print(url)
        response = requests.request("GET", url, headers={'X-eBirdApiToken': self.api_key}, data={})
        
        # if response status code is 200
        if response:

            self.recent_nearby_obs = pd.DataFrame(response.json())
            print(f"eBird observation records found.")

            # Subset based on diurnal vs nocturnal taxa
            if self.night:

                self.recent_nearby_obs = self.recent_nearby_obs.query(f"speciesCode in {self.night_birds()}")
            
            else:
                
                self.recent_nearby_obs = self.recent_nearby_obs.query(f"speciesCode not in {self.night_birds()}")
                
            self.num_nearby_records = self.recent_nearby_obs.shape[0]
            print(f"{self.num_nearby_records} records returned.")
            return True

        else:

            print("Something went wrong. No eBird records received. Trying again...")
            return False

    ## Get notable nearby observations of birds
    def get_recent_notable_nearby_observations(self):
        
        url = "https://api.ebird.org/v2/data/obs/geo/recent/notable?lat=%.2f&lng=%.2f&sort=species&dist=50" % (self.lat, self.lon)
        response = requests.request("GET", url, headers={'X-eBirdApiToken': self.api_key}, data={})
        
        # if response status code is 200
        if response:

            self.recent_notable_nearby_obs = pd.DataFrame(response.json())
            print(f"eBird observation records found.")
            
            # Subset based on diurnal vs nocturnal taxa
            if self.night:

                self.recent_notable_nearby_obs = self.recent_notable_nearby_obs.query(f"speciesCode in {self.night_birds()}")
            
            else:
                
                self.recent_notable_nearby_obs = self.recent_notable_nearby_obs.query(f"speciesCode not in {self.night_birds()}")
                
            self.num_notable_nearby_records = self.recent_notable_nearby_obs.shape[0]
            print(f"{self.num_notable_nearby_records} notable records returned.")
            return True

        else:

            print(f"Something went wrong. No notable eBird records received (status: {response.status_code}). Trying again...")
            return False

    ## Get recent nearby observations of birds
    def choose_a_species(self):
        
        row = self.recent_nearby_obs.sample()
        common_name = row["comName"].values[0]
        sci_name = row["sciName"].values[0]
        print(f"Species selected: {sci_name} - {common_name}")
        return sci_name, common_name

    ## Get recent nearby observations of birds
    def choose_a_notable_species(self):

        row = self.recent_nearby_notable_obs.sample()
        common_name = row["comName"].values[0]
        sci_name = row["sciName"].values[0]
        print(f"Notable species selected: {sci_name} - {common_name}")
        return sci_name, common_name
