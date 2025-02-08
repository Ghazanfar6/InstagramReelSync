import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

# Instagram credentials
INSTAGRAM_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")

# Timing configurations
MIN_INTERVAL = 3600  # Minimum 1 hour between posts
MAX_INTERVAL = 7200  # Maximum 2 hours between posts
MIN_WAIT = 5  # Minimum wait time for actions
MAX_WAIT = 10  # Maximum wait time for actions

# File management
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Upload settings
MAX_RETRIES = 3
DEFAULT_CAPTION = """#fitness #workout #motivation #gym
#fitnessmotivation #fit #training #health
#sport #healthy #bodybuilding #lifestyle
#fitfam #gymlife #exercise #crossfit"""

# Target accounts to scrape from
TARGET_ACCOUNTS = [
    "fitness_example1",
    "fitness_example2"
]