import os
import instaloader
import logging
from typing import List, Optional
from config import (
    INSTAGRAM_USERNAME,
    INSTAGRAM_PASSWORD,
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

class ReelDownloader:
    def __init__(self):
        """Initialize the Instagram loader instance"""
        self.loader = instaloader.Instaloader(
            dirname_pattern=DOWNLOAD_DIR,
            filename_pattern="{profile}_{mediaid}",
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False
        )
        self.is_logged_in = False

    def login(self) -> bool:
        """Login to Instagram"""
        try:
            logger.info("Attempting to login to Instagram...")
            self.loader.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            self.is_logged_in = True
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def download_reel(self, shortcode: str) -> Optional[str]:
        """Download a single reel by its shortcode"""
        try:
            if not self.is_logged_in and not self.login():
                return None

            post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
            if post.is_video:
                self.loader.download_post(post, target=DOWNLOAD_DIR)
                # Find the downloaded video file
                for file in os.listdir(DOWNLOAD_DIR):
                    if file.endswith('.mp4') and str(post.mediaid) in file:
                        return os.path.join(DOWNLOAD_DIR, file)
            else:
                logger.warning(f"Post {shortcode} is not a video")
            return None
        except Exception as e:
            logger.error(f"Failed to download reel {shortcode}: {str(e)}")
            return None

    def download_user_reels(self, username: str, max_count: int = 5) -> List[str]:
        """Download recent reels from a user"""
        downloaded_files = []
        try:
            if not self.is_logged_in and not self.login():
                return downloaded_files

            profile = instaloader.Profile.from_username(self.loader.context, username)
            posts = profile.get_posts()
            
            count = 0
            for post in posts:
                if count >= max_count:
                    break
                if post.is_video:
                    file_path = self.download_reel(post.shortcode)
                    if file_path:
                        downloaded_files.append(file_path)
                        count += 1
                        logger.info(f"Downloaded reel {count}/{max_count}")

        except Exception as e:
            logger.error(f"Failed to download reels from {username}: {str(e)}")

        return downloaded_files

def download_with_retry(shortcode: Optional[str] = None, username: Optional[str] = None, max_count: int = 5) -> List[str]:
    """Download reels with retry mechanism"""
    downloader = ReelDownloader()
    downloaded_files = []

    for attempt in range(MAX_RETRIES):
        try:
            if shortcode:
                result = downloader.download_reel(shortcode)
                if result:
                    downloaded_files.append(result)
                    break
            elif username:
                downloaded_files = downloader.download_user_reels(username, max_count)
                if downloaded_files:
                    break
        except Exception as e:
            logger.error(f"Download attempt {attempt + 1} failed: {str(e)}")
        
        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            import time
            time.sleep(60)

    return downloaded_files

if __name__ == "__main__":
    # Example usage
    # For single reel: download_with_retry(shortcode="ABC123")
    # For user reels: download_with_retry(username="target_account", max_count=5)
    pass
