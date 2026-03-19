import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
TOKEN = "7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
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
    """Helper to find data like 'Salary' or 'Education' in the Job Bank page"""
    try:
        label = soup.find(lambda tag: tag.name == "span" and label_text in tag.text)
        if label and label.parent:
            return label.parent.get_text().replace(label_text, "").strip()
    except: return "Not listed"
    return "Not listed"

def check_jobs():
    print("🚀 Scanning for detailed International & LMIA Jobs...")
    processed_links = set()
    for url in URLS:
        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.find_all("article")[:15] 
            
            for job in articles:
                link_tag = job.find("a")
                if link_tag:
                    link = "https://www.jobbank.gc.ca" + link_tag["href"]
                    if link in processed_links: continue
                    processed_links.add(link)
                    
                    try:
                        detail_res = requests.get(link, headers=HEADERS, timeout=12)
                        detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                        details_text = detail_res.text.lower()
                        
                        # ELIGIBILITY CHECK: The 'Magic Phrase' from your image
                        phrase = "without a valid canadian work permit"
                        if phrase in details_text:
                            # 1. Title
                            title = link_tag.text.strip().split('\n')[0].upper()
                            
                            # 2. Location (Usually inside a span with class 'city')
                            loc_tag = job.find("li", class_="location")
                            location = loc_tag.get_text().strip() if loc_tag else "Canada"
                            
                            # 3. Pay / Salary
                            salary = get_text_after_label(detail_soup, "Salary:")
                            
                            # 4. Education
                            education = get_text_after_label(detail_soup, "Education")
                            if education == "Not listed": # Alternate check
                                if "secondary (high) school graduation certificate" in details_text:
                                    education = "High School Certificate"
                                elif "no degree, certificate or diploma" in details_text:
                                    education = "No Degree Required"

                            # --- THE STYLED OUTPUT ---
                            message = (
                                f"<b>🇨🇦 NEW JOB FOUND</b>\n"
                                f"━━━━━━━━━━━━━━━━━━\n"
                                f"💼 <b>JOB:</b> <code>{title}</code>\n"
                                f"📍 <b>LOCATION:</b> {location}\n"
                                f"💰 <b>PAY:</b> {salary}\n"
                                f"🎓 <b>EDU:</b> {education}\n"
                                f"━━━━━━━━━━━━━━━━━━\n"
                                f"🔗 <a href='{link}'><b>[ VIEW & APPLY NOW ]</b></a>\n"
                            )
                            send_tg(message)
                    except: continue
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    check_jobs()
