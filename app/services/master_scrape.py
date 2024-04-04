import pandas as pd
import time
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

def get_current_tourney( db: Session, tourney_name, year=CURRENT_YEAR, tourney_id=None):
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
        try:
            odds = int((row.find_element(By.CSS_SELECTOR, "span.css-1yh709r").text).replace("+", ''))
        except:
            odds = 6969

        tourney_dict = {
                        "year": year, 
                        "tourney_id": tourney_id,
                        "tourney_name": tourney_name,
                        "player_name": player_name, 
                        "odds": odds
                    }
        output_list.append(tourney_dict)
    print(f"{tourney_name} scraped. Adding to db")

    return output_list