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

    def upload_reel(self, video_path):
        """Upload reel using browser automation"""
        try:
            # Login to Instagram
            self.driver.get("https://www.instagram.com/login")
            self.wait_random()
            
            # Find and fill login fields
            username_input = self.find_element_with_retry(By.NAME, "username")
            username_input.send_keys(os.environ.get("INSTAGRAM_USERNAME"))
            
            password_input = self.find_element_with_retry(By.NAME, "password")
            password_input.send_keys(os.environ.get("INSTAGRAM_PASSWORD"))
            
            # Click login button
            login_button = self.find_element_with_retry(By.XPATH, "//button[@type='submit']")
            login_button.click()
            self.wait_random()
            
            # Navigate to create reel page
            self.driver.get("https://www.instagram.com/create/reels")
            self.wait_random()
            
            # Upload video file
            file_input = self.find_element_with_retry(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(os.path.abspath(video_path))
            
            # Wait for upload to complete
            self.wait_random()
            
            # Click Next
            next_button = self.find_element_with_retry(By.XPATH, "//button[text()='Next']")
            next_button.click()
            self.wait_random()
            
            # Click Share
            share_button = self.find_element_with_retry(By.XPATH, "//button[text()='Share']")
            share_button.click()
            
            # Wait for confirmation
            self.wait_random()
            return True
            
        except Exception as e:
            logging.error(f"Browser upload failed: {str(e)}")
            return False

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")