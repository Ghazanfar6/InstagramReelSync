import time
import os
import logging
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

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
        """Initialize undetected Chrome browser"""
        try:
            options = uc.ChromeOptions()

            # Basic Chrome options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')

            # Experimental options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Download preferences
            options.add_experimental_option("prefs", {
                "download.default_directory": os.path.abspath(DOWNLOAD_DIR),
                "download.prompt_for_download": False,
                "safebrowsing.enabled": True
            })

            # Create downloads directory if it doesn't exist
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)

            # Initialize undetected Chrome
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            self.wait = WebDriverWait(self.driver, 30)

            logger.info("Browser initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            if self.driver:
                self.driver.quit()
            return False

    def login(self):
        """Log into Instagram with human-like behavior"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(random.randint(5, 10))

            # Find login fields with explicit wait
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )

            # Type credentials with random delays
            for char in INSTAGRAM_USERNAME:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))

            for char in INSTAGRAM_PASSWORD:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))

            time.sleep(random.randint(2, 4))
            password_field.submit()

            # Wait for successful login
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
            )

            time.sleep(random.randint(5, 10))
            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def scrape_reel(self):
        """Scrape a reel from Instagram reels page"""
        try:
            logger.info("Navigating to reels page")
            self.driver.get('https://www.instagram.com/reels/')
            time.sleep(random.randint(5, 10))

            logger.info("Waiting for reels to load...")

            # Wait for reels container
            reels_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main[role='main']"))
            )

            # Find clickable reel elements
            reel_elements = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div[role='button'] a[role='link']")
                )
            )

            if not reel_elements:
                logger.error("No reel elements found")
                return None

            logger.info(f"Found {len(reel_elements)} reels")

            # Click the first reel
            reel_elements[0].click()
            time.sleep(random.randint(3, 5))

            # Wait for and get video element
            video_element = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )

            video_url = video_element.get_attribute("src")
            if not video_url:
                logger.error("Could not get video URL")
                return None

            logger.info(f"Found video URL: {video_url}")

            # Download the video
            filename = os.path.join(DOWNLOAD_DIR, f"reel_{int(time.time())}.mp4")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }

            response = requests.get(video_url, headers=headers, stream=True)
            response.raise_for_status()

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Successfully downloaded: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to scrape reel: {str(e)}")
            return None

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")

def scrape_with_retry():
    """Scrape with retry mechanism"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Scrape attempt {attempt + 1}/{MAX_RETRIES}")
            scraper = InstagramScraper()

            if scraper.login():
                result = scraper.scrape_reel()
                if result:
                    return result

        except Exception as e:
            logger.error(f"Scrape attempt {attempt + 1} failed: {str(e)}")
        finally:
            if 'scraper' in locals():
                scraper.close()

        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    return None

if __name__ == "__main__":
    scrape_with_retry()