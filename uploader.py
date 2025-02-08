import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from browser import BrowserManager
from config import USERNAME, PASSWORD, LOGIN_URL, DEFAULT_CAPTION, MAX_RETRIES, BROWSER_SETTINGS
from utils import logger, verify_file

class InstagramUploader:
    def __init__(self):
        self.browser = BrowserManager()
        self.driver = None

    def login(self):
        """Login to Instagram"""
        try:
            logger.info("Initializing browser for upload...")
            self.driver = self.browser.init_browser()
            self.driver.get(LOGIN_URL)
            self.browser.wait_random()

            username_field = self.browser.find_element_with_retry(By.NAME, "username")
            password_field = self.browser.find_element_with_retry(By.NAME, "password")

            username_field.send_keys(USERNAME)
            password_field.send_keys(PASSWORD)
            password_field.submit()

            self.browser.wait_random()

            # Verify login success
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']"))
                )
                logger.info("Login successful")
                return True
            except Exception:
                logger.error("Could not verify successful login")
                return False

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def upload_reel(self, file_path, caption=DEFAULT_CAPTION):
        """Upload a reel with verification"""
        if not verify_file(file_path):
            logger.error("Invalid file path or empty file")
            return False

        try:
            logger.info("Starting reel upload process...")

            # Click Create button
            create_button = self.browser.find_element_with_retry(
                By.XPATH, "//div[text()='Create']"
            )
            create_button.click()
            self.browser.wait_random()

            # Click Post option
            post_button = self.browser.find_element_with_retry(
                By.XPATH, "//div[text()='Post']"
            )
            post_button.click()
            self.browser.wait_random()

            # Upload file
            file_input = self.browser.find_element_with_retry(
                By.CSS_SELECTOR, "input[type='file']"
            )
            file_input.send_keys(file_path)
            time.sleep(BROWSER_SETTINGS['VIDEO_PROCESS_WAIT'])

            # Click Next
            next_button = self.browser.find_element_with_retry(
                By.XPATH, "//div[text()='Next']"
            )
            next_button.click()
            self.browser.wait_random()

            # Add caption
            caption_box = self.browser.find_element_with_retry(
                By.XPATH, "//textarea[@aria-label='Write a caption...']"
            )
            caption_box.send_keys(caption)
            self.browser.wait_random()

            # Share
            share_button = self.browser.find_element_with_retry(
                By.XPATH, "//div[text()='Share']"
            )
            share_button.click()

            # Wait for upload confirmation
            try:
                WebDriverWait(self.driver, BROWSER_SETTINGS['UPLOAD_CONFIRMATION_WAIT']).until(
                    lambda x: any(
                        msg in x.page_source.lower() 
                        for msg in ['reel was shared', 'post has been shared', 'post shared']
                    )
                )
                logger.info("Reel uploaded successfully")
                return True
            except Exception:
                logger.error("Could not confirm upload success")
                return False

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False

    def close(self):
        """Clean up resources"""
        self.browser.close()

def upload_with_retry(file_path):
    """Upload with retry mechanism"""
    uploader = InstagramUploader()

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Upload attempt {attempt + 1}/{MAX_RETRIES}")
            if uploader.login() and uploader.upload_reel(file_path):
                logger.info("Upload completed successfully")
                return True
        except Exception as e:
            logger.error(f"Upload attempt {attempt + 1} failed: {str(e)}")
        finally:
            uploader.close()

        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    logger.error("All upload attempts failed")
    return False

if __name__ == "__main__":
    from utils import get_latest_download
    latest_file = get_latest_download()
    if latest_file:
        upload_with_retry(latest_file)