import logging
import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, USER_AGENT, DOWNLOAD_DIR
import instaloader

logger = logging.getLogger(__name__)

class InstagramBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.loader = instaloader.Instaloader(download_videos=True, download_comments=False, save_metadata=False, dirname_pattern=DOWNLOAD_DIR)

    def setup_browser(self):
        try:
            logger.info("Setting up Chrome browser...")
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-notifications')
            options.add_argument('--start-maximized')
            options.add_argument(f'user-agent={USER_AGENT}')
            self.driver = webdriver.Chrome(executable_path='C:/Users/mdgha/OneDrive/Desktop/chromedriver.exe', options=options)  # Update the path as needed
            self.wait = WebDriverWait(self.driver, 30)
            logger.info("Browser setup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}")
            return False

    def login_with_cookies(self):
        try:
            logger.info("Attempting to login with cookies...")
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)

            if os.path.exists("cookies.pkl"):
                with open("cookies.pkl", "rb") as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                self.driver.refresh()
                time.sleep(3)

                # Check if login was successful
                if self.driver.current_url == "https://www.instagram.com/":
                    logger.info("Logged in using cookies")
                    return True
                else:
                    logger.warning("Cookies expired or invalid, falling back to username/password login")
                    return False
            else:
                logger.warning("No cookies found, falling back to username/password login")
                return False
        except Exception as e:
            logger.error(f"Login with cookies failed: {str(e)}")
            return False

    def login(self):
        if self.login_with_cookies():
            return True

        try:
            logger.info("Attempting to login with username and password...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)

            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )

            username_field.send_keys(INSTAGRAM_USERNAME)
            time.sleep(1)
            password_field.send_keys(INSTAGRAM_PASSWORD)
            time.sleep(1)

            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
            )
            logger.info("Login successful")

            # Save cookies for future use
            with open("cookies.pkl", "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)

            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def download_reel_from_feed(self):
        try:
            logger.info("Navigating to reels page...")
            self.driver.get("https://www.instagram.com/reels/")
            time.sleep(3)

            # Find the first reel in the reels page
            first_reel = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'x1lliihq')]"))
            )
            first_reel.click()
            time.sleep(3)

            # Get the current URL of the reel
            reel_url = self.driver.current_url
            logger.info(f"Reel URL: {reel_url}")

            # Download the reel using instaloader
            post = instaloader.Post.from_shortcode(self.loader.context, reel_url.split('/')[-2])
            filename = f"{reel_url.split('/')[-2]}.mp4"
            self.loader.download_post(post, target=DOWNLOAD_DIR)
            downloaded_file_path = os.path.join(DOWNLOAD_DIR, filename)
            logger.info(f"Expected downloaded file path: {downloaded_file_path}")

            # Verify the actual saved file name
            actual_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith('.mp4')]
            if actual_files:
                actual_file_path = max([os.path.join(DOWNLOAD_DIR, f) for f in actual_files], key=os.path.getctime)
                logger.info(f"Actual downloaded file path: {actual_file_path}")
                return actual_file_path
            else:
                logger.error("No .mp4 files found in the downloads directory after download")
                return None
        except Exception as e:
            logger.error(f"Failed to download reel: {str(e)}")
            return None

    def upload_reel(self, video_path):
        # Implement your upload logic here
        pass

    def close(self):
        if self.driver:
            self.driver.quit()