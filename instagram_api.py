import os
import json
import requests
import time
from utils import logger

class InstagramAPI:
    def __init__(self):
        self.access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        self.user_id = os.environ.get("INSTAGRAM_USER_ID")
        self.base_url = "https://graph.instagram.com/v12.0"
        
    def upload_reel(self, video_path, caption=""):
        """
        Upload reel using Instagram Graph API
        """
        try:
            # Step 1: Create container for the reel
            container_response = requests.post(
                f"{self.base_url}/{self.user_id}/media",
                params={
                    "access_token": self.access_token,
                    "media_type": "REELS",
                    "video_url": video_path,
                    "caption": caption,
                    "share_to_feed": "true"
                }
            )
            
            if not container_response.ok:
                logger.error(f"Failed to create container: {container_response.text}")
                return False
                
            container_data = container_response.json()
            creation_id = container_data.get("id")
            
            if not creation_id:
                logger.error("No creation ID received")
                return False
            
            # Step 2: Wait for video processing
            status = "IN_PROGRESS"
            max_attempts = 10
            attempt = 0
            
            while status == "IN_PROGRESS" and attempt < max_attempts:
                status_response = requests.get(
                    f"{self.base_url}/{creation_id}",
                    params={"access_token": self.access_token}
                )
                
                if status_response.ok:
                    status = status_response.json().get("status_code", "ERROR")
                    if status == "FINISHED":
                        break
                        
                attempt += 1
                time.sleep(5)
                
            if status != "FINISHED":
                logger.error(f"Video processing failed or timed out. Status: {status}")
                return False
                
            # Step 3: Publish the reel
            publish_response = requests.post(
                f"{self.base_url}/{self.user_id}/media_publish",
                params={
                    "access_token": self.access_token,
                    "creation_id": creation_id
                }
            )
            
            if publish_response.ok:
                logger.info("Reel published successfully")
                return True
            else:
                logger.error(f"Failed to publish reel: {publish_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading reel: {str(e)}")
            return False

def upload_reel_api(file_path, caption=""):
    """Helper function to upload reel using API"""
    api = InstagramAPI()
    return api.upload_reel(file_path, caption)
