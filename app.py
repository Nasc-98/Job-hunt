import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
TOKEN = "7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
CHAT_ID = "2108985800"
URL = "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except: pass

def check_jobs():
    print("Starting Job Bank scan...")
    try:
        res = requests.get(URL, headers=HEADERS, timeout=30)
        if res.status_code != 200: return

        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.find_all("article")
        
        for job in articles:
            link_tag = job.find("a")
            if link_tag:
                link = "https://www.jobbank.gc.ca" + link_tag["href"]
                # We check the job details
                try:
                    details = requests.get(link, headers=HEADERS, timeout=20).text.lower()
                    if "candidates with or without a valid canadian work permit" in details:
                        title = link_tag.text.strip()
                        send_tg(f"<b>🇨🇦 NEW LMIA JOB FOUND</b>\n\n{title}\n<a href='{link}'>Apply Here</a>")
                except: continue
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_jobs()





