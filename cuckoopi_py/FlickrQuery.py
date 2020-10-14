import os
import requests
import json
import re
import random
from cuckoopi_py.check_directory import check_directory


class FlickrQuery:

    def __init__(self, Genus_species: str, api_key: str):

        self.genus = Genus_species.split(" ")[0].lower()
        self.species = Genus_species.split(" ")[1]
        self.search_string = f"{self.genus}+{self.species}"
        self.url = f"https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={api_key}&" \
                   f"format=json&text={self.search_string}&privacy_filter=1&content_type=1"
        self.request()

    def format_json(self, x: str):
        
        x = re.compile("jsonFlickrApi\\(").sub("", x)
        x = re.compile("\\)$").sub("", x)
        return json.loads(x)

    # Make HTTP request
    def request(self):
        
        # Define headers
        USER_AGENT_HEADERS = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"}

        # GET HTTP response
        response = requests.get(self.url, headers=USER_AGENT_HEADERS)

        # if response status code is 200
        if response:

            try:

                self.response = self.format_json(response.text)

            except:
                
                self.num_records = 0
                print("Something went wrong. No records received.")

        else:
            
            print(f"WARNING: Webpage response status code did not return 200 (STATUS: {response.status_code})")

    def get_photo(self):
        
        photos = self.response["photos"]["photo"]
        index = random.randint(0, len(photos))
        photo_info = photos[0]
        self.remote_photo_file = f"https://live.staticflickr.com/{photo_info['server']}/{photo_info['id']}_{photo_info['secret']}_b.jpg"
        work_dir = f"{os.getcwd()}/cache/{self.genus.capitalize()}_{self.species}"
        check_directory(work_dir)
        self.local_photo_file = f"{work_dir}/photo/{photo_info['id']}.jpg"
        os.system(f"wget -O {self.local_photo_file} {self.remote_photo_file}")
        return self.local_photo_file
