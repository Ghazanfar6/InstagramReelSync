import os
import time
import json
from instagrapi import Client
from utils import logger, verify_file
from config import USERNAME, PASSWORD, MAX_RETRIES, DEFAULT_CAPTION, INSTAGRAPI_SETTINGS

class InstagrapiUploader:
    def __init__(self):
        self.cl = Client()
        self.is_logged_in = False
        self._configure_client()

    def _configure_client(self):
        """Configure client with device settings and session handling"""
        try:
            # Set device settings
            logger.info("Configuring Instagrapi client with device settings...")
            self.cl.set_device(
                app_version=INSTAGRAPI_SETTINGS['device_settings']['app_version'],
                android_version=INSTAGRAPI_SETTINGS['device_settings']['android_version'],
                android_release=INSTAGRAPI_SETTINGS['device_settings']['android_release'],
                device_model=INSTAGRAPI_SETTINGS['device_settings']['device_model'],
                manufacturer=INSTAGRAPI_SETTINGS['device_settings']['manufacturer']
            )

            # Try to load existing session
            session_file = "instagram_session.json"
            if os.path.exists(session_file):
                try:
                    with open(session_file) as f:
                        cached_settings = json.load(f)
                        self.cl.set_settings(cached_settings)
                        logger.info("Loaded existing session, attempting to verify...")
                        # Verify session is still valid
                        if self.cl.login_by_sessionid(cached_settings.get("sessionid")):
                            logger.info("Successfully restored session")
                            self.is_logged_in = True
                            return
                except Exception as e:
                    logger.warning(f"Failed to load session: {str(e)}")
                    if os.path.exists(session_file):
                        os.remove(session_file)
                        logger.info("Removed invalid session file")

        except Exception as e:
            logger.error(f"Error configuring client: {str(e)}")

    def _save_session(self):
        """Save session data for future use"""
        try:
            with open("instagram_session.json", "w") as f:
                json.dump(self.cl.get_settings(), f)
            logger.info("Session saved successfully")
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")

    def login(self):
        """Login to Instagram using Instagrapi"""
        if self.is_logged_in:
            logger.info("Using existing session")
            return True

        try:
            logger.info("Attempting to login via Instagrapi...")
            self.cl.login(USERNAME, PASSWORD)
            self.is_logged_in = True
            self._save_session()
            logger.info("Login successful")
            return True

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            self.is_logged_in = False
            return False

    def upload_reel(self, file_path, caption=DEFAULT_CAPTION):
        """Upload a reel with verification"""
        if not verify_file(file_path):
            logger.error("Invalid file path or empty file")
            return False

        try:
            if not self.is_logged_in and not self.login():
                logger.error("Not logged in and login attempt failed")
                return False

            logger.info(f"Uploading reel: {file_path}")
            media = self.cl.clip_upload(
                file_path,
                caption=caption,
                extra_data={
                    "custom_accessibility_caption": "Video content",
                    "like_and_view_counts_disabled": False,
                    "disable_comments": False
                }
            )

            if media and hasattr(media, 'pk'):
                logger.info(f"Reel uploaded successfully. Media ID: {media.pk}")
                return True
            else:
                logger.error("Upload failed - no media ID received")
                return False

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            # Clear session on upload failure
            if "login_required" in str(e).lower():
                logger.info("Login expired, clearing session...")
                self.is_logged_in = False
                if os.path.exists("instagram_session.json"):
                    os.remove("instagram_session.json")
            return False

def upload_with_retry(file_path):
    """Upload with retry mechanism"""
    uploader = InstagrapiUploader()

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Upload attempt {attempt + 1}/{MAX_RETRIES}")
            if uploader.login() and uploader.upload_reel(file_path):
                logger.info("Upload completed successfully")
                return True
        except Exception as e:
            logger.error(f"Upload attempt {attempt + 1} failed: {str(e)}")

        if attempt < MAX_RETRIES - 1:
            logger.info("Waiting 60 seconds before retry...")
            time.sleep(60)

    logger.error("All upload attempts failed")
    return False

if __name__ == "__main__":
    from utils import get_latest_download
    latest_file = get_latest_download()
    if latest_file:
        upload_with_retry(latest_file)