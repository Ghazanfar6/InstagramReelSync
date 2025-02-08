import time
import random
from datetime import datetime
from utils import logger, cleanup_old_files
from scraper import scrape_with_retry
from uploader import upload_with_retry
from config import MIN_INTERVAL, MAX_INTERVAL

def run_bot():
    """Execute one complete cycle of scraping and uploading"""
    try:
        logger.info(f"Starting Instagram automation cycle at {datetime.now()}")

        # Clean up old downloads first
        cleanup_old_files()

        # Step 1: Download a new reel
        logger.info("Attempting to scrape a new reel...")
        downloaded_file = scrape_with_retry()

        if not downloaded_file:
            logger.error("Failed to download reel after all retries")
            return False

        logger.info(f"Successfully downloaded reel: {downloaded_file}")

        # Step 2: Upload the downloaded reel
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
            # Wait for 5 minutes before retrying on critical error
            time.sleep(300)

if __name__ == "__main__":
    main()