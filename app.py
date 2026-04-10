import requests
from bs4 import BeautifulSoup
import time

# --- CONFIG ---
TOKEN = "7799390812:AAHdWgi0tq2O100RkDqzYB9G8oHvTUzSSZA"
CHAT_ID = "2108985800"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

URLS = [
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M",
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=foreign+worker&sort=M"
]

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=25)
    except: pass

def safe_get(url, retries=3):
    """Attempt to get a URL up to 3 times if it times out"""
    for i in range(retries):
        try:
            # Increase read timeout significantly to 60 seconds
            return requests.get(url, headers=HEADERS, timeout=(10, 60))
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
            if i < retries - 1:
                print(f"⚠️ Slow connection for {url}. Retrying ({i+1}/3)...")
                time.sleep(5) # Wait 5 seconds before trying again
            else:
                print(f"❌ Failed after {retries} attempts.")
                return None
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            return None

def get_data(soup, label_text):
    try:
        label = soup.find(lambda tag: tag.name == "span" and label_text in tag.text)
        if label and label.parent:
            return label.parent.get_text().replace(label_text, "").strip()
    except: return "Check Link"
    return "Check Link"

def check_jobs():
    print("🚀 Running persistent Auto-Retry Scraper...")
    processed = set()
    
    for url in URLS:
        res = safe_get(url)
        if not res: continue
        
        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.find_all("article")[:10] 
        
        for job in articles:
            link_tag = job.find("a")
            if link_tag:
                link = "https://www.jobbank.gc.ca" + link_tag["href"]
                if link in processed: continue
                processed.add(link)
                
                date_tag = job.find("li", class_="date")
                date_text = date_tag.get_text().lower() if date_tag else ""
                
                # Only check fresh jobs
                if any(x in date_text for x in ["hour", "minute", "just"]):
                    detail_res = safe_get(link)
                    if not detail_res: continue
                    
                    if "without a valid canadian work permit" in detail_res.text.lower():
                        dsoup = BeautifulSoup(detail_res.text, "html.parser")
                        title = link_tag.text.strip().split('\n').upper()
                        location = job.find("li", class_="location").get_text().strip() if job.find("li", class_="location") else "Canada"
                        salary = get_data(dsoup, "Salary:")
                        edu = get_data(dsoup, "Education")

                        msg = (
                            f"<b>✨ FRESH JOB | {date_text.upper()}</b>\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"💼 <b>JOB:</b> <code>{title}</code>\n"
                            f"📍 <b>LOC:</b> {location}\n"
                            f"💰 <b>PAY:</b> {salary}\n"
                            f"🎓 <b>EDU:</b> {edu}\n"
                            f"━━━━━━━━━━━━━━━━━━\n"
                            f"🔗 <a href='{link}'><b>[ VIEW & APPLY NOW ]</b></a>"
                        )
                        send_tg(msg)
                        print(f"✅ Sent: {title}")

if __name__ == "__main__":
    check_jobs()
