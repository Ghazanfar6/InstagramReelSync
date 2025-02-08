import os

# Instagram credentials
USERNAME = os.environ.get("INSTAGRAM_USERNAME", "liftlearnrepeat")
PASSWORD = os.environ.get("INSTAGRAM_PASSWORD", "Ghazanfar@19")

# URLs
LOGIN_URL = "https://www.instagram.com/accounts/login/"
REELS_URL = "https://www.instagram.com/reels/"

# Timing configurations (in seconds)
MIN_WAIT = 5  # Minimum wait between actions
MAX_WAIT = 10  # Maximum wait between actions
MIN_INTERVAL = 3600  # Minimum interval between runs (1 hour)
MAX_INTERVAL = 7200  # Maximum interval between runs (2 hours)

# Upload settings
MAX_RETRIES = 3
DEFAULT_CAPTION = """#fitness #workout #motivation #gym
#fitnessmotivation #fit #training #health
#sport #healthy #bodybuilding #lifestyle
#fitfam #gymlife #exercise #crossfit"""

# File paths
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Browser configurations
CHROME_OPTIONS = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.notifications": 2,
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.default_content_settings.popups": 0,
    "disable-popup-blocking": True,
    "start-maximized": True,
    "disable-infobars": True
}

# Additional browser settings
BROWSER_SETTINGS = {
    "PAGE_LOAD_TIMEOUT": 30,
    "IMPLICIT_WAIT": 10,
    "EXPLICIT_WAIT": 20,
    "RETRY_DELAY": 2,
    "VIDEO_PROCESS_WAIT": 15,
    "UPLOAD_CONFIRMATION_WAIT": 20,
    "PAGE_LOAD_WAIT": 8  # Additional wait after page load
}

# User agent string to mimic real browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"