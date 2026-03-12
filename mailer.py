#!/usr/bin/python3
import smtplib
import time
import datetime
import os
from email.message import EmailMessage

# --- CONFIGURATION ---
SENDER_NAME = "Binance Security"
SENDER_EMAIL = "binancesecurity@gmail.com"
APP_PASSWORD = "kufq wmes uhco ikpe" 
SUBJECT = "[Binance] Login Attempted from New IP address 81.91.128.22"

# --- PROGRESS TRACKING ---
LOG_FILE = "sent_emails.log"
EMAILS_FILE = "emails.txt"
TEMPLATE_FILE = "template.html"

# --- WARMING & AUTO-RESUME SETTINGS ---
DAILY_LIMIT = 50        # Start small and manually increase this daily for warming
COOLDOWN_SECONDS = 60   # 1 minute between individual emails
WAIT_24_HOURS = 86400   # Seconds in a day

def get_already_sent():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f)

def log_success(email):
    with open(LOG_FILE, "a") as f:
        f.write(email + "\n")

def run_daily_batch():
    sent_set = get_already_sent()
    
    with open(EMAILS_FILE, "r") as f:
        all_emails = [line.strip() for line in f if line.strip()]

    pending_emails = [e for e in all_emails if e not in sent_set]
    
    if not pending_emails:
        print("Done! Every email in the list has been delivered.")
        return False # Tells the loop to stop

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template_content = f.read()

    sent_this_session = 0
    
    try:
        print(f"--- Starting Session: {datetime.datetime.now()} ---")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        for recipient in pending_emails:
            if sent_this_session >= DAILY_LIMIT:
                print(f"Limit of {DAILY_LIMIT} reached for today.")
                break

            msg = EmailMessage()
            msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            msg['To'] = recipient
            msg['Subject'] = SUBJECT

            formatted_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S (UTC)")
            custom_html = template_content.replace("email@gmail.com", recipient)
            custom_html = custom_html.replace("2026-03-10 14:05:22 (UTC)", formatted_time)
            
            msg.set_content("HTML is required to view this message.")
            msg.add_alternative(custom_html, subtype='html')

            server.send_message(msg)
            log_success(recipient)
            sent_this_session += 1
            print(f"[{sent_this_session}] Sent to: {recipient}")
            
            time.sleep(COOLDOWN_SECONDS)

        server.quit()
        return True # Keep the loop going for tomorrow
    except Exception as e:
        print(f"Connection error occurred: {e}")
        return True # Try again tomorrow even if it failed today

if __name__ == "__main__":
    while True:
        should_continue = run_daily_batch()
        
        if not should_continue:
            break
            
        print(f"Batch complete. Sleeping for 24 hours...")
        time.sleep(WAIT_24_HOURS)