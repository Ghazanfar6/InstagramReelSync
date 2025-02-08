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

# Wait time ranges (in seconds)
MIN_WAIT = 2
MAX_WAIT = 5

# Chrome browser settings
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--window-size=1920,1080'
]

BROWSER_SETTINGS = {
    'timeout': 45,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}