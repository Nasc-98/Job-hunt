import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
TOKEN = "7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
CHAT_ID = "2108985800"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

# We now have TWO search links
URLS = [
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M",
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=foreign+worker&sort=M"
]

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except: pass

def check_jobs():
    for url in URLS:
        print(f"Scanning: {url}")
        try:
            res = requests.get(url, headers=HEADERS, timeout=30)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.text, "html.parser")
            for job in soup.find_all("article"):
                link_tag = job.find("a")
                if link_tag:
                    link = "https://www.jobbank.gc.ca" + link_tag["href"]
                    try:
                        details = requests.get(link, headers=HEADERS, timeout=20).text.lower()
                        # The "Magic Phrase" that means they hire from outside Canada
                        if "candidates with or without a valid canadian work permit" in details:
                            title = link_tag.text.strip()
                            send_tg(f"<b>🇨🇦 NEW JOB FOUND</b>\n\n{title}\n<a href='{link}'>Apply Here</a>")
                    except: continue
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    check_jobs()





