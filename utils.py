import os
import logging
import time
from config import DOWNLOAD_DIR

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def verify_file(file_path):
    """Verify if file exists and is not empty"""
    try:
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            logger.error(f"File is empty: {file_path}")
            return False

        # Check file extension
        if not file_path.lower().endswith(('.mp4', '.mov')):
            logger.error(f"Invalid file type: {file_path}")
            return False

        logger.info(f"Verified file {file_path} (size: {file_size:,} bytes)")
        return True

    except Exception as e:
        logger.error(f"Error verifying file {file_path}: {str(e)}")
        return False

def get_latest_download():
    """Get the most recent downloaded file from downloads directory"""
    try:
        if not os.path.exists(DOWNLOAD_DIR):
            logger.error(f"Download directory {DOWNLOAD_DIR} does not exist")
            return None

        files = os.listdir(DOWNLOAD_DIR)
        if not files:
            logger.warning("No files found in downloads directory")
            return None

        # Get all valid video files
        video_files = [f for f in files if f.lower().endswith(('.mp4', '.mov'))]
        if not video_files:
            logger.warning("No video files found in downloads directory")
            return None

        latest_file = max(
            [os.path.join(DOWNLOAD_DIR, f) for f in video_files],
            key=os.path.getctime
        )

        if verify_file(latest_file):
            logger.info(f"Found latest download: {latest_file}")
            return latest_file

        return None

    except Exception as e:
        logger.error(f"Error getting latest download: {str(e)}")
        return None

def cleanup_old_files(max_age_hours=24):
    """Clean up old downloaded files"""
    try:
        if not os.path.exists(DOWNLOAD_DIR):
            logger.warning(f"Download directory {DOWNLOAD_DIR} does not exist, skipping cleanup")
            return

        current_time = time.time()
        total_removed = 0
        total_size_freed = 0

        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            try:
                if os.path.getctime(file_path) < (current_time - max_age_hours * 3600):
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    total_removed += 1
                    total_size_freed += file_size
                    logger.info(f"Removed old file: {filename} (size: {file_size:,} bytes)")
            except Exception as e:
                logger.error(f"Error removing file {filename}: {str(e)}")

        if total_removed > 0:
            logger.info(f"Cleanup completed: removed {total_removed} files, freed {total_size_freed:,} bytes")
        else:
            logger.info("No files needed cleanup")

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")