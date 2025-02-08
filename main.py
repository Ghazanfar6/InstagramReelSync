import time
import random
from datetime import datetime
import logging
from scraper import scrape_with_retry
from uploader import upload_with_retry
from config import MIN_INTERVAL, MAX_INTERVAL

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

def run_bot():
    """Execute one complete cycle of scraping and uploading"""
    try:
        logger.info(f"Starting Instagram automation cycle at {datetime.now()}")

        # Scrape a reel
        downloaded_file = scrape_with_retry()
        if not downloaded_file:
            logger.error("Failed to download reel")
            return False

        # Upload the reel
        if upload_with_retry(downloaded_file):
            logger.info("Successfully completed the automation cycle")
            return True

        logger.error("Failed to upload reel")
        return False

    except Exception as e:
        logger.error(f"Error in automation cycle: {str(e)}")
        return False

def main():
    """Main loop with random intervals within 1 hour"""
    logger.info("Starting Instagram Reel Bot")

    while True:
        try:
            # Run the automation cycle
            success = run_bot()
            status = "Successfully" if success else "Failed to"
            logger.info(f"{status} complete automation cycle")

            # Calculate next run time (random time within the hour)
            delay = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            next_run = datetime.fromtimestamp(time.time() + delay)
            logger.info(f"Next run scheduled for: {next_run}")

            # Sleep until next run
            time.sleep(delay)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            time.sleep(300)  # Wait for 5 minutes before retrying on critical error

if __name__ == "__main__":
    main()