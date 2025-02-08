import time
import random
import logging
from datetime import datetime
from typing import Optional

from downloader import download_with_retry
from uploader import upload_with_retry
from config import (
    MIN_INTERVAL,
    MAX_INTERVAL
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

def process_single_reel(shortcode: str) -> bool:
    """Process a single reel: download and repost"""
    try:
        # Download the reel
        downloaded_files = download_with_retry(shortcode=shortcode)
        if not downloaded_files:
            logger.error("Failed to download reel")
            return False

        # Upload the first downloaded file
        return upload_with_retry(downloaded_files[0])

    except Exception as e:
        logger.error(f"Error processing reel: {str(e)}")
        return False

def process_user_reels(username: str, max_count: int = 5) -> bool:
    """Process multiple reels from a user"""
    try:
        # Download reels
        downloaded_files = download_with_retry(username=username, max_count=max_count)
        if not downloaded_files:
            logger.error(f"Failed to download reels from {username}")
            return False

        # Upload each downloaded file
        success = False
        for file_path in downloaded_files:
            if upload_with_retry(file_path):
                success = True
                break

        return success

    except Exception as e:
        logger.error(f"Error processing user reels: {str(e)}")
        return False

def run_bot(target_username: Optional[str] = None):
    """Main bot execution function"""
    logger.info("Starting Instagram Reel Bot")

    while True:
        try:
            logger.info(f"Starting automation cycle at {datetime.now()}")

            if target_username:
                success = process_user_reels(target_username, max_count=1)
            else:
                # You can add logic here to determine which reel to download
                # For now, we'll just log that we need a target
                logger.error("No target username specified")
                break

            status = "Successfully" if success else "Failed to"
            logger.info(f"{status} complete automation cycle")

            # Calculate next run time (random interval within the hour)
            delay = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            next_run = datetime.fromtimestamp(time.time() + delay)
            logger.info(f"Next run scheduled for: {next_run}")

            # Sleep until next run
            time.sleep(delay)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Critical error in main loop: {str(e)}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == "__main__":
    # Specify the target username whose reels you want to download and repost
    target_username = "example_user"  # Replace with actual username
    run_bot(target_username)