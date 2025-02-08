import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import logging
import os
from config import (
    MIN_WAIT, MAX_WAIT, CHROME_OPTIONS, BROWSER_SETTINGS,
    USER_AGENT
)

class BrowserManager:
    def __init__(self):
        self.driver = None
        self.wait = None

    def init_browser(self):
        """Initialize Chrome browser with undetected-chromedriver"""
        try:
            logging.info("Setting up Chrome options...")
            options = uc.ChromeOptions()

            # Basic Chrome arguments
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--headless=new')
            options.add_argument(f'user-agent={USER_AGENT}')

            # Add experimental options
            prefs = CHROME_OPTIONS.copy()
            options.add_experimental_option("prefs", prefs)

            # Initialize Chrome with simplified configuration
            logging.info("Initializing Chrome driver...")
            self.driver = uc.Chrome(
                options=options,
                headless=True,
                use_subprocess=True
            )

            # Configure timeouts
            self.driver.set_page_load_timeout(BROWSER_SETTINGS['PAGE_LOAD_TIMEOUT'])
            self.driver.implicitly_wait(BROWSER_SETTINGS['IMPLICIT_WAIT'])
            self.wait = WebDriverWait(self.driver, BROWSER_SETTINGS['EXPLICIT_WAIT'])

            logging.info("Chrome driver initialized successfully")
            return self.driver

        except Exception as e:
            logging.error(f"Browser initialization failed: {str(e)}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            raise

    def wait_random(self):
        """Wait for a random time between MIN_WAIT and MAX_WAIT seconds"""
        time.sleep(random.randint(MIN_WAIT, MAX_WAIT))

    def find_element_with_retry(self, by, value, retries=3, timeout=None):
        """Find element with retry mechanism"""
        if not timeout:
            timeout = BROWSER_SETTINGS['EXPLICIT_WAIT']

        for attempt in range(retries):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except Exception as e:
                if attempt == retries - 1:
                    raise
                logging.warning(f"Retry {attempt + 1}/{retries} finding element {value}")
                time.sleep(BROWSER_SETTINGS['RETRY_DELAY'])

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")