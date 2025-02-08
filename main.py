import time
import random
from datetime import datetime
from utils import logger, cleanup_old_files, get_latest_download
from instagrapi_uploader import upload_with_retry
from config import MIN_INTERVAL, MAX_INTERVAL

def run_bot():
    """Execute one complete cycle of uploading"""
    try:
        logger.info(f"Starting Instagram automation cycle at {datetime.now()}")

        # Clean up old downloads first
        cleanup_old_files()

        # Get the latest downloaded reel
        latest_file = get_latest_download()
        if not latest_file:
            logger.error("No valid reel found in downloads directory")
            return False

        # Upload the reel using Instagrapi
        logger.info("Attempting to upload the reel...")
        if upload_with_retry(latest_file):
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