import time
import base64
import os
from selenium.webdriver.common.by import By
from browser import BrowserManager
from config import USERNAME, PASSWORD, LOGIN_URL, REELS_URL, DOWNLOAD_DIR, MAX_RETRIES
from utils import logger

class ReelScraper:
    def __init__(self):
        self.browser = BrowserManager()
        self.driver = None

    def login(self):
        """Log into Instagram"""
        try:
            logger.info("Initializing browser for scraping...")
            self.driver = self.browser.init_browser()
            self.driver.get(LOGIN_URL)
            self.browser.wait_random()

            username_field = self.browser.find_element_with_retry(By.NAME, "username")
            password_field = self.browser.find_element_with_retry(By.NAME, "password")

            username_field.send_keys(USERNAME)
            password_field.send_keys(PASSWORD)
            password_field.submit()

            self.browser.wait_random()
            logger.info("Login attempt completed")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def download_reel(self):
        """Download a reel from the feed"""
        try:
            logger.info("Navigating to reels page...")
            self.driver.get(REELS_URL)
            self.browser.wait_random()

            first_reel = self.browser.find_element_with_retry(
                By.XPATH, "//div[@role='button']",
                retries=3,
                timeout=10
            )
            first_reel.click()
            self.browser.wait_random()

            video_element = self.browser.find_element_with_retry(
                By.TAG_NAME, "video",
                retries=3,
                timeout=10
            )
            video_url = video_element.get_attribute("src")

            if "blob:" in video_url:
                logger.info("Extracting video data from blob URL...")
                video_data = self.driver.execute_script("""
                    let video = document.querySelector('video');
                    let canvas = document.createElement('canvas');
                    let ctx = canvas.getContext('2d');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    return canvas.toDataURL('image/png');
                """)

                video_binary = base64.b64decode(video_data.split(',')[1])
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                filename = os.path.join(DOWNLOAD_DIR, f"reel_{int(time.time())}.mp4")

                with open(filename, "wb") as file:
                    file.write(video_binary)

                logger.info(f"Successfully downloaded: {filename}")
                return filename

            logger.error("Could not extract video data")
            return None

        except Exception as e:
            logger.error(f"Failed to download reel: {str(e)}")
            return None

    def close(self):
        """Clean up resources"""
        self.browser.close()

def scrape_with_retry():
    """Scrape with retry mechanism"""
    scraper = ReelScraper()

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Scrape attempt {attempt + 1}/{MAX_RETRIES}")
            if scraper.login():
                result = scraper.download_reel()
                if result:
                    return result
        except Exception as e:
            logger.error(f"Scrape attempt {attempt + 1} failed: {str(e)}")
        finally:
            scraper.close()

        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    return None

if __name__ == "__main__":
    scrape_with_retry()