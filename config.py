import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Instagram credentials
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")

# Directory configurations
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Default caption template for reposts
DEFAULT_CAPTION = """#reels #viral #trending #instagram 
#explore #instareels #reelsvideo #reelitfeelit 
#explorepage #instadaily #viralreels #instagood
#reelsinstagram #follow #like #reelkarofeelkaro"""

# Timing configurations (in seconds)
MIN_INTERVAL = 3300  # 55 minutes
MAX_INTERVAL = 3900  # 65 minutes

# Maximum retries for operations
MAX_RETRIES = 3

# Browser settings
MIN_WAIT = 2
MAX_WAIT = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

CHROME_OPTIONS = {
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.media_stream_mic": 2,
    "profile.default_content_setting_values.media_stream_camera": 2,
}

BROWSER_SETTINGS = {
    'PAGE_LOAD_TIMEOUT': 30,
    'IMPLICIT_WAIT': 10,
    'EXPLICIT_WAIT': 20,
    'RETRY_DELAY': 5
}