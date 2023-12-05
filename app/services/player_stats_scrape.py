import pandas as pd
import time
from icecream import ic

# Selenium Imports
from selenium.webdriver.common.by import By

# Local Imports
from app.crud.players import get_players
from app.services.selenium_setup import get_driver, CURRENT_YEAR
from sqlalchemy.orm import Session


pd.set_option('display.max_columns', None)

def get_player_stats(player_list=None):

    driver = get_driver()
    dict = get_players(db=Session)

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
        driver.get(f"{base_url}{url['url_end']}")
        time.sleep(8)

        rows = driver.find_elements(By.CSS_SELECTOR, "tr.css-79elbk")
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

get_player_stats()