import pandas as pd
import time
from icecream import ic
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

# Selenium Imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Local Imports
from app.crud.players import get_players
from app.services.selenium_setup import get_driver, CURRENT_YEAR
from app.db.db_setup import get_db
from app.models import player


pd.set_option('display.max_columns', None)
def scrape_player_stats(db: Session, player_list=None):
    """
    Scrape player stats from the PGA Tour website.
    Will scrape all players found on the stats page, not just those in the database.
    
    Args:
        db: Database session
        player_list: Optional list of players to scrape stats for (not used anymore, kept for compatibility)
    
    Returns:
        List of dictionaries containing player stats
    """
    # Get players from the database for reference
    db_players = get_players(db)
    
    # Create a mapping of player names to IDs for reference
    player_name_to_id = {}
    if db_players:
        player_name_to_id = {player.name: player.id for player in db_players}
        print(f"Found {len(db_players)} players in the database for reference")
    else:
        print("No players found in the database. Will still scrape stats and create new player entries.")
    
    driver = get_driver()

    base_url = "https://www.pgatour.com/stats/detail/"
    url_list = [{"name": "SG: Total", "url_end":"02675"},
                {"name": "SG: T2G", "url_end":"02674"},
                {"name": "SG: OTT", "url_end":"02567"},
                {"name": "SG: APR", "url_end":"02568"},
                {"name": "SG: ATG", "url_end":"02569"},
                {"name": "SG: PUTT", "url_end":"02564"}]
    
    # We'll build the return list as we go, adding players as we find them
    return_list = []
    # Keep track of players we've already added to the return list
    processed_players = set()

    for url in url_list:
        stat_name = url["name"]
        print(f"Navigating to {stat_name} stats page...")
        driver.get(f"{base_url}{url['url_end']}")
        
        # Use explicit wait instead of fixed sleep
        try:
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.css-paaamq")))
            print(f"Stats table for {stat_name} loaded successfully")
        except TimeoutException:
            print(f"Timeout waiting for {stat_name} stats table to load. Continuing with available data...")
            # Wait a bit longer as fallback
            time.sleep(5)
        
        # Get all rows from the stats table
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.css-paaamq")
        print(f"Found {len(rows)} player entries for {stat_name}")
        
        # Process each row
        stats_found = 0
        for row in rows:
            try:
                player_name = row.find_element(By.CSS_SELECTOR, "td.css-bpavs2").text
                average = row.find_element(By.CSS_SELECTOR, "td.css-deko6d").text
                
                # Check if we've already processed this player
                if player_name not in processed_players:
                    # Create a new player entry
                    player_dict = {
                        "player_name": player_name,
                        "player_id": player_name_to_id.get(player_name),  # Will be None if not in database
                        "SG: Total": None,
                        "SG: T2G": None,
                        "SG: OTT": None,
                        "SG: APR": None,
                        "SG: ATG": None,
                        "SG: PUTT": None,
                        "stats_found": False
                    }
                    return_list.append(player_dict)
                    processed_players.add(player_name)
                
                # Find the player in our return list and add the stat
                for player_dict in return_list:
                    if player_dict["player_name"] == player_name:
                        try:
                            player_dict[stat_name] = float(average)
                            player_dict["stats_found"] = True  # Mark that we found at least one stat
                            stats_found += 1
                            break  # Found the player, no need to continue the loop
                        except ValueError:
                            # Handle case where average might not be a valid float
                            print(f"Warning: Could not convert stat value '{average}' to float for player {player_name}")
                            # Set to None instead of keeping the default value
                            player_dict[stat_name] = None
            except Exception as e:
                print(f"Error processing a row for {stat_name}: {e}")
                continue
                
        print(f"{stat_name} scraped! Found stats for {stats_found} players")
    # Count how many players have stats
    players_with_stats = sum(1 for player in return_list if player["stats_found"])
    print(f"Found stats for {players_with_stats} out of {len(return_list)} players")
    
    # Remove the stats_found tracking field before returning
    for player in return_list:
        if "stats_found" in player:
            del player["stats_found"]
    
    print("Scrape Successful - Attempting to post to DB\n")
    return return_list
