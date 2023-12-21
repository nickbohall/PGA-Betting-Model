import pandas as pd
import time
from icecream import ic
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

# Selenium Imports
from selenium.webdriver.common.by import By

# Local Imports
from app.services.selenium_setup import get_driver, CURRENT_YEAR

pd.set_option('display.max_columns', None)

def get_tourney_info():
    driver = get_driver()

    url = 'https://www.pgatour.com/schedule/2022' # Setting the Schedule url
    driver.get(url) # Initializing the driver on the url - This opens the page
    time.sleep(3) # Giving the page time to load

    tourney_list = [] # Create empty player list

    # Find all tourneys on the page

    tourney_objects = driver.find_elements(By.CSS_SELECTOR, 'div.css-1itfnhz') # Grabs player element
    for tourney in tourney_objects:
        tourney_name = tourney.find_element(By.CSS_SELECTOR, 'p.css-vgdvwe').text
        try:
            tourney_link = tourney.find_element(By.CSS_SELECTOR, 'a.css-1jfg7sy').get_attribute('href')
            tourney_id = (tourney_link.split("/"))[-1]
        except:
            tourney_id = "not found"
        tourney_dict = {"tournament_id": tourney_id, "tournament_name": tourney_name}
        tourney_list.append(tourney_dict)
        
    return tourney_list


    