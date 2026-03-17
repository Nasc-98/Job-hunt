import os
import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask

# 1. FLASK WEB SERVER (To keep Render happy)
app = Flask(__name__)

@app.route('/')
def home():
    return "Job Tracker is Running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Start the web server in the background
threading.Thread(target=run_web_server, daemon=True).start()

# 2. CONFIGURATION
# It is better to put these in Render's "Environment Variables" later
BOT_TOKEN = "7799390812:AAHdWgi0tq2O100RkDqzYB9G8oHvTUzSSZA"
CHAT_ID = "2108985800"
URL = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M"

seen_jobs = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

def is_international_friendly(job_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    try:
        response = requests.get(job_url, headers=headers, timeout=10)
        text = response.text.lower()
        # Look for the specific phrase Job Bank uses for international candidates
        if "other candidates with or without a valid canadian work permit" in text:
            return True
        return False
    except:
        return False

def check_jobs():
    print("Scanning Job Bank...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("article")

        for job in jobs:
            title_tag = job.find("a")
            if title_tag:
                link = "https://www.jobbank.gc.ca" + title_tag["href"]
                if link not in seen_jobs:
                    if is_international_friendly(link):
                        job_title = title_tag.text.strip()
                        message = f"<b>🇨🇦 NEW LMIA JOB</b>\n\n<b>Role:</b> {job_title}\n<b>Link:</b> {link}"
                        send_telegram(message)
                        print(f"Alert sent: {job_title}")
                    seen_jobs.add(link)
    except Exception as e:
        print(f"Scraping Error: {e}")

# 3. THE INFINITE LOOP (The part that keeps it running)
if __name__ == "__main__":
    # This confirms the bot is alive on your phone immediately
    send_telegram("🚀 <b>LMIA Job Tracker is now LIVE!</b>\nSearching for Canada jobs...")
    
    while True:
        check_jobs()
        # Wait 15 minutes (900 seconds) so you don't get banned
        time.sleep(900)