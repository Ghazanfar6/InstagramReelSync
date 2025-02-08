import time
import os
import logging
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import base64

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
        if not self.setup_browser():
            raise Exception("Failed to initialize browser")

    def setup_browser(self):
        """Initialize undetected Chrome browser"""
        try:
            logger.info("Setting up Chrome browser...")

            # Create downloads directory
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)

            # Basic Chrome options
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')

            # Add experimental options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Initialize Chrome
            logger.info("Initializing Chrome...")
            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=None,
                browser_executable_path=None,
                version_main=121
            )

            # Set up WebDriverWait with increased timeout
            self.wait = WebDriverWait(self.driver, 45)
            logger.info("Browser setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}")
            if self.driver:
                self.driver.quit()
            return False

    def login(self):
        """Login to Instagram"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(random.randint(MIN_WAIT, MAX_WAIT))

            # Wait for and fill login fields
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

            password_field.submit()

            # Wait for successful login
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
            )
            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def scrape_reel(self):
        """Scrape a reel from Instagram reels page"""
        try:
            logger.info("Navigating to reels page")
            self.driver.get("https://www.instagram.com/reels/")
            time.sleep(random.randint(MIN_WAIT, MAX_WAIT))

            logger.info("🔍 Searching for a reel...")

            try:
                # Click on the first reel in the feed
                first_reel = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button']"))
                )
                first_reel.click()
                time.sleep(random.randint(MIN_WAIT, MAX_WAIT))

                # Wait for URL to change
                new_url = self.driver.current_url
                logger.info(f"🔗 Reel URL: {new_url}")

                # Extract video element
                video_element = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
                video_url = video_element.get_attribute("src")

                if "blob:" in video_url:
                    logger.info("⚠ Blob URL detected, extracting video data...")

                    # Extract the actual video data from the blob URL
                    video_data = self.driver.execute_script("""
                        let video = document.querySelector('video');
                        let canvas = document.createElement('canvas');
                        let ctx = canvas.getContext('2d');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        return canvas.toDataURL('image/png');
                    """)

                    # Convert Base64 to binary
                    video_binary = base64.b64decode(video_data.split(',')[1])

                    filename = os.path.join(DOWNLOAD_DIR, f"reel_{int(time.time())}.mp4")
                    with open(filename, "wb") as file:
                        file.write(video_binary)

                    logger.info(f"✅ Successfully downloaded: {filename}")
                    return filename

                else:
                    logger.info("📥 Downloading video from direct URL...")
                    filename = os.path.join(DOWNLOAD_DIR, f"reel_{int(time.time())}.mp4")
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "*/*",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Referer": "https://www.instagram.com/"
                    }

                    response = requests.get(video_url, headers=headers, stream=True)
                    response.raise_for_status()

                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                    logger.info(f"✅ Successfully downloaded: {filename}")
                    return filename

            except Exception as e:
                logger.error(f"Failed to extract video: {str(e)}")
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