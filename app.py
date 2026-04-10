import requests
from bs4 import BeautifulSoup
from datetime import datetime

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
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=15)
    except: pass

def get_text_after_label(soup, label_text):
    try:
        label = soup.find(lambda tag: tag.name == "span" and label_text in tag.text)
        if label and label.parent:
            return label.parent.get_text().replace(label_text, "").strip()
    except: return "Not listed"
    return "Not listed"

def check_jobs():
    print("🚀 Scanning for UNIQUE new jobs...")
    processed_in_this_run = set()
    
    for url in URLS:
        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.find_all("article")[:15] 
            
            for job in articles:
                link_tag = job.find("a")
                if link_tag:
                    link = "https://www.jobbank.gc.ca" + link_tag["href"]
                    
                    # Prevent processing the same link twice in the same 10-minute scan
                    if link in processed_in_this_run: continue
                    processed_in_this_run.add(link)
                    
                    try:
                        # 1. Check the date on the search page first
                        date_tag = job.find("li", class_="date")
                        date_text = date_tag.get_text().lower() if date_tag else ""
                        
                        # ONLY process if it says 'hours ago' or 'minutes ago'
                        # This stops it from repeating older jobs from 'yesterday'
                        if "hour" in date_text or "minute" in date_text or "just" in date_text:
                            
                            detail_res = requests.get(link, headers=HEADERS, timeout=12)
                            detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                            details_text = detail_res.text.lower()
                            
                            phrase = "without a valid canadian work permit"
                            if phrase in details_text:
                                title = link_tag.text.strip().split('\n').upper()
                                loc_tag = job.find("li", class_="location")
                                location = loc_tag.get_text().strip() if loc_tag else "Canada"
                                salary = get_text_after_label(detail_soup, "Salary:")
                                education = get_text_after_label(detail_soup, "Education")

                                message = (
                                    f"<b>✨ FRESH JOB ALERT</b>\n"
                                    f"━━━━━━━━━━━━━━━━━━\n"
                                    f"💼 <b>JOB:</b> <code>{title}</code>\n"
                                    f"📍 <b>LOCATION:</b> {location}\n"
                                    f"💰 <b>PAY:</b> {salary}\n"
                                    f"🎓 <b>EDU:</b> {education}\n"
                                    f"🕒 <b>POSTED:</b> {date_text.capitalize()}\n"
                                    f"━━━━━━━━━━━━━━━━━━\n"
                                    f"🔗 <a href='{link}'><b>[ VIEW & APPLY NOW ]</b></a>\n"
                                )
                                send_tg(message)
                                print(f"Sent: {title}")
                        else:
                            print(f"Skipping older job: {link}")
                    except: continue
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    check_jobs()
