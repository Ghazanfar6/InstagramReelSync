import os

# Instagram credentials
USERNAME = os.environ.get("INSTAGRAM_USERNAME", "your_username")  # Replace with your username
PASSWORD = os.environ.get("INSTAGRAM_PASSWORD", "your_password")  # Replace with your password

# Timing configurations
MIN_WAIT = 5
MAX_WAIT = 10
MIN_INTERVAL = 3600  # 1 hour
MAX_INTERVAL = 7200  # 2 hours

# Upload settings
MAX_RETRIES = 3
DEFAULT_CAPTION = """#fitness #workout #motivation #gym
#fitnessmotivation #fit #training #health
#sport #healthy #bodybuilding #lifestyle
#fitfam #gymlife #exercise #crossfit"""

# File paths
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Instagrapi settings - Optimized for better success rate
INSTAGRAPI_SETTINGS = {
    'device_settings': {
        'app_version': '269.0.0.18.75',  # Latest stable version
        'android_version': 29,
        'android_release': '10.0',
        'device_model': 'SM-G973F',  # Samsung Galaxy S10
        'manufacturer': 'Samsung',
    },
    'request_timeout': 30,  # Timeout for requests in seconds
    'video_upload_timeout': 300,  # 5 minutes timeout for video uploads
    'max_video_length': 90,  # Maximum video length in seconds
    'sleep_between_requests': 2,  # Sleep time between API requests
    'max_connection_attempts': 3  # Maximum number of connection retry attempts
}