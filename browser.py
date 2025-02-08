import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
            options = uc.ChromeOptions()

            # Add required Chrome arguments
            options.add_argument('--no-sandbox')
            options.add_argument('--headless=new')  # Use new headless mode
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')  # Disable GPU usage
            options.add_argument('--disable-extensions')  # Disable extensions
            options.add_argument('--window-size=1920,1080')  # Set window size
            options.add_argument('--start-maximized')  # Start maximized
            options.add_argument(f'user-agent={USER_AGENT}')
            options.add_argument('--disable-infobars')
            options.add_argument('--lang=en-US')
            options.add_argument('--disable-blink-features=AutomationControlled')

            # Add experimental options for preferences
            prefs = CHROME_OPTIONS.copy()
            prefs.update({
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_settings.popups": 0
            })
            options.add_experimental_option("prefs", prefs)

            # Set binary location if available
            chrome_binary = os.environ.get('CHROME_BINARY_PATH')
            if chrome_binary and os.path.exists(chrome_binary):
                logging.info(f"Using Chrome binary at: {chrome_binary}")
                options.binary_location = chrome_binary
            else:
                logging.warning("CHROME_BINARY_PATH not set or invalid, using default Chrome location")

            logging.info("Initializing Chrome driver with configured options...")
            self.driver = uc.Chrome(options=options)

            # Set page load timeout
            self.driver.set_page_load_timeout(BROWSER_SETTINGS['PAGE_LOAD_TIMEOUT'])
            self.driver.implicitly_wait(BROWSER_SETTINGS['IMPLICIT_WAIT'])

            # Initialize wait with longer timeout
            self.wait = WebDriverWait(self.driver, BROWSER_SETTINGS['EXPLICIT_WAIT'])

            logging.info("Chrome driver initialized successfully")
            return self.driver

        except Exception as e:
            logging.error(f"Failed to initialize browser: {str(e)}")
            raise

    def wait_random(self):
        """Wait for a random time between MIN_WAIT and MAX_WAIT seconds"""
        time.sleep(random.randint(MIN_WAIT, MAX_WAIT))

    def find_element_with_retry(self, by, value, retries=3, timeout=None):
        """Find element with retry mechanism and dynamic timeout"""
        if timeout is None:
            timeout = BROWSER_SETTINGS['EXPLICIT_WAIT']

        for attempt in range(retries):
            try:
                # Try to find element with explicit wait
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )

                # Additional check for element interactability
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by, value))
                )

                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

                # Small delay before returning element
                time.sleep(BROWSER_SETTINGS['RETRY_DELAY'])
                return element

            except TimeoutException:
                if attempt == retries - 1:
                    raise
                logging.warning(f"Retry {attempt + 1} finding element {value}")
                time.sleep(BROWSER_SETTINGS['RETRY_DELAY'])
            except Exception as e:
                if attempt == retries - 1:
                    raise
                logging.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                time.sleep(BROWSER_SETTINGS['RETRY_DELAY'])

    def close(self):
        """Close browser and clean up"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")