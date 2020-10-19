# REQUIRES FFMPEG TO BE INSTALLED ON LOCAL SYSTEM


import os
import pandas as pd
import requests
import schedule
from cuckoopi_py.check_directory import check_directory


class XenoCantoQuery:

    def __init__(self, Genus_species: str):

        self.genus = Genus_species.split(" ")[0].lower()
        self.species = Genus_species.split(" ")[1]
        self.search_string = f"{self.genus}+{self.species}"
        self.url = f"https://www.xeno-canto.org/api/2/recordings?query={self.search_string}+q:A+len:12-30"
        self.request()

    # Make HTTP request
    def request(self):

        # Define headers
        USER_AGENT_HEADERS = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        }

        # GET HTTP response
        response = requests.get(self.url, headers=USER_AGENT_HEADERS)

        # if response status code is 200
        if response:
            
            self.response_json = response.json()
            self.num_records = int(self.response_json["numRecordings"])
            print(f"{self.num_records} recordings found for {self.genus.capitalize()} {self.species}")

        else:

            print(f"Xeno-canto response status code did not return 200 (STATUS: {response.status_code})")

    def get_audio(self):

        if self.num_records > 0:
            
            row = pd.DataFrame(self.response_json["recordings"]).sample()
            file_path = row["file"].values[0]
            file_id = row["id"].values[0]
            self.remote_audio_file = "https:" + file_path
            work_dir = f"{os.getcwd()}/cache/{self.genus.capitalize()}_{self.species}"
            check_directory(work_dir)
            self.local_audio_file = f"{work_dir}/audio/{file_id}.mp3"
            if  os.path.isfile(self.local_audio_file):

                print("A copy of this file has already been downloaded.")

            else:

                os.system(f"wget -q -O {self.local_audio_file} {self.remote_audio_file}")
                print("Audio file download complete.\n")

        else:

            print("No audio records found.\n")


# ## Test
# xc_client = XenoCantoQuery("Strix varia")
# xc_client.get_audio()
