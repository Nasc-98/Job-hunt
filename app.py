import requests
from bs4 import BeautifulSoup

TOKEN ="7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
CHAT_ID = "2108985800"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

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
    print("🚀 Starting fast scan...")
    for url in URLS:
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")
            for job in soup.find_all("article")[:15]: # We check the 15 most recent jobs per link
                link_tag = job.find("a")
                if link_tag:
                    link = "https://www.jobbank.gc.ca" + link_tag["href"]
                    try:
                        # We only wait 10 seconds per job detail page
                        details = requests.get(link, headers=HEADERS, timeout=10).text.lower()
                        if "without a valid canadian work permit" in details:
                            title = link_tag.text.strip()
                            send_tg(f"<b>🇨🇦 FOUND FOR YOU</b>\n\n{title}\n<a href='{link}'>Apply Here</a>")
                    except: continue
        except Exception as e: print(f"Error: {e}")
    print("✅ Scan complete.")

if __name__ == "__main__":
    check_jobs()




