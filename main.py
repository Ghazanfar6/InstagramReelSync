import logging
import os
import time
import random
from datetime import datetime
from scraper import InstagramBot
from uploader import upload_with_retry
from config import MIN_INTERVAL, MAX_INTERVAL, PROCESSED_VIDEO_DIR, DOWNLOAD_DIR
from video_processor import crop_video, add_border, overlay_logo

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_latest_file_in_directory(directory: str) -> str:
    """Get the latest file in the specified directory"""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def clean_downloads_folder(directory: str):
    """Delete all files in the specified directory"""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}")

def process_single_reel() -> bool:
    """Process a single reel: download and repost"""
    try:
        logger.info("Downloading reel")
        bot = InstagramBot()
        if not bot.setup_browser():
            raise Exception("Failed to setup browser")

        if not bot.login():
            raise Exception("Failed to login")

        video_path = bot.download_reel_from_feed()
        if not video_path:
            logger.error("Failed to download reel")
            return False

        # Process the downloaded video
        processed_video_path = os.path.join(PROCESSED_VIDEO_DIR, 'processed_video.mp4')
        process_downloaded_video(video_path, processed_video_path)

        logger.info(f"Uploading file: {processed_video_path}")
        success = upload_with_retry(processed_video_path)
        logger.info("Completed" if success else "Failed")
        
        # Clean the downloads folder after uploading
        clean_downloads_folder(DOWNLOAD_DIR)
        
        bot.close()
        return success

    except Exception as e:
        logger.error(f"Error processing reel: {str(e)}")
        return False

def process_downloaded_video(input_path, output_path):
    cropped_path = os.path.join(PROCESSED_VIDEO_DIR, "cropped_" + os.path.basename(output_path))
    bordered_path = os.path.join(PROCESSED_VIDEO_DIR, "bordered_" + os.path.basename(output_path))
    final_path = output_path

    crop_video(input_path, cropped_path)
    add_border(cropped_path, bordered_path)
    overlay_logo(bordered_path, final_path, "C:/Users/mdgha/Downloads/bot/InstagramReelSync/llr.png")

def run_bot():
    """Main bot execution function"""
    logger.info("Starting Instagram Reel Bot")

    while True:
        try:
            logger.info(f"Starting automation cycle at {datetime.now()}")

            success = process_single_reel()

            status = "Successfully" if success else "Failed to"
            logger.info(f"{status} complete automation cycle")

            # Calculate next run time (random interval within 5 to 7 minutes)
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
    run_bot()
    process_downloaded_video("downloaded_video.mp4", "processed_video.mp4")