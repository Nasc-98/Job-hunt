import os, requests, time, threading
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

# CONFIGURATION
TOKEN = "7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
CHAT_ID = "2108985800"
URL = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
seen_jobs = set()

@app.route('/')
def health_check():
    return "Bot is active and scanning!", 200

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except: pass

def check_logic():
    print("Scanning for jobs...")
    try:
        res = requests.get(URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        for job in soup.find_all("article"):
            link_tag = job.find("a")
            if link_tag:
                link = "https://www.jobbank.gc.ca" + link_tag["href"]
                if link not in seen_jobs:
                    seen_jobs.add(link)
                    details = requests.get(link, headers=HEADERS, timeout=10).text.lower()
                    if "candidates with or without a valid canadian work permit" in details:
                        title = link_tag.text.strip()
                        send_tg(f"<b>🇨🇦 NEW LMIA JOB</b>\n\n{title}\n<a href='{link}'>Apply Here</a>")
    except Exception as e:
        print(f"Loop Error: {e}")

def bot_loop():
    # Wait 30 seconds for the web server to fully stabilize before first scan
    time.sleep(30)
    send_tg("🚀 <b>Tracker is officially ONLINE!</b>")
    while True:
        check_logic()
        time.sleep(900) # Scan every 15 minutes

# Start the background bot thread
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    # This part is only used for local testing
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


