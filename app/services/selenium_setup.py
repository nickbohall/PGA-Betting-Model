# Selenium Imports
import datetime as dt

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

CURRENT_YEAR = dt.datetime.today().year

def get_driver():
    options = Options()
    service = Service(ChromeDriverManager().install()) # This installs the latest ChromeDriver on use
    # options.add_argument('--headless')  # Set to True to not open the webpage
    options.add_argument('--ignore-certificate-errors') # Ignores a random error oops
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options, service=service) # setup the driver when the class is initiated

    return driver