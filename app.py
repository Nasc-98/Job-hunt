import requests
from bs4 import BeautifulSoup

# --- CONFIG ---
TOKEN = "7799390812:AAGyT71IvcB52MHCyEqMtbr_bIylFn2Z3ZI"
CHAT_ID = "2108985800"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

URLS = [
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=LMIA&sort=M",
    "https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring=work+permit&sort=M&fsrc=32"
]

def send_tg(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False}, timeout=15)
    except: pass

def check_jobs():
    print("🚀 Running Styled Universal Filter...")
    for url in URLS:
        try:
            res = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(res.text, "html.parser")
            articles = soup.find_all("article")[:25] 
            
            for job in articles:
                link_tag = job.find("a")
                if link_tag:
                    link = "https://www.jobbank.gc.ca" + link_tag["href"]
                    try:
                        detail_res = requests.get(link, headers=HEADERS, timeout=15)
                        details = detail_res.text.lower()
                        
                        # --- FILTERS ---
                        has_phrase = "without a valid canadian work permit" in details
                        is_lmia = any(x in details for x in ["lmia approved", "positive lmia", "lmia requested"])
                        is_intl = "can apply to this job" in details

                        if has_phrase or is_lmia or is_intl:
                            title = link_tag.text.strip().split('\n')[0] # Get clean title
                            
                            # Determine Status Tag
                            status = "🌟 WORK PERMIT OPEN" if has_phrase else "🍁 LMIA TRACK"
                            
                            # --- STYLED MESSAGE ---
                            message = (
                                f"<b>{status}</b>\n"
                                f"━━━━━━━━━━━━━━━━━━\n"
                                f"💼 <b>JOB:</b> <code>{title.upper()}</code>\n"
                                f"📍 <b>SOURCE:</b> Canada Job Bank\n"
                                f"✅ <b>STATUS:</b> Verified International\n\n"
                                f"🔗 <a href='{link}'><b>[ CLICK HERE TO APPLY ]</b></a>\n"
                                f"━━━━━━━━━━━━━━━━━━"
                            )
                            
                            send_tg(message)
                    except: continue
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    check_jobs()

