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

# --- WARMING LOGIC ---
# Day 1: 50, Day 2: 100, Day 3: 200, Day 4+: 450
DAILY_LIMIT = 50 
COOLDOWN_SECONDS = 60 # 1 minute between sends to look natural
LOG_FILE = "sent_emails.log"

def get_already_sent():
    """Reads the log file to see who we already emailed."""
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f)

def log_success(email):
    """Saves successfully sent email to the log."""
    with open(LOG_FILE, "a") as f:
        f.write(email + "\n")

def send_notifications():
    # 1. Load your full email list
    with open("emails.txt", "r") as f:
        all_emails = [line.strip() for line in f if line.strip()]

    # 2. Check progress
    sent_set = get_already_sent()
    # Filter out people who already received it
    pending_emails = [e for e in all_emails if e not in sent_set]
    
    if not pending_emails:
        print("All emails in the list have been sent!")
        return

    # 3. Load HTML
    with open("template.html", "r", encoding="utf-8") as f:
        template_content = f.read()

    sent_this_session = 0
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        for recipient in pending_emails:
            if sent_this_session >= DAILY_LIMIT:
                print(f"Daily limit of {DAILY_LIMIT} reached. See you tomorrow!")
                break

            msg = EmailMessage()
            msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            msg['To'] = recipient
            msg['Subject'] = SUBJECT

            now = datetime.datetime.now(datetime.timezone.utc)
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S (UTC)")

            # Personalized replacements
            custom_html = template_content.replace("email@gmail.com", recipient)
            custom_html = custom_html.replace("2026-03-10 14:05:22 (UTC)", formatted_time)
            
            msg.set_content("Please view in an HTML compatible viewer.")
            msg.add_alternative(custom_html, subtype='html')

            # Execute Send
            server.send_message(msg)
            
            # Record Progress
            log_success(recipient)
            sent_this_session += 1
            
            print(f"[{sent_this_session}] Successfully sent to: {recipient}")

            # Human-like delay
            time.sleep(COOLDOWN_SECONDS)

        server.quit()
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    send_notifications()