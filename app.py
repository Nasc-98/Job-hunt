import os, requests, time, threading
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

# --- CONFIG ---
TOKEN = "7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
CHAT_ID = "2108985800"
URL = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
seen_jobs = set()

@app.route('/')
def home():
    return "OK", 200

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except: pass

def check_logic():
    print("Checking Job Bank...")
    try:
        # Increased timeout to 30 seconds for slow website responses
        res = requests.get(URL, headers=HEADERS, timeout=(5, 30))
        
        if res.status_code != 200:
            print(f"Job Bank busy (Status {res.status_code}).")
            return

        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.find_all("article")
        
        for job in articles:
            link_tag = job.find("a")
            if link_tag:
                link = "https://www.jobbank.gc.ca" + link_tag["href"]
                if link not in seen_jobs:
                    seen_jobs.add(link)
                    try:
                        # Check individual job details
                        details_res = requests.get(link, headers=HEADERS, timeout=20)
                        details = details_res.text.lower()
                        if "candidates with or without a valid canadian work permit" in details:
                            title = link_tag.text.strip()
                            send_tg(f"<b>🇨🇦 NEW LMIA JOB</b>\n\n{title}\n<a href='{link}'>Apply Here</a>")
                    except:
                        continue
    except Exception as e:
        print(f"Scraping error: {e}")

def bot_worker():
    time.sleep(20) # Wait for Render to settle
    send_tg("🚀 <b>Bot Updated!</b> Timeout fixes applied.")
    while True:
        check_logic()
        time.sleep(900) # Wait 15 mins

# Start background thread
threading.Thread(target=bot_worker, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)




