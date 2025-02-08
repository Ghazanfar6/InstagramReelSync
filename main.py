import time
import random
from datetime import datetime
import logging
from scraper import scrape_with_retry
from uploader import upload_with_retry
from utils import cleanup_old_files, get_latest_download
from config import MIN_INTERVAL, MAX_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_bot():
    """Execute one complete cycle of scraping and uploading"""
    try:
        logger.info(f"Starting Instagram automation cycle at {datetime.now()}")

        # Clean up old downloads first
        cleanup_old_files()

        # Scrape a new reel
        logger.info("Attempting to scrape a new reel...")
        downloaded_file = scrape_with_retry()
        if not downloaded_file:
            logger.error("Failed to scrape a new reel")
            return False

        # Upload the reel
        logger.info("Attempting to upload the reel...")
        if upload_with_retry(downloaded_file):
            logger.info("Successfully completed the automation cycle")
            return True
        else:
            logger.error("Failed to upload reel after all retries")
            return False

    except Exception as e:
        logger.error(f"Error in automation cycle: {e}")
        return False

def main():
    """Main loop with random intervals"""
    logger.info("Starting Instagram Reel Bot")

    while True:
        try:
            # Run the automation cycle
            success = run_bot()
            status = "Successfully" if success else "Failed to"
            logger.info(f"{status} complete automation cycle")

            # Calculate next run time
            delay = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            next_run = datetime.fromtimestamp(time.time() + delay)
            logger.info(f"Next run scheduled for: {next_run}")

            # Sleep until next run
            time.sleep(delay)

        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            time.sleep(300)  # Wait for 5 minutes before retrying on critical error

if __name__ == "__main__":
    main()