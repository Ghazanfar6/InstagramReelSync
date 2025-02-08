import time
import logging
from instagrapi import Client
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    DEFAULT_CAPTION,
    MAX_RETRIES
)

logger = logging.getLogger(__name__)

class InstagramUploader:
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [3, 5]

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
        try:
            logger.info(f"Uploading reel: {file_path}")
            
            # Configure client settings for better stability
            self.client.request_timeout = 30
            self.client.private_request_timeout = 30
            
            # Upload the reel
            self.client.clip_upload(
                file_path,
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

def upload_with_retry(file_path):
    """Upload with retry mechanism"""
    uploader = None
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Upload attempt {attempt + 1}/{MAX_RETRIES}")
            uploader = InstagramUploader()
            
            if uploader.login() and uploader.upload_reel(file_path):
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
