# Instagram Reel Bot

A bot that automatically downloads and reposts reels from Instagram's reels page at random intervals within an hour.

## Files Structure

- `main.py` - The entry point that orchestrates the automation cycle
- `scraper.py` - Handles downloading reels from Instagram using Selenium
- `uploader.py` - Manages reel uploading using instagrapi
- `config.py` - Contains all configuration settings
- `utils.py` - Helper functions for file management and logging

## Setup Instructions

1. Create a `.env` file with your Instagram credentials:
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

2. Install required packages:
```bash
pip install selenium python-dotenv instagrapi webdriver-manager
```

3. Run the bot:
```bash
python main.py
```

## Configuration

The bot is configured to:
- Scrape reels from Instagram's main reels page
- Post at random intervals (between 55-65 minutes)
- Use default viral hashtags (configurable in config.py)
- Store downloads in the "downloads" directory
- Log activities to "instagram_bot.log"

## Key Features

1. Automated Reel Download:
   - Uses Selenium for web scraping
   - Downloads reels in MP4 format
   - Handles blob URLs and video extraction

2. Automated Posting:
   - Uses instagrapi for reliable uploads
   - Includes retry mechanism
   - Maintains random intervals

3. Error Handling:
   - Comprehensive logging
   - Multiple retry attempts
   - Graceful failure recovery

4. File Management:
   - Automatic cleanup of old downloads
   - Download verification
   - Organized file structure
