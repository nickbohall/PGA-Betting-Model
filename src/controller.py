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



CURRENT_YEAR = dt.datetime.today().year
pd.set_option('display.max_columns', None)

class PgaScrape:
    def __init__(self):
        options = Options()
        service = Service(ChromeDriverManager().install()) # This installs the latest ChromeDriver on use
        options.add_argument('--headless')  # Set to True to not open the webpage
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
        url = 'https://www.pgatour.com/stats' # Setting the base stats url

        player_list = [{"player_id": "01226", "player_name": "Fred Couples"}, {"player_id":"01249", "player_name": "John Daly"}]
        player_stats = [] # Create empty list to put the data
        # Loop through the player list and go get their individual stats - This is probably gonna take a minute..
        for player in player_list:

            player_id = player["player_id"]
            player_name = "-".join([x.lower() for x in player["player_name"].split(" ")])

            stat_dict = {"player_id": player_id} # Creating a dict to put stats into

            url = f"https://www.pgatour.com/player/{player_id}/{player_name}/stats" # Grabbing url based on id and name

            self.driver.get(url) # Initializing the driver on the url - This opens the page
            time.sleep(10) # Giving the page time to load
            
            stats = self.driver.find_elements(By.CSS_SELECTOR, 'tr.css-79elbk')
            
            for stat in stats: # Loop through the stats and add them to the dict
                stat_name = stat.find_element(By.CSS_SELECTOR, 'td.css-3g81zr').text
                stat_value = stat.find_element(By.CSS_SELECTOR, 'td.css-4afaty span').text
                stat_dict[stat_name] = stat_value
            
            player_stats.append(stat_dict)

        return player_stats
                
                
            

    def get_tourney_info(self):
        pass

    def get_schedule_info(self):
        pass

print(PgaScrape().get_player_stats())