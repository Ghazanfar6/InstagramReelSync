import os
import time
import logging
from instagrapi import Client
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    INSTAGRAPI_SETTINGS,
    DEFAULT_CAPTION,
    MAX_RETRIES
)
from utils import verify_file

logger = logging.getLogger(__name__)

class InstagramUploader:
    def __init__(self):
        self.client = Client()
        self.client.set_device_settings(INSTAGRAPI_SETTINGS['device_settings'])
        self.client.request_timeout = INSTAGRAPI_SETTINGS['request_timeout']
        self.client.video_upload_timeout = INSTAGRAPI_SETTINGS['video_upload_timeout']
        self.client.sleep_between_requests = INSTAGRAPI_SETTINGS['sleep_between_requests']
        self.client.max_connection_attempts = INSTAGRAPI_SETTINGS['max_connection_attempts']

    def login(self):
        """Login to Instagram using instagrapi"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def upload_reel(self, file_path, caption=DEFAULT_CAPTION):
        """Upload a reel using instagrapi"""
        if not verify_file(file_path):
            logger.error("Invalid file path or empty file")
            return False

        try:
            logger.info(f"Uploading reel: {file_path}")
            self.client.clip_upload(
                file_path,
                caption=caption
            )
            logger.info("Reel uploaded successfully")
            return True

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False

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