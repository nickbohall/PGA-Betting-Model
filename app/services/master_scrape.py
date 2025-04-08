import pandas as pd
import time
import logging
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from datetime import datetime, date
import traceback

# Configure logging for this module
logger = logging.getLogger("pga_betting_model.master_scrape")

# Selenium Imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException

# Local Imports
from app.services.selenium_setup import get_driver, CURRENT_YEAR
from app.models.tournament import Tournament
from app.models.player import Player
from app.models.master import Master
from app.db.db_setup import SessionLocal

pd.set_option('display.max_columns', None)

def scrape_master_data():
    """
    Main function to scrape tournament results for all tournaments and add to master table.
    This function:
    1. Gets all tournaments from the database
    2. For each tournament, scrapes the player results
    3. Adds all results to the master table
    """
    driver = None
    try:
        # Initialize database session
        db = SessionLocal()
        
        try:
            # Get all tournaments from the database
            logger.info("Fetching all tournaments from database...")
            tournaments = db.query(Tournament).all()
            
            if not tournaments:
                logger.warning("No tournaments found in database. Please run tournament scraper first.")
                return {"status": "error", "message": "No tournaments found in database"}
            
            logger.info(f"Found {len(tournaments)} tournaments in database.")
            
            # Initialize the Selenium driver
            logger.info("Initializing Selenium driver...")
            driver = get_driver()
            
            # Create a list to store all master data
            all_master_data = []
            
            # Get today's date
            today = date.today()
            logger.info(f"Today's date: {today}")
            
            # Filter tournaments that happened before today
            filtered_tournaments = []
            for tournament in tournaments:
                if tournament.tournament_date:
                    try:
                        # Parse the tournament date string to a date object
                        # The format should be YYYY-MM-DD
                        tournament_date = datetime.strptime(tournament.tournament_date, "%Y-%m-%d").date()
                        if tournament_date <= today:
                            filtered_tournaments.append(tournament)
                            logger.info(f"Including tournament {tournament.tournament_name} with date {tournament_date}")
                        else:
                            logger.info(f"Skipping future tournament {tournament.tournament_name} with date {tournament_date}")
                    except (ValueError, TypeError) as e:
                        # Try to extract year from tournament.year
                        try:
                            # If we can't parse the date but have a year, check if it's this year or earlier
                            if tournament.year and tournament.year < today.year:
                                logger.info(f"Including tournament {tournament.tournament_name} from past year {tournament.year}")
                                filtered_tournaments.append(tournament)
                            elif tournament.year and tournament.year == today.year:
                                # For current year tournaments with unparseable dates, skip them to be safe
                                logger.warning(f"Skipping tournament {tournament.tournament_name} from current year with unparseable date: {tournament.tournament_date}")
                            else:
                                logger.warning(f"Skipping tournament {tournament.tournament_name} with unparseable date '{tournament.tournament_date}': {e}")
                        except Exception as year_error:
                            logger.warning(f"Error checking year for tournament {tournament.tournament_name}: {year_error}")
                            logger.warning(f"Skipping tournament with unparseable date")
                else:
                    # If tournament_date is not available, check the year
                    if tournament.year and tournament.year < today.year:
                        # Include tournaments from past years even without dates
                        logger.info(f"Including tournament {tournament.tournament_name} from past year {tournament.year} (no date available)")
                        filtered_tournaments.append(tournament)
                    else:
                        logger.warning(f"Skipping tournament {tournament.tournament_name} with no date available")
            
            logger.info(f"Filtered to {len(filtered_tournaments)} tournaments that happened before today.")
            
            # Loop through each filtered tournament
            for tournament in filtered_tournaments:
                try:
                    logger.info(f"Processing tournament: {tournament.tournament_name}")
                    
                    # Get tournament results
                    tournament_results = get_tournament_results(
                        driver=driver,
                        db=db,
                        tournament_name=tournament.tournament_name,
                        tournament_id=tournament.tournament_id,
                        year=tournament.year,
                        course_name=tournament.course_name
                    )
                    
                    if tournament_results:
                        all_master_data.extend(tournament_results)
                        logger.info(f"Added {len(tournament_results)} results for {tournament.tournament_name}")
                    else:
                        logger.warning(f"No results found for tournament: {tournament.tournament_name}")
                
                except WebDriverException as e:
                    logger.error(f"WebDriver error processing tournament {tournament.tournament_name}: {e}")
                    # Try to recreate the driver if it crashed
                    try:
                        if driver:
                            driver.quit()
                        logger.info("Recreating WebDriver after error...")
                        driver = get_driver()
                    except Exception as driver_error:
                        logger.error(f"Failed to recreate WebDriver: {driver_error}")
                        break
                except Exception as e:
                    logger.error(f"Error processing tournament {tournament.tournament_name}: {e}")
                    continue
            
            # Add all data to the master table
            if all_master_data:
                logger.info(f"Adding {len(all_master_data)} total records to master table")
                add_to_master_table(db, all_master_data)
                return {"status": "success", "message": f"Added {len(all_master_data)} records to master table"}
            else:
                logger.warning("No data collected for master table")
                return {"status": "warning", "message": "No data collected for master table"}
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"An error occurred during master data scraping: {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": f"Error: {str(e)}"}
    
    finally:
        # Ensure the driver is closed even if errors occur
        if driver:
            try:
                logger.info("Closing Selenium driver...")
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing Selenium driver: {e}")

def get_tournament_results(driver, db=None, tournament_name=None, tournament_id=None, year=CURRENT_YEAR, course_name=None):
    """
    Get tournament results for a specific tournament with improved error handling.
    
    Args:
        driver: Selenium WebDriver instance
        db: Database session (optional, can be None when just scraping)
        tournament_name: Name of the tournament
        tournament_id: ID of the tournament
        year: Year of the tournament (default: current year)
        course_name: Name of the course (optional)
        
    Returns:
        List of dictionaries containing tournament results
    """
    try:
        # Format tournament name for URL (replace spaces with dashes and remove special characters)
        dashed_tournament_name = "-".join(
            "".join(c if c.isalnum() or c.isspace() else ' ' for c in tournament_name.lower()).split()
        )
        
        # Construct URL
        url = f"https://www.pgatour.com/tournaments/{year}/{dashed_tournament_name}/{tournament_id}"
        
        logger.info(f"Navigating to {url}...")
        driver.get(url)
        
        # Wait for page to load with explicit wait instead of sleep
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.css-1qtrmek, .leaderboard-table"))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for leaderboard data for {tournament_name}. Trying alternative selector...")
            try:
                # Try alternative selector
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".leaderboard-wrap, .leaderboard"))
                )
            except TimeoutException:
                logger.warning(f"No leaderboard found for tournament: {tournament_name}. URL structure may have changed.")
                return []
        
        output_list = []
        
        # Try multiple CSS selectors for player rows to handle different page structures
        row_selectors = [
            "tr.css-1qtrmek", 
            "tr[class*='css-1qtrmek']",
            ".player-[0-9]+ tr",
            ".leaderboard-table tbody tr",
            ".leaderboard-row",
            ".table-data-row"
        ]
        
        rows = []
        for selector in row_selectors:
            rows = driver.find_elements(By.CSS_SELECTOR, selector)
            if rows:
                logger.info(f"Found {len(rows)} player rows using selector: {selector}")
                break
        
        if not rows:
            logger.warning(f"No player rows found for tournament: {tournament_name}")
            return []
        
        # Try multiple selector combinations for player data based on exact HTML structure
        name_selectors = [".css-hmig5c", "span.chakra-text.css-hmig5c", ".player-name", "[data-testid='playerName']"]
        
        # The finish position is in the first TD with class css-11dj2vk > span.css-1psnea4
        finish_selectors = [
            "td.css-11dj2vk span.css-1psnea4", 
            "td[scope='row'] span.chakra-text", 
            "td:first-child span.chakra-text",
            ".position span", 
            ".pos"
        ]
        
        # The score is in a span with class css-11aoq3v
        score_selectors = [".css-11aoq3v", "span.chakra-text.css-11aoq3v", ".to-par", "[data-testid='score']"]
        
        for row in rows:
            try:
                # Find player name using multiple selectors
                player_name = None
                for selector in name_selectors:
                    try:
                        name_element = row.find_element(By.CSS_SELECTOR, selector)
                        player_name = name_element.text.strip()
                        if player_name:
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
                
                if not player_name:
                    logger.warning("Could not find player name, skipping row")
                    continue
                
                # Find player finish using multiple selectors
                player_finish_str = None
                for selector in finish_selectors:
                    try:
                        # First try direct access using find_element
                        finish_element = row.find_element(By.CSS_SELECTOR, selector)
                        player_finish_str = finish_element.text.strip()
                        if player_finish_str:
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
                
                # If we still don't have a finish position, try a more general approach
                if not player_finish_str:
                    try:
                        # Look for the first cell in the row
                        first_td = row.find_element(By.TAG_NAME, "td")
                        # Try to find a span within it
                        spans = first_td.find_elements(By.TAG_NAME, "span")
                        if spans:
                            player_finish_str = spans[0].text.strip()
                    except (NoSuchElementException, StaleElementReferenceException, IndexError):
                        logger.warning(f"Could not find finish position for player {player_name} using alternative method")
                        
                if not player_finish_str:
                    logger.warning(f"Could not find finish position for player {player_name}, using 'N/A'")
                    player_finish_str = "N/A"
                
                # Find player score using multiple selectors
                player_score_str = None
                for selector in score_selectors:
                    try:
                        score_element = row.find_element(By.CSS_SELECTOR, selector)
                        player_score_str = score_element.text.strip()
                        if player_score_str:
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
                
                # If we still don't have a score, try to find it in the fourth column which typically has the score
                if not player_score_str:
                    try:
                        # Get all cells in the row
                        all_cells = row.find_elements(By.TAG_NAME, "td")
                        # The score is usually in the 4th column (index 3)
                        if len(all_cells) > 3:
                            score_cell = all_cells[3]
                            spans = score_cell.find_elements(By.TAG_NAME, "span")
                            if spans:
                                player_score_str = spans[0].text.strip()
                    except (NoSuchElementException, StaleElementReferenceException, IndexError):
                        logger.warning(f"Could not find score for player {player_name} using alternative method")
                
                if not player_score_str:
                    logger.warning(f"Could not find score for player {player_name}, using placeholder")
                    player_score_str = "-"
                
                # Process player finish
                if player_finish_str in ["CUT", "C"]:
                    player_finish = 99
                elif player_finish_str in ["W/D", "WD"]:
                    player_finish = 98
                elif player_finish_str in ["NAN", "-", "N/A"]:
                    player_finish = 97 
                elif player_finish_str in ["DQ"]:
                    player_finish = 96
                else:  
                    try:
                        # Remove any non-numeric characters except for 'T' (tied)
                        cleaned_finish = ''.join(c for c in player_finish_str if c.isdigit() or c == 'T')
                        cleaned_finish = cleaned_finish.replace("T", "")
                        player_finish = int(cleaned_finish) if cleaned_finish else 95
                    except ValueError:
                        logger.warning(f"Could not parse finish '{player_finish_str}' for player {player_name}, using 95")
                        player_finish = 95
                
                # Process player score
                if player_score_str == "E" or player_score_str == "Even":
                    player_score = 0
                elif player_score_str in ["-", "N/A", ""]:
                    player_score = 99
                else:
                    try:
                        # Handle different score formats ("+3", "-5", etc.)
                        if player_score_str.startswith("+"):
                            player_score = int(player_score_str[1:])
                        elif player_score_str.startswith("-"):
                            player_score = -int(player_score_str[1:])
                        else:
                            player_score = int(player_score_str)
                    except ValueError:
                        logger.warning(f"Could not convert score '{player_score_str}' to integer for player {player_name}")
                        player_score = 99
                
                # Try to get player ID from database if db is provided
                player_id = None
                if db:
                    player_obj = db.query(Player).filter(Player.name == player_name).first()
                    if player_obj:
                        player_id = player_obj.id
                
                # Create result dictionary
                result_dict = {
                    "year": year,
                    "tournament_id": tournament_id,
                    "tournament_name": tournament_name,
                    "course_name": course_name,
                    "player_id": player_id,
                    "player_name": player_name,
                    "finish": player_finish,
                    "score": player_score
                }
                
                output_list.append(result_dict)
                
            except StaleElementReferenceException:
                logger.warning("Stale element reference, page probably changed during processing")
                continue
            except NoSuchElementException as e:
                logger.error(f"Could not find element for player in tournament {tournament_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing player in tournament {tournament_name}: {e}")
                continue
        
        logger.info(f"Scraped {len(output_list)} player results for tournament: {tournament_name}")
        return output_list
        
    except WebDriverException as e:
        logger.error(f"WebDriver error in get_tournament_results for {tournament_name}: {e}")
        raise  # Re-raise to handle in the main function
    except Exception as e:
        logger.error(f"Error getting tournament results for {tournament_name}: {e}")
        return []

def add_to_master_table(db, master_data):
    """
    Add data to the master table.
    
    Args:
        db: Database session
        master_data: List of dictionaries containing master data
    """
    try:
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(master_data)
        
        # Add each record to the master table
        records_added = 0
        records_updated = 0
        
        for _, row in df.iterrows():
            try:
                # Check if record already exists
                existing_record = db.query(Master).filter(
                    Master.year == row['year'],
                    Master.tournament_id == row['tournament_id'],
                    Master.player_name == row['player_name']
                ).first()
                
                if existing_record:
                    # Update existing record
                    existing_record.finish = row['finish']
                    existing_record.score = row['score']
                    records_updated += 1
                else:
                    # Create new record
                    master_record = Master(
                        year=row['year'],
                        tournament_id=row['tournament_id'],
                        tournament_name=row['tournament_name'],
                        course_name=row['course_name'],
                        player_id=row['player_id'],
                        player_name=row['player_name'],
                        finish=row['finish'],
                        score=row['score']
                    )
                    db.add(master_record)
                    records_added += 1
            except Exception as e:
                logger.error(f"Error adding/updating record for {row['player_name']} in {row['tournament_name']}: {e}")
                continue
                
        # Commit changes to database
        db.commit()
        logger.info(f"Successfully added {records_added} and updated {records_updated} records in master table")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding data to master table: {e}")
        raise
    
def get_upcoming_tournament_players(driver, db, tournament_name, tournament_id, year=CURRENT_YEAR, course_name=None):
    """
    Get players list for an upcoming tournament that hasn't happened yet.
    
    Args:
        driver: Selenium WebDriver instance
        db: Database session
        tournament_name: Name of the tournament
        tournament_id: ID of the tournament
        year: Year of the tournament (default: current year)
        course_name: Name of the course (optional)
        
    Returns:
        List of dictionaries containing player information for upcoming tournament
    """
    try:
        # Format tournament name for URL (replace spaces with dashes and remove special characters)
        dashed_tournament_name = "-".join(
            "".join(c if c.isalnum() or c.isspace() else ' ' for c in tournament_name.lower()).split()
        )
        
        # Construct URL
        url = f"https://www.pgatour.com/tournaments/{year}/{dashed_tournament_name}/{tournament_id}/field"
        
        logger.info(f"Navigating to tournament field page: {url}...")
        driver.get(url)
        
        # Wait for page to load with explicit wait
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "tr.css-79elbk, .tournament-field, table.field-table"))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for field data for {tournament_name}. Trying alternative selector...")
            try:
                # Try alternative selector
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".players-list, .field-list"))
                )
            except TimeoutException:
                logger.warning(f"No player field found for tournament: {tournament_name}. URL structure may have changed.")
                return []
        
        output_list = []
        
        # Try multiple CSS selectors for player rows to handle different page structures
        row_selectors = [
            "tr.css-79elbk",               # New format from example
            "tr[class*='css-79elbk']",     # Partial class match
            "tr.player-row",               # Generic player row class
            ".tournament-field tr",        # Any rows in tournament field
            ".field-table tbody tr"        # Any rows in field table
        ]
        
        rows = []
        for selector in row_selectors:
            rows = driver.find_elements(By.CSS_SELECTOR, selector)
            if rows:
                logger.info(f"Found {len(rows)} player rows using selector: {selector}")
                break
        
        if not rows:
            logger.warning(f"No player rows found for tournament: {tournament_name}")
            return []
        
        # Try multiple selector combinations for player names
        # The new format has names in "Last, First" format in the span with class css-hmig5c
        name_selectors = [
            ".css-hmig5c",                  # Class from example
            "span.chakra-text.css-hmig5c",  # Full path
            "a.css-1jfg7sy span.css-hmig5c", # Player link with name span
            ".player-name",                 # Generic player name class
            "td a div div div span"         # Deep path navigation
        ]
        
        for row in rows:
            try:
                # Find player name using multiple selectors
                player_name_raw = None
                for selector in name_selectors:
                    try:
                        name_element = row.find_element(By.CSS_SELECTOR, selector)
                        player_name_raw = name_element.text.strip()
                        if player_name_raw:
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
                
                if not player_name_raw:
                    logger.warning("Could not find player name, skipping row")
                    continue
                
                # Process the player name from "Last, First" to "First Last"
                if "," in player_name_raw:
                    parts = player_name_raw.split(",")
                    if len(parts) == 2:
                        last_name = parts[0].strip()
                        first_name = parts[1].strip()
                        player_name = f"{first_name} {last_name}"
                    else:
                        logger.warning(f"Unexpected name format: {player_name_raw}")
                        player_name = player_name_raw
                else:
                    # If it's not in "Last, First" format, use as is
                    player_name = player_name_raw
                
                logger.info(f"Found player: {player_name} (original: {player_name_raw})")
                
                # Try to get player ID from database
                player_id = None
                player_obj = db.query(Player).filter(Player.name == player_name).first()
                if player_obj:
                    player_id = player_obj.id
                
                # Create result dictionary
                result_dict = {
                    "year": year,
                    "tournament_id": tournament_id,
                    "tournament_name": tournament_name,
                    "course_name": course_name,
                    "player_id": player_id,
                    "player_name": player_name,
                    "finish": None,  # No finish for upcoming tournament
                    "score": None    # No score for upcoming tournament
                }
                
                output_list.append(result_dict)
                
            except StaleElementReferenceException:
                logger.warning("Stale element reference, page probably changed during processing")
                continue
            except NoSuchElementException as e:
                logger.error(f"Could not find element for player in tournament {tournament_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing player in tournament {tournament_name}: {e}")
                continue
        
        logger.info(f"Scraped {len(output_list)} players for upcoming tournament: {tournament_name}")
        return output_list
        
    except WebDriverException as e:
        logger.error(f"WebDriver error in get_upcoming_tournament_players for {tournament_name}: {e}")
        raise  # Re-raise to handle in the main function
    except Exception as e:
        logger.error(f"Error getting players for tournament {tournament_name}: {e}")
        return []

def scrape_single_tournament(tournament_name, year, db: Session = None):
    """
    Scrape data for a single tournament and add players to the master table.
    This function is specifically for adding upcoming tournaments where players
    may not have finishes or scores yet.
    
    Args:
        tournament_name: Name of the tournament to scrape
        year: Year of the tournament
        db: Database session (optional, will create one if not provided)
        
    Returns:
        Dictionary with status and message
    """
    driver = None
    close_db = False
    
    try:
        # Initialize database session if not provided
        if db is None:
            from app.db.db_setup import SessionLocal
            db = SessionLocal()
            close_db = True
        
        # Get tournament from database
        tournament = db.query(Tournament).filter(
            Tournament.tournament_name == tournament_name
        ).first()
        
        if not tournament:
            logger.error(f"Tournament {tournament_name} not found in database")
            return {"status": "error", "message": f"Tournament {tournament_name} not found in database"}
        
        tournament_id = tournament.tournament_id
        course_name = tournament.course_name
        
        logger.info(f"Found tournament: {tournament_name}, ID: {tournament_id}, Course: {course_name}")
        
        # Initialize Selenium driver
        logger.info("Initializing Selenium driver...")
        driver = get_driver()
        
        # Get tournament players (use the new function for upcoming tournaments)
        player_results = get_upcoming_tournament_players(
            driver=driver,
            db=db,
            tournament_name=tournament_name,
            tournament_id=tournament_id,
            year=year,
            course_name=course_name
        )
        
        if not player_results:
            logger.warning(f"No players found for tournament {tournament_name} ({year})")
            return {"status": "warning", "message": f"No players found for tournament {tournament_name} ({year})"}
        
        logger.info(f"Found {len(player_results)} players for tournament {tournament_name} ({year})")
        
        # Add players to master table
        players_added = 0
        for player_data in player_results:
            # Check if this specific player record already exists for this tournament + year
            existing_player_record = db.query(Master).filter(
                Master.tournament_name == tournament_name,
                Master.year == year,
                Master.player_name == player_data['player_name']
            ).first()
            
            if existing_player_record:
                # Skip this player if already added
                logger.info(f"Player {player_data['player_name']} already exists for {tournament_name} ({year})")
                continue
            
            # Create new master record
            new_master = Master(
                year=year,
                tournament_id=tournament_id,
                tournament_name=tournament_name,
                course_name=course_name or "NAN",
                player_id=player_data['player_id'],
                player_name=player_data['player_name'],
                finish=None,  # No finish for upcoming tournaments
                score=None,   # No score for upcoming tournaments
                sg_total=None,  # Set to None initially
                sg_ttg=None,    # Set to None initially
                sg_ott=None,    # Set to None initially
                sg_apr=None,    # Set to None initially
                sg_atg=None,    # Set to None initially
                sg_putt=None,   # Set to None initially
                odds=None       # Set to None initially
            )
            
            db.add(new_master)
            players_added += 1
        
        db.commit()
        logger.info(f"Added {players_added} players to master table for {tournament_name} ({year})")
        
        return {
            "status": "success",
            "message": f"Added {players_added} players to master table for {tournament_name} ({year})"
        }
        
    except Exception as e:
        logger.error(f"Error scraping tournament {tournament_name} ({year}): {e}")
        logger.error(traceback.format_exc())
        return {"status": "error", "message": f"Error: {str(e)}"}
    
    finally:
        # Ensure the driver is closed even if errors occur
        if driver:
            try:
                logger.info("Closing Selenium driver...")
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing Selenium driver: {e}")
        
        # Close the database session if we created it
        if close_db and db:
            db.close()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the scraper
    result = scrape_master_data()
    print(result)
def scrape_tournament_results(tournament_name, tournament_id, year, course_name):
    """
    Scrape tournament results for a specific tournament and return the data.
    This function handles all the web scraping logic for tournament results.
    
    Parameters:
    - tournament_name: Name of the tournament
    - tournament_id: ID of the tournament
    - year: Year of the tournament
    - course_name: Name of the course
    
    Returns:
    - List of dictionaries containing player results
    """
    driver = None
    try:
        # Initialize the Selenium driver
        driver = get_driver()
        
        # Get tournament results using the existing function
        player_finishes = get_tournament_results(
            driver=driver,
            db=None,  # We don't need the db here as we're just scraping
            tournament_name=tournament_name,
            tournament_id=tournament_id,
            year=year,
            course_name=course_name
        )
        
        return player_finishes
    
    except Exception as e:
        logger.error(f"Error scraping tournament results for {tournament_name} ({year}): {e}")
        return []
    
    finally:
        # Ensure the driver is closed even if errors occur
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing Selenium driver: {e}")
    print(result)