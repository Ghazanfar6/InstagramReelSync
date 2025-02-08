import os
import time
import random
import logging
from instagrapi import Client
from datetime import datetime

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
    def __init__(self, username, password):
        self.client = Client()
        self.username = username
        self.password = password
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)

    def login(self):
        """Login to Instagram"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.client.login(self.username, self.password)
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def get_user_reels(self, username, amount=5):
        """Get recent reels from a user"""
        try:
            user_id = self.client.user_id_from_username(username)
            medias = self.client.user_medias(user_id, amount=amount)
            return [media for media in medias if media.media_type == 2]  # Type 2 is video/reel
        except Exception as e:
            logger.error(f"Failed to get user reels: {str(e)}")
            return []

    def download_reel(self, media_pk):
        """Download a reel by media PK"""
        try:
            path = self.client.clip_download(media_pk, folder=self.download_dir)
            logger.info(f"Successfully downloaded reel to: {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to download reel: {str(e)}")
            return None

    def upload_reel(self, video_path, caption):
        """Upload a reel"""
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return False

            logger.info(f"Uploading reel: {video_path}")
            self.client.clip_upload(video_path, caption=caption)
            logger.info("Reel uploaded successfully")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return False

    def cleanup_old_files(self, max_age_hours=24):
        """Clean up old downloaded files"""
        try:
            current_time = time.time()
            for filename in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, filename)
                if os.path.getctime(file_path) < (current_time - max_age_hours * 3600):
                    os.remove(file_path)
                    logger.info(f"Removed old file: {filename}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

def run_bot(username, password, target_accounts, caption, min_interval, max_interval):
    """Main bot execution function"""
    bot = InstagramBot(username, password)

    while True:
        try:
            logger.info(f"Starting Instagram automation cycle at {datetime.now()}")

            if not bot.login():
                raise Exception("Failed to login")

            bot.cleanup_old_files()

            for account in target_accounts:
                reels = bot.get_user_reels(account)
                if reels:
                    path = bot.download_reel(reels[0].pk)
                    if path and bot.upload_reel(path, caption):
                        logger.info("Successfully completed automation cycle")
                        break

            delay = random.randint(min_interval, max_interval)
            next_run = datetime.fromtimestamp(time.time() + delay)
            logger.info(f"Next run scheduled for: {next_run}")
            time.sleep(delay)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in automation cycle: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    from config import (
        INSTAGRAM_USERNAME,
        INSTAGRAM_PASSWORD,
        TARGET_ACCOUNTS,
        DEFAULT_CAPTION,
        MIN_INTERVAL,
        MAX_INTERVAL
    )

    run_bot(
        INSTAGRAM_USERNAME,
        INSTAGRAM_PASSWORD,
        TARGET_ACCOUNTS,
        DEFAULT_CAPTION,
        MIN_INTERVAL,
        MAX_INTERVAL
    )