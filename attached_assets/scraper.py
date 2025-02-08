import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import os
import base64
from config import USERNAME, PASSWORD

# Initialize Chrome
options = uc.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": os.path.abspath("downloads"),  # Set download folder
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})

driver = uc.Chrome(options=options)

def login():
    """Logs into Instagram"""
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(random.randint(5, 10))

    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.NAME, "password").submit()

    time.sleep(random.randint(5, 10))

def scrape_reel():
    """Finds a reel, detects URL change, and downloads it"""
    driver.get("https://www.instagram.com/reels/")
    time.sleep(random.randint(5, 10))

    print("🔍 Searching for a reel...")

    try:
        # Click on the first reel in the feed
        first_reel = driver.find_element(By.XPATH, "//div[@role='button']")
        first_reel.click()
        time.sleep(random.randint(5, 10))

        # Wait for the URL to change
        new_url = driver.current_url
        print(f"🔗 Reel URL: {new_url}")

        # Extract video element
        video_element = driver.find_element(By.TAG_NAME, "video")
        video_url = video_element.get_attribute("src")

        if "blob:" in video_url:
            print("⚠ Blob URL detected, extracting video data...")

            # Extract the actual video data from the blob URL
            video_data = driver.execute_script("""
                let video = document.querySelector('video');
                let canvas = document.createElement('canvas');
                let ctx = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                return canvas.toDataURL('image/png');
            """)

            # Convert Base64 to binary
            video_binary = base64.b64decode(video_data.split(',')[1])

            if not os.path.exists("downloads"):
                os.mkdir("downloads")

            filename = f"downloads/reel_{int(time.time())}.mp4"

            with open(filename, "wb") as file:
                file.write(video_binary)

            print(f"✅ Successfully downloaded: {filename}")

        else:
            print("❌ Could not extract video data.")

    except Exception as e:
        print(f"❌ Failed to download reel: {e}")

login()
scrape_reel()
driver.quit()
