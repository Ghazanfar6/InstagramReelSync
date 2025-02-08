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

    def wait_for_page_load(self, timeout=30):
        """Wait for the page to be fully loaded"""
        try:
            # Wait for document ready state
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            # Additional wait for Instagram's dynamic content
            time.sleep(BROWSER_SETTINGS['PAGE_LOAD_WAIT'])
            return True
        except Exception as e:
            logger.error(f"Page load timeout: {str(e)}")
            return False

    def wait_for_element_visibility(self, selector, timeout=10):
        """Wait for an element to be visible"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(selector)
            )
            return True
        except Exception:
            return False

    def wait_for_any_element(self, selectors, timeout=10):
        """Wait for any of the given selectors to be visible"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for selector in selectors:
                try:
                    element = self.browser.find_element_with_retry(
                        By.XPATH, selector, retries=1, timeout=2
                    )
                    if element and element.is_displayed():
                        return element
                except Exception:
                    continue
            time.sleep(1)
        return None

    def login(self):
        """Login to Instagram"""
        try:
            logger.info("Initializing browser for upload...")
            self.driver = self.browser.init_browser()
            self.driver.get(LOGIN_URL)

            if not self.wait_for_page_load():
                logger.error("Login page failed to load completely")
                return False

            # Wait for login form visibility
            if not self.wait_for_element_visibility((By.NAME, "username")):
                logger.error("Login form not visible")
                return False

            username_field = self.browser.find_element_with_retry(By.NAME, "username")
            password_field = self.browser.find_element_with_retry(By.NAME, "password")

            # Type credentials with human-like delays
            for char in USERNAME:
                username_field.send_keys(char)
                time.sleep(0.1)

            for char in PASSWORD:
                password_field.send_keys(char)
                time.sleep(0.1)

            password_field.send_keys(Keys.RETURN)
            logger.info("Login credentials entered")

            # Wait for home page to load and verify login success
            if not self.wait_for_page_load():
                logger.error("Home page failed to load after login")
                return False

            # Additional verification of successful login
            home_icon_visible = self.wait_for_element_visibility(
                (By.CSS_SELECTOR, "svg[aria-label='Home']")
            )
            if home_icon_visible:
                logger.info("Login successful - Home icon found")
                return True
            else:
                logger.error("Could not verify successful login - Home icon not found")
                return False

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def find_button_with_text(self, text_list, timeout=10):
        """Find a button using multiple text options and selectors"""
        all_selectors = []
        for text in text_list:
            selectors = [
                f"//div[text()='{text}']",
                f"//span[text()='{text}']",
                f"//button[text()='{text}']",
                f"//div[@role='button'][text()='{text}']",
                f"//button[contains(.,'{text}')]",
                f"//div[contains(.,'{text}')]",
                f"//a[contains(.,'{text}')]",
                f"//*[contains(@aria-label,'{text}')]",
                f"//div[contains(@class,'x1i10hfl')][contains(.,'{text}')]",
                f"//div[contains(@class,'_abl-')][contains(.,'{text}')]"
            ]
            all_selectors.extend(selectors)

        return self.wait_for_any_element(all_selectors, timeout)

    def wait_for_upload_complete(self, timeout=60):
        """Wait for upload to complete and verify success"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                page_source = self.driver.page_source.lower()

                # Check for success indicators
                success_phrases = [
                    'reel was shared',
                    'post has been shared',
                    'post shared',
                    'successfully uploaded',
                    'share complete'
                ]

                for phrase in success_phrases:
                    if phrase in page_source:
                        logger.info(f"Upload confirmed: Found '{phrase}'")
                        return True

                # Check for error messages
                error_phrases = [
                    'error occurred',
                    'upload failed',
                    'try again',
                    'something went wrong',
                    'cannot upload'
                ]

                for phrase in error_phrases:
                    if phrase in page_source:
                        logger.error(f"Upload failed: Found '{phrase}'")
                        return False

                time.sleep(2)

            logger.warning("Upload confirmation timed out")
            return False

        except Exception as e:
            logger.error(f"Error waiting for upload completion: {str(e)}")
            return False

    def upload_reel(self, file_path, caption=DEFAULT_CAPTION):
        """Upload a reel with verification"""
        if not verify_file(file_path):
            logger.error("Invalid file path or empty file")
            return False

        try:
            logger.info("Initiating reel upload process...")

            # Ensure the page is fully loaded
            if not self.wait_for_page_load():
                logger.error("Page not fully loaded before upload")
                return False

            # Find and click Create button
            create_button = self.find_button_with_text(
                ['Create', 'New post', 'New reel', 'Add post', 'Create new post'],
                timeout=20
            )
            if not create_button:
                logger.error("Could not find Create button")
                return False

            create_button.click()
            logger.info("Clicked Create button")
            self.browser.wait_random()

            # Find and click Post button
            post_button = self.find_button_with_text(
                ['Post', 'Select from computer', 'Upload', 'Select files'],
                timeout=15
            )
            if not post_button:
                logger.error("Could not find Post button")
                return False

            post_button.click()
            logger.info("Clicked Post button")
            self.browser.wait_random()

            # Upload file
            logger.info(f"Uploading file: {file_path}")
            file_input = self.browser.find_element_with_retry(
                By.CSS_SELECTOR, "input[type='file']",
                timeout=BROWSER_SETTINGS['EXPLICIT_WAIT']
            )
            file_input.send_keys(file_path)
            logger.info("File selected for upload")

            # Wait for video processing
            time.sleep(BROWSER_SETTINGS['VIDEO_PROCESS_WAIT'])
            logger.info("Waiting for video processing...")

            # Find and click Next button
            next_button = self.find_button_with_text(['Next', 'Continue'], timeout=15)
            if not next_button:
                logger.error("Could not find Next button")
                return False

            next_button.click()
            logger.info("Clicked Next button")
            self.browser.wait_random()

            # Find caption input
            caption_selectors = [
                "//textarea[@aria-label='Write a caption...']",
                "//textarea[@placeholder='Write a caption...']",
                "//textarea",
                "//*[@role='textbox']"
            ]

            caption_box = None
            for selector in caption_selectors:
                try:
                    caption_box = self.browser.find_element_with_retry(
                        By.XPATH, selector, retries=2, timeout=5
                    )
                    if caption_box and caption_box.is_displayed():
                        break
                except Exception:
                    continue

            if not caption_box:
                logger.error("Could not find caption input")
                return False

            # Type caption with human-like delays
            logger.info("Adding caption...")
            for char in caption:
                caption_box.send_keys(char)
                time.sleep(0.05)
            logger.info("Caption added")
            self.browser.wait_random()

            # Find and click Share button
            share_button = self.find_button_with_text(['Share', 'Post', 'Upload now'], timeout=15)
            if not share_button:
                logger.error("Could not find Share button")
                return False

            share_button.click()
            logger.info("Clicked Share button")

            # Wait for upload confirmation
            return self.wait_for_upload_complete()

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