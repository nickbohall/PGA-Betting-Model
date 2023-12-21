import pandas as pd
import time
from icecream import ic
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

# Selenium Imports
from selenium.webdriver.common.by import By

# Local Imports
from app.crud.players import get_player_names
from app.services.selenium_setup import get_driver, CURRENT_YEAR
from app.db.db_setup import get_db
from app.models import player

pd.set_option('display.max_columns', None)

def scrape_player_stats(db: Session, player_list=None):

    # Using a get request to get all player names from db
    player_object = get_player_names(db=db)
    player_list = [player_object[0] for player_object in player_object] # Turning the object to a list
    print(len(player_list))

    
    if not player_list:
        print("could not get player_list")
    else: 
        driver = get_driver()

        base_url = "https://www.pgatour.com/stats/detail/"
        url_list = [{"name": "SG: Total", "url_end":"02675"}, 
                    {"name": "SG: T2G", "url_end":"02674"},
                    {"name": "SG: OTT", "url_end":"02567"},
                    {"name": "SG: APR", "url_end":"02568"},
                    {"name": "SG: ATG", "url_end":"02569"},
                    {"name": "SG: PUTT", "url_end":"02564"}]
        
        return_list = [{"player_name": player} for player in player_list]

        for url in url_list:
            stat_name = url["name"]
            driver.get(f"{base_url}{url['url_end']}")
            time.sleep(8)

            rows = driver.find_elements(By.CSS_SELECTOR, "tr.css-79elbk")
            for row in rows:
                player_name = row.find_element(By.CSS_SELECTOR, "td.css-1y50yag").text
                average = row.find_element(By.CSS_SELECTOR, "td.css-mme8j7").text

                for dict in return_list:
                    if dict["player_name"] == player_name:
                        dict[stat_name] = float(average)
                    else:
                        pass

        return return_list
