import time
import base64
import os
import logging
import random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import moviepy.editor as mp
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    DOWNLOAD_DIR,
    MAX_RETRIES,
    MIN_WAIT,
    MAX_WAIT,
    TARGET_ACCOUNTS
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BrowserManager:
    def __init__(self):
        self.driver = None

    def init_browser(self):
        """Initialize undetected-chromedriver"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless=new')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = uc.Chrome(options=options)
            return self.driver
        except Exception as e:
            logging.error(f"Failed to initialize browser: {str(e)}")
            return None

    def wait_random(self):
        """Wait for a random time between MIN_WAIT and MAX_WAIT seconds"""
        time.sleep(random.uniform(MIN_WAIT, MAX_WAIT))

    def find_element_with_retry(self, by, value, retries=3, timeout=10):
        """Find element with retry mechanism"""
        for _ in range(retries):
            try:
                return self.driver.find_element(by, value)
            except Exception as e:
                logging.warning(f"Failed to find element {value}: {str(e)}")
                time.sleep(timeout / retries)
        return None

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logging.error(f"Failed to close browser: {str(e)}")

class ReelScraper:
    def __init__(self):
        self.browser = BrowserManager()
        self.driver = None

    def login(self):
        """Log into Instagram"""
        try:
            logging.info("Initializing browser for scraping...")
            self.driver = self.browser.init_browser()
            self.driver.get('https://www.instagram.com/accounts/login/')
            self.browser.wait_random()

            username_field = self.browser.find_element_with_retry(By.NAME, "username")
            password_field = self.browser.find_element_with_retry(By.NAME, "password")

            if username_field and password_field:
                username_field.send_keys(INSTAGRAM_USERNAME)
                password_field.send_keys(INSTAGRAM_PASSWORD)
                password_field.submit()

                self.browser.wait_random()
                logging.info("Login attempt completed")
                return True
            return False

        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            return False

    def verify_video(self, file_path):
        """Verify if the downloaded file is a valid video"""
        try:
            if not os.path.exists(file_path):
                return False

            # Try to load the video
            video = mp.VideoFileClip(file_path)
            duration = video.duration
            video.close()

            # Check if video is too short or too long
            if duration < 1 or duration > 90:
                logging.error(f"Invalid video duration: {duration} seconds")
                return False

            logging.info(f"Video verified successfully: {duration} seconds")
            return True

        except Exception as e:
            logging.error(f"Video verification failed: {str(e)}")
            return False

    def download_reel_from_account(self, account):
        """Download a reel from a specific account"""
        try:
            logging.info(f"Navigating to account: {account}")
            self.driver.get(f'https://www.instagram.com/{account}/reels/')
            self.browser.wait_random()

            first_reel = self.browser.find_element_with_retry(
                By.XPATH, "//div[contains(@class, '_aagv')]//img",
                retries=3,
                timeout=10
            )
            if first_reel:
                first_reel.click()
                self.browser.wait_random()

                video_element = self.browser.find_element_with_retry(
                    By.TAG_NAME, "video",
                    retries=3,
                    timeout=10
                )

                if video_element:
                    video_url = video_element.get_attribute("src")

                    if video_url and "blob:" in video_url:
                        logging.info("Extracting video data from blob URL...")
                        video_data = self.driver.execute_script("""
                            async function getVideoData() {
                                let video = document.querySelector('video');
                                let blob = await fetch(video.src).then(r => r.blob());
                                return new Promise((resolve) => {
                                    let reader = new FileReader();
                                    reader.onloadend = () => resolve(reader.result);
                                    reader.readAsDataURL(blob);
                                });
                            }
                            return getVideoData();
                        """)

                        if video_data:
                            video_binary = base64.b64decode(video_data.split(',')[1])
                            filename = os.path.join(DOWNLOAD_DIR, f"reel_{int(time.time())}.mp4")

                            with open(filename, "wb") as file:
                                file.write(video_binary)

                            if self.verify_video(filename):
                                logging.info(f"Successfully downloaded and verified: {filename}")
                                return filename

            logging.error("Failed to download reel")
            return None

        except Exception as e:
            logging.error(f"Failed to download reel: {str(e)}")
            return None

    def close(self):
        """Clean up resources"""
        self.browser.close()

def scrape_with_retry():
    """Scrape with retry mechanism"""
    scraper = ReelScraper()

    for attempt in range(MAX_RETRIES):
        try:
            logging.info(f"Scrape attempt {attempt + 1}/{MAX_RETRIES}")
            if scraper.login():
                for account in TARGET_ACCOUNTS:
                    result = scraper.download_reel_from_account(account)
                    if result:
                        return result
        except Exception as e:
            logging.error(f"Scrape attempt {attempt + 1} failed: {str(e)}")
        finally:
            scraper.close()

        if attempt < MAX_RETRIES - 1:
            logging.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    return None

if __name__ == "__main__":
    scrape_with_retry()