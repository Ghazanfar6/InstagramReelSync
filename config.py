import os
from dotenv import load_dotenv

# Explicitly reload environment variables from .env file
load_dotenv(override=True)

# Instagram credentials
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')

# Print the loaded username to confirm
print(f"Loaded Instagram username: {INSTAGRAM_USERNAME}")

# Directory settings
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Directory for processed videos
PROCESSED_VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'processed_videos')
os.makedirs(PROCESSED_VIDEO_DIR, exist_ok=True)

# Directory for video processor
VIDEO_PROCESSOR_DIR = os.path.join(os.path.dirname(__file__), 'video_processor')
os.makedirs(VIDEO_PROCESSOR_DIR, exist_ok=True)

# Default caption template for reposts
DEFAULT_CAPTION = """🔥 Bringing you the best fitness content! If this belongs to you and you’d like credit or removal, please DM me. 💪📩 Stay strong, stay motivated! 🚀 #trending #viral #explorepage #reels #fyp #fitnessmotivation #gymrat #workout #fitspo #trainhard"""

# Timing configurations (in seconds)
MIN_INTERVAL = 300  # 5 minutes
MAX_INTERVAL = 420  # 7 minutes

# Maximum retries for operations
MAX_RETRIES = 3

# User agent for web scraping
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"