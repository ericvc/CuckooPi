import requests
from bs4 import BeautifulSoup
from cuckoopi.text_to_image import description_to_image
from cuckoopi.check_directory import check_directory
import os
import re


class AllAboutBirdsScraper:


    def __init__(self, common_name: str, Genus_species: str):

        self.genus = Genus_species.split(" ")[0].lower()
        self.species = Genus_species.split(" ")[1]
        self.common_name = common_name.replace(" ", "_").replace("'","")
        self.url = f"https://www.allaboutbirds.org/guide/{self.common_name}/"
        self.work_dir = f"{os.getcwd()}/cache/{self.genus.capitalize()}_{self.species}"


    def request(self):

        # Define headers
        USER_AGENT_HEADERS = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        }

        # GET HTTP response
        response = requests.get(self.url, headers=USER_AGENT_HEADERS)

        # if response status code is 200
        if response:
            
            try:

                #Parse HTML response
                soup = BeautifulSoup(response.text, 'html.parser')
                #Locate description text in HTML response
                div = soup.find('div', {"class": "speciesInfoCard float clearfix"})
                desc = str(div.find("p"))  # Find paragraph tag within div class
                desc = re.compile("</?[a-zA-Z]+>").sub("", desc) # Removes HTML tags
                desc = re.compile("^\\[").sub("", desc) # Removes paragraph tags
                self.description = re.compile("\\]$").sub("", desc) # Removes paragraph tags
            
            except:

                self.description = "(No description could be found. Sorry!)"  # if error
                print("While trying to get a bird description, an error occurred.")

        else:

            print("WARNING: Webpage response status code did not return 200 (STATUS: %d)" % response.status_code)


    def format_description(self):

        line_width = 80  # number characters per line
        words = self.description.split(" ")
        # Containers
        lines = []
        text = ""
        # Sequentially adds words to a string until they would exceed character limit (line_width)
        while words:
            if (len(text) + len(words[0]) + 1) <  line_width:
                text = text + " " + words[0]
                del words[0]
            else:
                lines.append(text)
                text = ""
        lines.append(text)
        self.frmt_desc = "\n".join(lines)  # Add 'new line' character to the end of each line
        # Save output
        check_directory(self.work_dir)
        self.local_info_file = f"{self.work_dir}/photo/info.jpg"
        if not os.path.isfile(self.local_info_file):
            
            description_to_image(self.local_info_file, self.frmt_desc)

        return self.local_info_file
