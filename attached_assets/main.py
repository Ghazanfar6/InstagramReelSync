import time
import random
import subprocess

def run_bot():
    print("🚀 Running Instagram automation...")

    subprocess.run(["python", "scraper.py"])  # Scrape reels
    time.sleep(random.randint(1800, 3600))  # Wait 30-60 mins

    subprocess.run(["python", "uploader.py"])  # Upload reels
    print("✅ Task completed. Next run in a random hour.")

while True:
    delay = random.randint(3600, 7200)  # Random delay (1-2 hours)
    print(f"⏳ Next run scheduled in {delay // 60} minutes.")
    time.sleep(delay)
    run_bot()
