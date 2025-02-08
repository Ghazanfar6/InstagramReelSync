import time
import os
import base64
from selenium.webdriver.common.by import By
from browser import BrowserManager
from config import USERNAME, PASSWORD, LOGIN_URL, REELS_URL, DOWNLOAD_DIR
from utils import logger

class ReelScraper:
    def __init__(self):
        self.browser = BrowserManager()
        self.driver = None

    def login(self):
        """Log into Instagram"""
        try:
            self.driver = self.browser.init_browser()
            self.driver.get(LOGIN_URL)
            self.browser.wait_random()

            # Enter credentials
            username_field = self.browser.find_element_with_retry(By.NAME, "username")
            password_field = self.browser.find_element_with_retry(By.NAME, "password")

            username_field.send_keys(USERNAME)
            password_field.send_keys(PASSWORD)
            password_field.submit()

            self.browser.wait_random()
            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def download_reel(self):
        """Download a reel from the feed"""
        try:
            self.driver.get(REELS_URL)
            self.browser.wait_random()

            logger.info("Searching for a reel...")
            first_reel = self.browser.find_element_with_retry(
                By.XPATH, "//div[@role='button']"
            )
            first_reel.click()
            self.browser.wait_random()

            video_element = self.browser.find_element_with_retry(By.TAG_NAME, "video")
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

                if not os.path.exists(DOWNLOAD_DIR):
                    os.makedirs(DOWNLOAD_DIR)

                filename = f"{DOWNLOAD_DIR}/reel_{int(time.time())}.mp4"
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

def scrape_with_retry(max_retries=3):
    """Scrape with retry mechanism"""
    scraper = ReelScraper()

    for attempt in range(max_retries):
        try:
            logger.info(f"Scrape attempt {attempt + 1}/{max_retries}")
            if scraper.login():
                result = scraper.download_reel()
                if result:
                    logger.info("Scraping completed successfully")
                    return result
        except Exception as e:
            logger.error(f"Scrape attempt {attempt + 1} failed: {str(e)}")
        finally:
            scraper.close()

        if attempt < max_retries - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    logger.error("All scrape attempts failed")
    return None

if __name__ == "__main__":
    scrape_with_retry()