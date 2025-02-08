import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

# Instagram credentials - These should be set via environment variables
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")

# Timing configurations for random intervals
MIN_INTERVAL = 3600  # Minimum 1 hour between posts
MAX_INTERVAL = 7200  # Maximum 2 hours between posts
MIN_WAIT = 5  # Minimum wait time for actions
MAX_WAIT = 10  # Maximum wait time for actions

# File management
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Instagram API settings
INSTAGRAPI_SETTINGS = {
    'device_settings': {
        'app_version': '269.0.0.18.75',
        'android_version': 29,
        'android_release': '10.0',
        'device_model': 'SM-G973F',
        'manufacturer': 'Samsung',
    },
    'request_timeout': 30,
    'video_upload_timeout': 300,
    'max_video_length': 90,
    'sleep_between_requests': 2,
    'max_connection_attempts': 3
}

# Upload settings
MAX_RETRIES = 3
DEFAULT_CAPTION = """#fitness #workout #motivation #gym
#fitnessmotivation #fit #training #health
#sport #healthy #bodybuilding #lifestyle
#fitfam #gymlife #exercise #crossfit"""

# Target accounts to scrape from (add your target accounts here)
TARGET_ACCOUNTS = [
    "fitness_example1",
    "fitness_example2"
]