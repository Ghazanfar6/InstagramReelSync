import time
import logging
from typing import Optional
from instagrapi import Client
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    DEFAULT_CAPTION,
    MAX_RETRIES
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ReelUploader:
    def __init__(self):
        """Initialize the Instagram API client"""
        self.client = Client()
        self.client.delay_range = [3, 6]  # Random delay between actions

    def login(self) -> bool:
        """Login to Instagram"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def upload_reel(self, video_path: str, caption: Optional[str] = None) -> bool:
        """Upload a reel to Instagram"""
        try:
            if not caption:
                caption = DEFAULT_CAPTION

            logger.info(f"Uploading reel: {video_path}")

            # Configure client settings for better stability
            self.client.request_timeout = 30
            self.client.video_upload_timeout = 300  # 5 minutes for video upload

            # Upload the reel
            self.client.clip_upload(
                video_path,
                caption=caption
            )

            logger.info("Reel uploaded successfully")
            return True

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False

    def close(self):
        """Clean up resources"""
        try:
            self.client.logout()
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")

def upload_with_retry(video_path: str, caption: Optional[str] = None) -> bool:
    """Upload with retry mechanism"""
    uploader = None

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Upload attempt {attempt + 1}/{MAX_RETRIES}")
            uploader = ReelUploader()

            if uploader.login() and uploader.upload_reel(video_path, caption):
                logger.info("Upload completed successfully")
                return True

        except Exception as e:
            logger.error(f"Upload attempt {attempt + 1} failed: {str(e)}")
        finally:
            if uploader:
                uploader.close()

        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    logger.error("All upload attempts failed")
    return False

if __name__ == "__main__":
    # Example usage:
    # upload_with_retry("path/to/video.mp4", "Optional custom caption")
    pass