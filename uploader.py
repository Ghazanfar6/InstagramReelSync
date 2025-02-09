import os
import time
import logging
from instagrapi import Client
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, MAX_RETRIES, DEFAULT_CAPTION

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class InstagramUploader:
    def __init__(self):
        self.cl = Client()
        self.is_logged_in = False

    def login(self):
        """Login to Instagram"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            self.is_logged_in = True
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def upload_reel(self, video_path, caption=DEFAULT_CAPTION):
        """Upload a reel to Instagram"""
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found at: {video_path}")
                return False

            if not self.is_logged_in and not self.login():
                logger.error("Not logged in and login attempt failed")
                return False

            logger.info(f"Uploading reel: {video_path}")
            media = self.cl.clip_upload(
                video_path,
                caption=caption
            )

            if media and hasattr(media, 'pk'):
                logger.info(f"Upload successful. Media ID: {media.pk}")
                return True
            else:
                logger.error("Upload failed - no media ID received")
                return False

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False

def upload_with_retry(video_path):
    """Upload with retry mechanism"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Upload attempt {attempt + 1}/{MAX_RETRIES}")
            uploader = InstagramUploader()
            if uploader.upload_reel(video_path):
                return True
        except Exception as e:
            logger.error(f"Upload attempt {attempt + 1} failed: {str(e)}")

        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    return False

if __name__ == "__main__":
    from utils import get_latest_download
    latest_file = get_latest_download()
    if latest_file:
        upload_with_retry(latest_file)