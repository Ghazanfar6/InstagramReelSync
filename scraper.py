import time
import os
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    DOWNLOAD_DIR,
    MAX_RETRIES,
    MIN_WAIT,
    MAX_WAIT
)

logger = logging.getLogger(__name__)

class InstagramScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_browser()

    def setup_browser(self):
        """Initialize Chrome browser"""
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless=new')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("Browser initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            return False

    def wait_random(self):
        """Wait for a random time between MIN_WAIT and MAX_WAIT seconds"""
        time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))

    def login(self):
        """Log into Instagram"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.driver.get('https://www.instagram.com/accounts/login/')
            self.wait_random()

            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )

            username_field.clear()
            password_field.clear()

            username_field.send_keys(INSTAGRAM_USERNAME)
            self.wait_random()
            password_field.send_keys(INSTAGRAM_PASSWORD)
            self.wait_random()
            password_field.submit()

            # Wait for login to complete
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main[role='main']"))
            )
            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def scrape_reel(self):
        """Scrape a reel from the main reels page"""
        try:
            logger.info("Navigating to reels page")
            self.driver.get('https://www.instagram.com/reels/')
            self.wait_random()

            # Wait for and click first reel
            reel = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article a"))
            )
            reel.click()
            self.wait_random()

            # Wait for and get video source
            video = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            video_url = video.get_attribute("src")

            if video_url:
                filename = os.path.join(DOWNLOAD_DIR, f"reel_{int(time.time())}.mp4")
                response = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': video_url})

                with open(filename, 'wb') as f:
                    f.write(bytes(response['body']))

                logger.info(f"Successfully downloaded: {filename}")
                return filename

            logger.error("Failed to find video URL")
            return None

        except Exception as e:
            logger.error(f"Failed to scrape reel: {str(e)}")
            return None

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Failed to close browser: {str(e)}")

def scrape_with_retry():
    """Scrape with retry mechanism"""
    scraper = None

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Scrape attempt {attempt + 1}/{MAX_RETRIES}")
            scraper = InstagramScraper()

            if not scraper.setup_browser():
                continue

            if scraper.login():
                result = scraper.scrape_reel()
                if result:
                    return result

        except Exception as e:
            logger.error(f"Scrape attempt {attempt + 1} failed: {str(e)}")
        finally:
            if scraper:
                scraper.close()

        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    return None

if __name__ == "__main__":
    scrape_with_retry()