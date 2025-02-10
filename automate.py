import schedule
import time
import random
import logging
from rich.console import Console
from rich.table import Table
from rich.live import Live
from scraper import InstagramBot
from uploader import upload_with_retry
from utils import cleanup_old_files

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
console = Console()

def download_and_upload_reel(table):
    try:
        bot = InstagramBot()
        if not bot.setup_browser():
            raise Exception("Failed to setup browser")

        if not bot.login():
            raise Exception("Failed to login")

        table.rows[0].cells[1].text = "Downloading"
        video_path = bot.download_reel_from_feed()
        if not video_path:
            raise Exception("Failed to download reel")

        table.rows[0].cells[1].text = "Uploading"
        if upload_with_retry(video_path):
            logger.info("Successfully downloaded and uploaded reel")
            table.rows[0].cells[1].text = "Completed"
        else:
            logger.error("Failed to upload reel")
            table.rows[0].cells[1].text = "Failed"

        bot.close()
    except Exception as e:
        logger.error(f"Error in download_and_upload_reel: {str(e)}")
        table.rows[0].cells[1].text = "Error"

def job(table):
    # Schedule the job to run at a random time within the next hour
    delay = random.randint(0, 3600)
    logger.info(f"Scheduling next job in {delay} seconds")
    table.rows[1].cells[1].text = f"In {delay} seconds"
    time.sleep(delay)
    download_and_upload_reel(table)

def display_dashboard():
    table = Table(title="Instagram Reel Sync Dashboard")

    table.add_column("Task", justify="left", style="cyan", no_wrap=True)
    table.add_column("Status", justify="left", style="magenta")

    table.add_row("Download and Upload Reel", "Pending")
    table.add_row("Next Job", "Pending")
    table.add_row("Cleanup Old Files", "Pending")

    with Live(table, refresh_per_second=1) as live:
        while True:
            schedule.run_pending()
            time.sleep(1)

# Schedule the job to run every hour
schedule.every().hour.do(job, table=Table(title="Instagram Reel Sync Dashboard"))

# Clean up old files every day
schedule.every().day.at("00:00").do(cleanup_old_files)

if __name__ == "__main__":
    display_dashboard()