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
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=20)
    except: pass

def get_data(soup, label_text):
    try:
        label = soup.find(lambda tag: tag.name == "span" and label_text in tag.text)
        if label and label.parent:
            return label.parent.get_text().replace(label_text, "").strip()
    except: return "Not listed"
    return "Not listed"

def check_jobs():
    print("🚀 Starting High-Speed Detailed Scan...")
    processed_in_this_run = set()
    
    for url in URLS:
        try:
            # Increased timeout to 30 to stop the error in your screenshot
            res = requests.get(url, headers=HEADERS, timeout=30)
            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.find_all("article")[:12] 
            
            for job in articles:
                link_tag = job.find("a")
                if link_tag:
                    link = "https://www.jobbank.gc.ca" + link_tag["href"]
                    if link in processed_in_this_run: continue
                    processed_in_this_run.add(link)
                    
                    # DATE CHECK: Only send if it's brand new (hours/minutes ago)
                    date_tag = job.find("li", class_="date")
                    date_text = date_tag.get_text().lower() if date_tag else ""
                    
                    if any(x in date_text for x in ["hour", "minute", "just"]):
                        try:
                            # Added a tiny delay so the website doesn't block us
                            time.sleep(1) 
                            detail_res = requests.get(link, headers=HEADERS, timeout=25)
                            detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                            
                            # ELIGIBILITY CHECK
                            if "without a valid canadian work permit" in detail_res.text.lower():
                                title = link_tag.text.strip().split('\n').upper()
                                location = job.find("li", class_="location").get_text().strip() if job.find("li", class_="location") else "Canada"
                                salary = get_data(detail_soup, "Salary:")
                                edu = get_data(detail_soup, "Education")

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
                        except: continue
        except Exception as e:
            print(f"⚠️ Connection slow, skipping this batch. Error: {e}")

if __name__ == "__main__":
    check_jobs()
