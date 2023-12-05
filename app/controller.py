import datetime as dt
import pandas as pd
import time
from icecream import ic

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

from .main import get_players

### TAKE AWAY IMPORT, MOVE LOGIC TO CONTROLLER, HAVE MAIN ONLY BE THERE FOR THE ENDPOINTS AND CALL THE CONTROLLER FUNCTIONS



CURRENT_YEAR = dt.datetime.today().year
pd.set_option('display.max_columns', None)

class PgaScrape:
    def __init__(self):
        options = Options()
        service = Service(ChromeDriverManager().install()) # This installs the latest ChromeDriver on use
        # options.add_argument('--headless')  # Set to True to not open the webpage
        options.add_argument('--ignore-certificate-errors') # Ignores a random error oops
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options, service=service) # setup the driver when the class is initiated
    
    def get_player_info(self):
        url = 'https://www.pgatour.com/players' # Setting the players url
        self.driver.get(url) # Initializing the driver on the url - This opens the page
        time.sleep(3) # Giving the page time to load


        player_list = [] # Create empty player list

        # Find all of the players on the page

        players = self.driver.find_elements(By.CSS_SELECTOR, 'div.css-1vdhhui') # Grabs player element

        for player in players:
            player_info = player.find_element(By.CSS_SELECTOR, 'span.css-rdwj84 a') # This contains name & href

            player_name = player_info.get_attribute('aria-label') # Grabbing just the name

            player_link = player_info.get_attribute('href') # Grabbing the href
            player_id = ''.join(map(str, [int(i) for i in player_link if i.isdigit()])) # Parsing the href for the player_id

            player_nationality = player.find_element(By.CSS_SELECTOR, 'span.css-rbcrqz p').text
            
            # Okay lets put all the player info into a dict and then add to the player list to return
            player_dict = {"id": player_id, "name": player_name, "nationality": player_nationality}
            
            player_list.append(player_dict)
            
        return player_list
    
    def get_player_stats(self, player_list=None):

        dict = get_players()
        print(dict)

        base_url = "https://www.pgatour.com/stats/detail/"
        url_list = [{"name": "SG: Total", "url_end":"02675"}, 
                    {"name": "SG: T2G", "url_end":"02674"},
                    {"name": "SG: OTT", "url_end":"02567"},
                    {"name": "SG: APR", "url_end":"02568"},
                    {"name": "SG: ATG", "url_end":"02569"},
                    {"name": "SG: PUTT", "url_end":"02564"}]
        
        return_list = [{"player_name": 'Scottie Scheffler'}, {"player_name": 'Rory McIlroy'}]
        
        for url in url_list:
            stat_name = url["name"]
            self.driver.get(f"{base_url}{url['url_end']}")
            time.sleep(8)

            rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.css-79elbk")
            for row in rows:
                stat_dict = {}
                player_name = row.find_element(By.CSS_SELECTOR, "td.css-1y50yag").text
                average = row.find_element(By.CSS_SELECTOR, "td.css-mme8j7").text

                for dict in return_list:
                    if dict["player_name"] == player_name:
                        dict[stat_name] = average
                    else:
                        pass
            
        return return_list

    def get_tourney_info(self):
        pass

    def get_schedule_info(self):
        pass

# print(PgaScrape().get_player_stats())