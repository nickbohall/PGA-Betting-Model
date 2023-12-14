import pandas as pd
import time
from icecream import ic
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

# Selenium Imports
from selenium.webdriver.common.by import By

# Local Imports
# from selenium_setup import get_driver, CURRENT_YEAR
from app.crud.tournaments import get_tournament_names, get_tournament_ids
from app.db.db_setup import get_db
from app.models import tournament   
from app.services.selenium_setup import get_driver, CURRENT_YEAR

pd.set_option('display.max_columns', None)

def get_schedule_info(db: Session, tourney_list=None):

    
    tourney_id_object = get_tournament_ids(db=db)
    tourney_id_list = [tourney_id_object[0] for tourney_id_object in tourney_id_object]

    tourney_name_object = get_tournament_names(db=db)
    tourney_name_list = [tourney_name_object[0] for tourney_name_object in tourney_name_object]
    tourney_name_list = ["-".join(map(lambda x: x.lower(), name.split())) for name in tourney_name_list]

    if not tourney_name_list or not tourney_id_list:
        print("could not get tourney list")
    else:

        # years = list(range(CURRENT_YEAR - 5, CURRENT_YEAR - 1))
        years = [2021]
        tourney_list = []

        for tourney_id, tourney_name in zip(tourney_id_list, tourney_name_list):
            if tourney_id == "not found":
                pass
            else:
                tourney_dict = {"tourney_id": tourney_id, "tourney_name": tourney_name}
                tourney_list.append(tourney_dict)

        output_list = []

        driver = get_driver()

        for year in years:
            for tourney in tourney_list:
                tourney_id = tourney['tourney_id']
                tourney_name = tourney['tourney_name']
                url = f"https://www.pgatour.com/tournaments/{year}/{tourney_name}/{tourney_id}/past-results"
                driver.get(url)
                time.sleep(3)
                rows = driver.find_elements(By.CSS_SELECTOR, "tr.css-79elbk")
                for row in rows:
                    pos = row.find_element(By.CSS_SELECTOR, "span.css-1bn4ecd").text
                    player = row.find_element(By.CSS_SELECTOR, "td.css-182plxy a").get_attribute('href')
                    score = row.find_elements(By.CSS_SELECTOR, "span.css-1q3u2k7")[-2].text

                    # Parsing the information - Person Info
                    href_split = player.split("/")
                    player_name = href_split[-1].split("-")[0] + " " + href_split[-1].split("-")[-1]
                    player_id = ''.join(map(str, [int(i) for i in href_split if i.isdigit()]))

                    # Handling Cuts and ties
                    if pos == "CUT":
                        pos = 99
                    elif "T" in pos:
                        pos = int(pos.replace('T', ''))
                    elif pos == "W/D":
                        pos = 98
                    elif pos == "NAN":
                        pos = 101
                    elif pos == "DQ":
                        pos = 98
                    else: 
                        pos = int(pos)

                    # Handling Even
                    if score == "E":
                        score = 0
                    elif score == "NAN":
                        score = 99
                    else: 
                        score = int(score)

                    tourney_dict = {
                        "year": year, 
                        "tourney_id": tourney_id,
                        "tourney_name": tourney_name,
                        "player_name": player_name, 
                        "player_id": player_id,
                        "finish": pos,
                        "score": score,
                    }
                    print(tourney_name)
                    print(player_name, player_id, pos, score)
                    output_list.append(tourney_dict)
        return output_list