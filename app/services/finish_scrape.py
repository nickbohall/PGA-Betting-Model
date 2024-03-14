import pandas as pd
import time
from icecream import ic
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from datetime import datetime

# Selenium Imports
from selenium.webdriver.common.by import By

# Local Imports
from app.services.selenium_setup import get_driver, CURRENT_YEAR
from app.models.tournament import Tournament

# db import 
from sqlalchemy.orm import Session

pd.set_option('display.max_columns', None)

def get_current_tourney_finish( db: Session, tourney_name, year=CURRENT_YEAR, tourney_id=None):
    driver = get_driver()

    tourney_id = db.query(Tournament).filter(Tournament.tourney_name == tourney_name).first().tourney_id
    dashed_tourney_name = "-".join(tourney_name.split(" "))

    url = f"https://www.pgatour.com/tournaments/{year}/{dashed_tourney_name}/{tourney_id}"

    driver.get(url)
    time.sleep(3)

    output_list = []

    rows = driver.find_elements(By.CSS_SELECTOR, "tr.css-1qtrmek")

    for row in rows:
        player_name = row.find_element(By.CSS_SELECTOR, "td.css-1y9jg86 span").text
        player_finish_str = row.find_element(By.CSS_SELECTOR, "td.css-ryx8py span").text
        player_score_str = row.find_element(By.CSS_SELECTOR, "td.css-l4z11p span").text

        if player_finish_str == "CUT":
            player_finish = 99
        elif player_finish_str == "W/D" or player_finish_str == "WD":
            player_finish = 98
        elif player_finish_str == "NAN":
            player_finish = 98 
        elif player_finish_str == "DQ":
            player_finish = 98
        else:  
            player_finish = int(player_finish_str.replace("T", ""))

        if player_score_str == "E":
            player_score = 0
        elif player_score_str == "-":
            player_score = 99
        else:
            player_score = int(player_score_str)
        
        tourney_dict = {
                        "year": year, 
                        "tourney_id": tourney_id,
                        "tourney_name": tourney_name,
                        "player_name": player_name, 
                        "player_finish": player_finish, 
                        "player_score": player_score
                    }
        output_list.append(tourney_dict)

    print(f"{tourney_name} finishes scraped. Adding to db")
    print(output_list)

    return output_list