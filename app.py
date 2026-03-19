import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
TOKEN = "7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
CHAT_ID = "2108985800"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

# We use the official "International" filter link + your search terms
URLS = [
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M&fsrc=32",
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=foreign+worker&sort=M&fsrc=32"
]

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except: pass

def check_jobs():
    print("🚀 Scanning for International & LMIA Jobs...")
    for url in URLS:
        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.find_all("article")[:20] # Check 20 most recent
            
            for job in articles:
                link_tag = job.find("a")
                if link_tag:
                    link = "https://www.jobbank.gc.ca" + link_tag["href"]
                    try:
                        detail_res = requests.get(link, headers=HEADERS, timeout=15)
                        details = detail_res.text.lower()
                        
                        # NEW RELAXED RULES:
                        # 1. Look for the 'International' icon text
                        # 2. Look for 'LMIA Approved'
                        # 3. Look for the work permit phrase
                        is_international = "can apply to this job" in details
                        is_approved = "lmia approved" in details or "positive lmia" in details
                        
                        if is_international or is_approved:
                            title = link_tag.text.strip()
                            # Avoid sending duplicate alerts if multiple keywords hit
                            send_tg(f"<b>🇨🇦 LMIA OPPORTUNITY FOUND</b>\n\n<b>{title}</b>\n\n<a href='{link}'>Click here to Apply</a>")
                    except: continue
        except Exception as e:
            print(f"Error scanning: {e}")

if __name__ == "__main__":
    check_jobs()



