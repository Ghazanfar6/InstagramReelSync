import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging
from browser import BrowserManager
from config import USERNAME, PASSWORD, LOGIN_URL, DEFAULT_CAPTION, MAX_RETRIES
from utils import logger, verify_file

class InstagramUploader:
    def __init__(self):
        self.browser = BrowserManager()
        self.driver = None

    def login(self):
        """Login to Instagram"""
        try:
            self.driver = self.browser.init_browser()
            self.driver.get(LOGIN_URL)
            self.browser.wait_random()

            username_field = self.browser.find_element_with_retry(By.NAME, "username")
            password_field = self.browser.find_element_with_retry(By.NAME, "password")

            username_field.send_keys(USERNAME)
            password_field.send_keys(PASSWORD + Keys.RETURN)
            
            self.browser.wait_random()
            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def upload_reel(self, file_path, caption=DEFAULT_CAPTION):
        """Upload a reel with verification"""
        if not verify_file(file_path):
            logger.error("Invalid file path or empty file")
            return False

        try:
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
            self.browser.wait_random()

            # Click Next
            next_button = self.browser.find_element_with_retry(
                By.XPATH, "//div[text()='Next']"
            )
            next_button.click()
            self.browser.wait_random()

            # Add caption
            caption_box = self.browser.find_element_with_retry(
                By.XPATH, "//textarea"
            )
            caption_box.send_keys(caption)

            # Share
            share_button = self.browser.find_element_with_retry(
                By.XPATH, "//div[text()='Share']"
            )
            share_button.click()
            
            # Wait for upload confirmation
            self.browser.wait_random()
            logger.info("Reel uploaded successfully")
            return True

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False

    def close(self):
        """Clean up resources"""
        self.browser.close()

def upload_with_retry(file_path):
    """Upload with retry mechanism"""
    uploader = InstagramUploader()
    
    for attempt in range(MAX_RETRIES):
        try:
            if uploader.login() and uploader.upload_reel(file_path):
                return True
        except Exception as e:
            logger.error(f"Upload attempt {attempt + 1} failed: {e}")
        finally:
            uploader.close()
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(60)  # Wait before retry
    
    return False

if __name__ == "__main__":
    from utils import get_latest_download
    latest_file = get_latest_download()
    if latest_file:
        upload_with_retry(latest_file)
