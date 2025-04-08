
import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging

# Configure logging
logger = logging.getLogger("pga_betting_model.selenium_setup")

CURRENT_YEAR = dt.datetime.today().year

def get_driver():
    """
    Create and return a Chrome WebDriver with appropriate settings.
    Includes better error handling and logging.
    """
    try:
        logger.info("Setting up Chrome WebDriver...")
        options = Options()
        # Define the path to the manually downloaded chromedriver
        driver_path = r"C:/Users/Sleepycornbread/Python Projects/Portfolio Projects/PGA Betting Model/drivers/chromedriver.exe"
        service = Service(executable_path=driver_path)
        
        # Enable headless mode for better performance and less resource usage
        # Uncommenting headless mode for debugging
        # options.add_argument('--headless=new')  # Using the new headless mode
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Increase timeouts for better stability
        options.add_argument('--page-load-timeout=90')
        
        driver = webdriver.Chrome(options=options, service=service)
        driver.set_page_load_timeout(90)  # 90-second timeout
        
        # Test that driver is working properly
        driver.get("https://www.google.com")
        logger.info("Chrome WebDriver initialized successfully")
        
        return driver
        
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        raise