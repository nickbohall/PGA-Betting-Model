import datetime as dt
import pandas as pd
import time
from icecream import ic

# Selenium Imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Local Imports
from app.services.selenium_setup import get_driver, CURRENT_YEAR

pd.set_option('display.max_columns', None)


from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from fastapi import HTTPException

def get_player_info():
    
    driver = None # Initialize driver to None
    try:
        # Check if we have players in the database already
        # If we do, return them instead of scraping
        # This is a temporary solution until we can fix the scraping issue
        from app.db.db_setup import SessionLocal
        from app.models.player import Player
        
        print("Checking for existing players in database...")
        db = SessionLocal()
        
        try:
            existing_players = db.query(Player).all()
            if existing_players:
                print(f"Found {len(existing_players)} existing players in database, but will scrape for new players anyway.")
            else:
                print("No existing players found in database. Attempting to scrape...")
        finally:
            db.close()
        
        # If no existing players, try to scrape
        print("Initializing Selenium driver...")
        driver = get_driver()
        if not driver:
             print("Failed to get Selenium driver.")
             raise HTTPException(status_code=503, detail="Could not initialize web driver for scraping.")

        url = 'https://www.pgatour.com/players' # Setting the players url
        print(f"Navigating to {url}...")
        driver.get(url) # Initializing the driver on the url - This opens the page
        
        # Check for 403 error or access denied in the page source
        if "403 ERROR" in driver.page_source or "Request blocked" in driver.page_source:
            print("Access to PGA Tour website is blocked (403 Forbidden).")
            raise HTTPException(
                status_code=403,
                detail="Access to PGA Tour website is blocked. The website may be blocking automated access. Please try again later."
            )
        
        # Use WebDriverWait instead of time.sleep for more reliable waiting
        wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds
        try:
            print("Waiting for player elements to load...")
            # Wait for the players container to be present
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-1vdhhui')))
            print("Player elements loaded successfully.")
        except TimeoutException as e:
            print(f"Timed out waiting for player elements to load: {e}")
            # Let's try to get the page source to see what's actually there
            page_source = driver.page_source
            print(f"Page source snippet: {page_source[:500]}...")
            
            # Check if the page source indicates a 403 error
            if "403 ERROR" in page_source or "Request blocked" in page_source:
                raise HTTPException(
                    status_code=403,
                    detail="Access to PGA Tour website is blocked. The website may be blocking automated access. Please try again later."
                )
            
            raise HTTPException(status_code=504, detail=f"Timed out waiting for PGA Tour website to load player data: {e}")

        player_list = [] # Create empty player list

        # Implement scrolling to load all players - first scroll to bottom, then scrape
        print("Scrolling to the bottom of the page to load all players...")
        
        try:
            # First, scroll to the bottom of the page
            max_scroll_attempts = 30  # Limit scrolling attempts to prevent infinite loops
            scroll_attempts = 0
            last_height = 0
            found_z_player = False
            
            # Function to check if we've reached the bottom by looking for a player with last name Z
            def check_for_z_player():
                players = driver.find_elements(By.CSS_SELECTOR, 'div.css-1vdhhui')
                for player in players:
                    try:
                        player_info = player.find_element(By.CSS_SELECTOR, 'span.css-rdwj84 a')
                        player_name = player_info.get_attribute('aria-label')
                        if player_name and player_name.strip().split()[-1].startswith('Z'):
                            print(f"Found player with last name starting with Z: {player_name}")
                            return True
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
                return False
            
            print("Starting initial scroll to bottom...")
            while scroll_attempts < max_scroll_attempts:
                # Get current scroll height
                current_height = driver.execute_script("return document.body.scrollHeight")
                
                # If we haven't moved since last scroll, we might be at the bottom
                if current_height == last_height and scroll_attempts > 0:
                    print("Scroll height hasn't changed - checking if we've reached the bottom...")
                    
                    # Check if we can find a player with last name Z as verification
                    found_z_player = check_for_z_player()
                    if found_z_player:
                        print("Confirmed we've reached the bottom (found player with last name Z)")
                        break
                    
                    # If we can't find a Z player but height hasn't changed, wait and try one more scroll
                    print("No Z player found yet, waiting longer for content to load...")
                    time.sleep(5)  # Extended wait
                    
                    # Try one more aggressive scroll
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    
                    # Check again for Z player
                    found_z_player = check_for_z_player()
                    if found_z_player:
                        print("Found Z player after additional wait")
                        break
                    else:
                        # If still no Z player but we've scrolled multiple times with no height change
                        # we're probably at the bottom
                        print("Reached apparent bottom of page after multiple scroll attempts")
                        break
                
                # Update last height
                last_height = current_height
                
                # Scroll down to the bottom of the page
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"Scrolled to bottom (attempt {scroll_attempts+1}/{max_scroll_attempts})")
                
                # Wait for page to load new content
                time.sleep(3)  # Wait for content to load
                
                # Count current players for logging
                current_player_count = len(driver.find_elements(By.CSS_SELECTOR, 'div.css-1vdhhui'))
                print(f"Currently loaded {current_player_count} players")
                
                scroll_attempts += 1
            
            # After reaching the bottom, wait a bit longer to ensure all content is fully loaded
            print("Reached the bottom of the page, waiting for all content to finish loading...")
            time.sleep(5)
            
            # Final check for Z player if we haven't found one yet
            if not found_z_player:
                found_z_player = check_for_z_player()
                if found_z_player:
                    print("Found Z player in final check")
                else:
                    print("Warning: Could not find a player with last name Z - may not have scrolled completely")
        
        except Exception as e:
            print(f"Error during scrolling: {e}")
            # Continue with whatever players we've loaded so far
        
        # After scrolling to the bottom, get the final list of players
        print("Finding all player elements after scrolling to bottom...")
        
        # Wait for the final player list to be fully loaded
        try:
            # Use an explicit wait to ensure all player elements are loaded
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-1vdhhui')))
        except TimeoutException:
            print("Timeout waiting for final player list to load. Proceeding with whatever is available.")
        
        # Get all player elements
        players = driver.find_elements(By.CSS_SELECTOR, 'div.css-1vdhhui')
        print(f"Final player count: {len(players)}")

        if not players:
            print("No player elements found on the page. Website structure might have changed.")
            # Let's try to get the page source to see what's actually there
            page_source = driver.page_source
            print(f"Page source snippet: {page_source[:500]}...")
            
            # Let's try an alternative selector
            print("Trying alternative selectors...")
            # Try a more general selector to see what elements are available
            all_divs = driver.find_elements(By.TAG_NAME, 'div')
            print(f"Found {len(all_divs)} div elements on the page")
            
            # Return empty list or raise error depending on desired behavior
            raise HTTPException(status_code=500, detail="No player elements found. Website structure might have changed.")

        for player in players:
            try:
                player_info = player.find_element(By.CSS_SELECTOR, 'span.css-rdwj84 a') # This contains name & href
                player_name = player_info.get_attribute('aria-label') # Grabbing just the name
                player_link = player_info.get_attribute('href') # Grabbing the href
                
                # Basic check for valid link before splitting
                if player_link and "/" in player_link:
                    player_id = player_link.split("/")[-2] # Parsing the href for the player_id
                else:
                    print(f"Warning: Could not parse player ID from link: {player_link} for player element.")
                    continue # Skip this player if link is invalid

                player_nationality = player.find_element(By.CSS_SELECTOR, 'span.css-rbcrqz p').text
                
                # Okay lets put all the player info into a dict and then add to the player list to return
                player_dict = {"id": player_id, "name": player_name, "nationality": player_nationality}
                player_list.append(player_dict)

            except NoSuchElementException as e:
                print(f"Warning: Could not find element for a player: {e}. Skipping player.")
                # Log the specific player element if possible to help debug
                continue # Skip this player if details can't be found
            except Exception as e:
                print(f"Warning: An unexpected error occurred processing a player: {e}. Skipping player.")
                continue # Skip this player on other unexpected errors

        print(f"Scrape successful! {len(player_list)} players scraped. Attempting to add to db!")
        return player_list

    except (TimeoutException, ConnectionError) as e:
        print(f"Error connecting to or loading {url}: {e}")
        # Raise an HTTPException so the API endpoint can return a proper error
        raise HTTPException(status_code=504, detail=f"Could not connect to PGA Tour website: {e}")
    except Exception as e:
        # Catch any other unexpected errors during setup or scraping
        import traceback
        traceback_str = traceback.format_exc()
        print(f"An unexpected error occurred during player scraping: {e}")
        print(f"Traceback: {traceback_str}")
        raise HTTPException(status_code=500, detail=f"Internal scraping error: {e}. Traceback: {traceback_str}")
    finally:
        # Ensure the driver is closed even if errors occur
        if driver:
            print("Closing Selenium driver...")
            driver.quit()