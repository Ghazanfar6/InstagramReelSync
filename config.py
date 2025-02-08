import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Instagram credentials
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")

# Timing configurations (in seconds)
MIN_INTERVAL = 3300  # 55 minutes (random time within the hour)
MAX_INTERVAL = 3900  # 65 minutes

# Script configurations
MAX_RETRIES = 3
MIN_WAIT = 2  # Minimum wait time between actions
MAX_WAIT = 5  # Maximum wait time between actions

# Directory for downloaded reels
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Default caption for reposts
DEFAULT_CAPTION = """#reels #viral #trending #instagram 
#explore #instareels #reelsvideo #reelitfeelit 
#explorepage #instadaily #viralreels #instagood
#reelsinstagram #follow #like #reelkarofeelkaro"""