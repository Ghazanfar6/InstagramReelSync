import os
import time
import random
import logging
from datetime import datetime
from instagrapi import Client
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
    TARGET_ACCOUNTS,
    DEFAULT_CAPTION,
    MIN_INTERVAL,
    MAX_INTERVAL,
    DOWNLOAD_DIR,
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

class InstagramBot:
    def __init__(self):
        self.client = Client()
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    def login(self):
        """Login to Instagram"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def download_reel(self, username):
        """Download latest reel from a user"""
        try:
            logger.info(f"Attempting to download reel from {username}")
            user_id = self.client.user_id_from_username(username)
            medias = self.client.user_medias(user_id, amount=1)

            if not medias:
                logger.warning(f"No media found for user {username}")
                return None

            media = medias[0]
            if media.media_type != 2:  # Type 2 is video/reel
                logger.warning(f"Latest media from {username} is not a reel")
                return None

            path = self.client.clip_download(media.pk, folder=DOWNLOAD_DIR)
            logger.info(f"Successfully downloaded reel to: {path}")
            return path

        except Exception as e:
            logger.error(f"Failed to download reel: {str(e)}")
            return None

    def upload_reel(self, video_path):
        """Upload a reel"""
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return False

            logger.info(f"Uploading reel: {video_path}")
            self.client.clip_upload(
                video_path,
                caption=DEFAULT_CAPTION
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

def run_bot():
    """Main bot execution function with retry mechanism"""
    bot = InstagramBot()

    while True:
        try:
            logger.info(f"Starting Instagram automation cycle at {datetime.now()}")

            # Login attempt with retries
            for attempt in range(MAX_RETRIES):
                if bot.login():
                    break
                if attempt < MAX_RETRIES - 1:
                    time.sleep(60)  # Wait before retry
            else:
                raise Exception("Failed to login after maximum retries")

            # Try downloading from each target account
            for account in TARGET_ACCOUNTS:
                path = bot.download_reel(account)
                if path and bot.upload_reel(path):
                    logger.info("Successfully completed automation cycle")
                    break

            # Random delay before next cycle
            delay = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            next_run = datetime.fromtimestamp(time.time() + delay)
            logger.info(f"Next run scheduled for: {next_run}")
            time.sleep(delay)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in automation cycle: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying
        finally:
            bot.close()

if __name__ == "__main__":
    run_bot()