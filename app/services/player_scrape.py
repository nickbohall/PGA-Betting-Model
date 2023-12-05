import datetime as dt
import pandas as pd
import time
from icecream import ic

# Selenium Imports
from selenium.webdriver.common.by import By

# Local Imports
from app.services.selenium_setup import get_driver, CURRENT_YEAR


pd.set_option('display.max_columns', None)


def get_player_info():

    driver = get_driver()

    url = 'https://www.pgatour.com/players' # Setting the players url
    driver.get(url) # Initializing the driver on the url - This opens the page
    time.sleep(3) # Giving the page time to load


    player_list = [] # Create empty player list

    # Find all of the players on the page

    players = driver.find_elements(By.CSS_SELECTOR, 'div.css-1vdhhui') # Grabs player element

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