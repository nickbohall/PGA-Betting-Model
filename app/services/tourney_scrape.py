import pandas as pd
import time
import logging
from icecream import ic
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
import re
from datetime import datetime, date

# Configure logging for this module
logger = logging.getLogger("pga_betting_model.tourney_scrape")

# Selenium Imports
from selenium.webdriver.common.by import By

# Local Imports
from app.services.selenium_setup import get_driver, CURRENT_YEAR
from urllib.parse import urlparse, parse_qs

pd.set_option('display.max_columns', None)

def parse_tournament_date(date_text, year):
    """
    Parse a tournament date string like 'JAN 2 - 5' or 'JAN 30 - FEB 2' 
    and return a proper datetime.date object for the first date.
    
    Args:
        date_text (str): The date text to parse
        year (int): The year to use
    
    Returns:
        date: A datetime.date object representing the start date of the tournament
    """
    # Try to extract the first date
    if " - " in date_text:
        # Format like "JAN 2 - 5" or "JAN 30 - FEB 2"
        first_part = date_text.split(" - ")[0].strip()
    elif "through" in date_text:
        # Format like "Date through Date"
        first_part = date_text.split("through")[0].strip()
    else:
        first_part = date_text.strip()
    
    # Define month mapping
    month_dict = {
        'JAN': 1, 'JANUARY': 1, 'Jan': 1, 'January': 1,
        'FEB': 2, 'FEBRUARY': 2, 'Feb': 2, 'February': 2,
        'MAR': 3, 'MARCH': 3, 'Mar': 3, 'March': 3,
        'APR': 4, 'APRIL': 4, 'Apr': 4, 'April': 4,
        'MAY': 5, 'May': 5,
        'JUN': 6, 'JUNE': 6, 'Jun': 6, 'June': 6,
        'JUL': 7, 'JULY': 7, 'Jul': 7, 'July': 7,
        'AUG': 8, 'AUGUST': 8, 'Aug': 8, 'August': 8,
        'SEP': 9, 'SEPTEMBER': 9, 'Sep': 9, 'September': 9,
        'OCT': 10, 'OCTOBER': 10, 'Oct': 10, 'October': 10,
        'NOV': 11, 'NOVEMBER': 11, 'Nov': 11, 'November': 11,
        'DEC': 12, 'DECEMBER': 12, 'Dec': 12, 'December': 12
    }
    
    # First try standard datetime formats
    standard_formats = [
        "%B %d, %Y",  # "January 1, 2025"
        "%B %d %Y",   # "January 1 2025"
        "%b %d, %Y",  # "Jan 1, 2025"
        "%b %d %Y"    # "Jan 1 2025"
    ]
    
    for fmt in standard_formats:
        try:
            return datetime.strptime(first_part, fmt).date()
        except ValueError:
            continue
    
    # If standard formats fail, try with regex
    # Pattern to match month name followed by day number
    pattern = r'([A-Za-z]+)\s+(\d+)'
    match = re.search(pattern, first_part)
    
    if match:
        month_name, day = match.groups()
        
        # Convert month name to uppercase for consistent lookup
        month_name_upper = month_name.upper()
        if month_name_upper in month_dict:
            month_num = month_dict[month_name_upper]
        elif month_name in month_dict:
            month_num = month_dict[month_name]
        else:
            # Try partial match
            for key in month_dict:
                if key.startswith(month_name_upper) or month_name_upper.startswith(key):
                    month_num = month_dict[key]
                    break
            else:
                logger.warning(f"Could not match month: {month_name}")
                return None
        
        day_num = int(day)
        
        # Create the date object
        try:
            return date(year, month_num, day_num)
        except ValueError as e:
            logger.error(f"ValueError creating date: {e}")
            return None
    
    # If we couldn't parse the date, return None
    return None

def get_tournament_data():
    driver = None
    try:
        # Check if we have tournaments in the database already
        # If we do, return them instead of scraping
        # This is a temporary solution until we can fix the scraping issue
        from app.db.db_setup import SessionLocal
        from app.models.tournament import Tournament
        
        logger.info("Checking for existing tournaments in database...")
        db = SessionLocal()
        try:
            # Try to query tournaments, but handle the case where the tournament_date column doesn't exist yet
            try:
                existing_tournaments = db.query(Tournament).all()
                if existing_tournaments:
                    logger.info(f"Found {len(existing_tournaments)} existing tournaments in database. Using cached data.")
                    tournament_list = []
                    for tournament in existing_tournaments:
                        tournament_dict = {
                            "tournament_id": tournament.tournament_id,
                            "tournament_name": tournament.tournament_name,
                            "course_name": tournament.course_name,
                            "year": tournament.year,
                            "tournament_date": tournament.tournament_date
                        }
                        tournament_list.append(tournament_dict)
                    return tournament_list
            except Exception as column_error:
                # If there's an error about missing column, we'll need to scrape
                logger.error(f"Error querying tournaments: {column_error}")
                logger.info("This might be due to schema changes. Proceeding with scraping...")
                existing_tournaments = []
            
            logger.info("No existing tournaments found in database or error occurred. Attempting to scrape...")
        finally:
            db.close()
        
        # If no existing tournaments, try to scrape
        logger.info("Initializing Selenium driver...")
        driver = get_driver()
        if not driver:
            logger.error("Failed to get Selenium driver.")
            raise HTTPException(status_code=503, detail="Could not initialize web driver for scraping.")

        url = 'https://www.pgatour.com/schedule' # Setting the Schedule url
        logger.info(f"Navigating to {url}...")
        driver.get(url) # Initializing the driver on the url - This opens the page
        
        # Check for 403 error or access denied in the page source
        if "403 ERROR" in driver.page_source or "Request blocked" in driver.page_source:
            logger.error("Access to PGA Tour website is blocked (403 Forbidden).")
            raise HTTPException(
                status_code=403,
                detail="Access to PGA Tour website is blocked. The website may be blocking automated access. Please try again later."
            )
        
        logger.info("Waiting for page to load...")
        time.sleep(5) # Increased wait time for page to load
        
        # Change view from "Upcoming" to "Full Schedule"
        try:
            logger.info("Attempting to change view to 'Full Schedule'...")
            # Find and click the View button
            view_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="view"]')
            view_button.click()
            time.sleep(2)  # Increased wait time for dropdown to appear
            
            # Find and click the "Full Schedule" option in the dropdown
            # The dropdown menu items are typically loaded dynamically, so we need to find them after clicking
            menu_items = driver.find_elements(By.CSS_SELECTOR, '.chakra-menu__menu-list button')
            full_schedule_option = None
            
            for item in menu_items:
                if "Full Schedule" in item.text:
                    full_schedule_option = item
                    break
            
            if full_schedule_option:
                full_schedule_option.click()
                logger.info("Successfully changed view to 'Full Schedule'")
                time.sleep(5)  # Increased wait time for page to reload with full schedule
            else:
                logger.warning("Could not find 'Full Schedule' option in dropdown. Proceeding with default view.")
        except Exception as e:
            logger.warning(f"Failed to change view to 'Full Schedule': {e}. Proceeding with default view.")

        tournament_list = [] # Create empty tournament list

        # Find all tourneys on the page
        logger.info("Finding tournament elements...")
        tournament_objects = driver.find_elements(By.CSS_SELECTOR, 'div.css-1itfnhz') # Grabs tournament element
        
        if not tournament_objects:
            logger.error("No tournament elements found on the page. Website structure might have changed.")
            # Let's try to get the page source to see what's actually there
            page_source = driver.page_source
            logger.debug(f"Page source snippet: {page_source[:500]}...")
            
            # Check if the page source indicates a 403 error
            if "403 ERROR" in page_source or "Request blocked" in page_source:
                logger.error("Access to PGA Tour website is blocked (403 Forbidden).")
                raise HTTPException(
                    status_code=403,
                    detail="Access to PGA Tour website is blocked. The website may be blocking automated access. Please try again later."
                )
            
            raise HTTPException(
                status_code=500,
                detail="No tournament elements found. Website structure might have changed."
            )
        
        logger.info(f"Found {len(tournament_objects)} tournament elements.")
        for tournament in tournament_objects:
            try:
                tournament_name = (tournament.find_element(By.CSS_SELECTOR, 'p.css-vgdvwe').text).strip()
                
                # Extract tournament ID from link
                try:
                    # Try multiple CSS selectors for tournament links
                    tournament_link = None
                    link_selectors = [
                        'a.css-1jfg7sy',  # Original selector
                        'a[href*="/tournaments/"]',  # Any link containing /tournaments/
                        'a[href*="pgatour.com"]',    # Any PGA Tour link
                        'a'                          # Any link as fallback
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_element = tournament.find_element(By.CSS_SELECTOR, selector)
                            tournament_link = link_element.get_attribute('href')
                            if tournament_link:
                                logger.info(f"Found tournament link using selector: {selector}")
                                break
                        except NoSuchElementException:
                            continue
                    
                    if tournament_link:
                        # Better parsing of the tournament ID
                        parsed_url = urlparse(tournament_link)
                        path_segments = parsed_url.path.split('/')
                        
                        # Look for tournament ID in path segments
                        tournament_id = None
                        
                        # Try to find a segment that looks like a tournament ID
                        # Tournament IDs are typically alphanumeric strings
                        for segment in reversed(path_segments):  # Check from the end
                            segment = segment.split('?')[0].strip()
                            if segment and segment not in ['tournaments', 'schedule', 'pgatour.com']:
                                tournament_id = segment
                                break
                        
                        # If we still don't have an ID, use the tournament name as a fallback
                        if not tournament_id or tournament_id == "undefined":
                            # Create an ID from the tournament name
                            tournament_id = tournament_name.lower().replace(' ', '-')
                            logger.warning(f"Using tournament name as ID fallback: {tournament_id}")
                    else:
                        # If no link found, use tournament name as ID
                        tournament_id = tournament_name.lower().replace(' ', '-')
                        logger.warning(f"No tournament link found, using name as ID: {tournament_id}")
                except Exception as e:
                    logger.error(f"Error extracting tournament ID: {e}")
                    # Use tournament name as ID instead of "undefined"
                    tournament_id = tournament_name.lower().replace(' ', '-')
                    logger.warning(f"Using tournament name as ID after error: {tournament_id}")

                # Extract course name
                try:
                    course_name = tournament.find_element(By.CSS_SELECTOR, 'p.css-16dpohb').text
                except Exception as e:
                    logger.error(f"Error extracting course name: {e}")
                    course_name = "Course not found"
                
                # Extract tournament date and parse it to a proper date format
                try:
                    date_text = tournament.find_element(By.CSS_SELECTOR, 'p.css-mi4td0').text
                    
                    # Store the original date string as a backup
                    original_date_string = date_text.strip()
                    
                    # Use our custom parser to get a proper date object
                    parsed_date = parse_tournament_date(date_text, CURRENT_YEAR)
                    
                    if parsed_date:
                        # Format as YYYY-MM-DD string for database storage
                        tournament_date = parsed_date.strftime("%Y-%m-%d")
                        logger.info(f"Parsed tournament date '{original_date_string}' to {tournament_date}")
                    else:
                        logger.warning(f"Could not parse tournament date: '{original_date_string}'")
                        tournament_date = original_date_string
                        
                except Exception as e:
                    logger.error(f"Error extracting tournament date: {e}")
                    tournament_date = None

                # Create tournament dictionary with year and date
                tournament_dict = {
                    "tournament_id": tournament_id,
                    "tournament_name": tournament_name,
                    "course_name": course_name,
                    "year": CURRENT_YEAR,
                    "tournament_date": tournament_date
                }
                tournament_list.append(tournament_dict)
            except Exception as e:
                logger.error(f"Error processing tournament element: {e}")
                continue

        logger.info(f'Tournament list found! {len(tournament_list)} tournaments scraped.')
        return tournament_list
    
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        # Catch any other unexpected errors
        import traceback
        traceback_str = traceback.format_exc()
        logger.error(f"An unexpected error occurred during tournament scraping: {e}")
        logger.error(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=f"Internal scraping error: {e}. Traceback: {traceback_str}")
    finally:
        # Ensure the driver is closed even if errors occur
        if driver:
            logger.info("Closing Selenium driver...")
            driver.quit()