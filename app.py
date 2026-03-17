import os, requests, time, threading
from bs4 import BeautifulSoup
from flask import Flask

# The variable name MUST be 'app' for 'gunicorn app:app' to work
app = Flask(__name__)

@app.route('/')
def home():
    return "Job Tracker is Active"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Start Flask in a separate thread
threading.Thread(target=run_web_server, daemon=True).start()

# --- CONFIG ---
TOKEN = "7799390812:AAHdWgi0tq2O100RkDqzYB9G8oHvTUzSSZA"
CHAT_ID = "2108985800"
URL = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

seen_jobs = set()

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except:
        pass

def check():
    try:
        res = requests.get(URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for job in soup.find_all("article"):
            link_tag = job.find("a")
            if link_tag:
                link = "https://www.jobbank.gc.ca" + link_tag["href"]
                if link not in seen_jobs:
                    seen_jobs.add(link)
                    # Check for international eligibility
                    try:
                        details = requests.get(link, headers=HEADERS, timeout=10).text.lower()
                        if "candidates with or without a valid canadian work permit" in details:
                            title = link_tag.text.strip()
                            send_tg(f"<b>🇨🇦 NEW LMIA JOB</b>\n\n{title}\n<a href='{link}'>Apply Here</a>")
                    except:
                        continue
    except Exception as e: 
        print(f"Error: {e}")

if __name__ == "__main__":
    send_tg("🚀 <b>Tracker Started!</b> Python 3.11 is active.")
    while True:
        check()
        time.sleep(900)

