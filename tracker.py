import requests
import feedparser
import time

import os

PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
TOKEN = os.getenv("WHATSAPP_TOKEN")
RECIPIENT = os.getenv("RECIPIENT_NUMBER")

RSS_FEEDS = [
    "https://www.livelaw.in/rss/top-stories.xml",
    "https://www.barandbench.com/rss",
    "https://www.taxscan.in/feed"
]

def get_last_timestamp():
    with open("last_sent.txt", "r") as f:
        return float(f.read().strip())

def update_timestamp(ts):
    with open("last_sent.txt", "w") as f:
        f.write(str(ts))

def fetch_cases(last_ts):
    new_items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = time.mktime(entry.published_parsed) if hasattr(entry, "published_parsed") else 0
            if published > last_ts:
                new_items.append((published, entry.title, entry.link))
    new_items.sort(reverse=True)
    return new_items[:5]

def send_whatsapp(message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT,
        "type": "text",
        "text": {"body": message}
    }
    print("SENDING TO:", RECIPIENT)
    print("PHONE ID:", PHONE_NUMBER_ID) 
    
    response = requests.post(url, headers=headers, json=payload)
    
    print(response.status_code)
    print(response.text)

def main():
    last_ts = get_last_timestamp()
    cases = fetch_cases(last_ts)
    if not cases:
        send_whatsapp("🕒 No new Supreme Court / High Court / ITAT / GST updates this hour.")
        return
    message = "*🧾 Hourly Litigation Tracker*\n\n"

    newest_ts = last_ts

for idx, (ts, title, link) in enumerate(cases, 1):
    message += f"*{idx}. {title}*\n"
    message += f"{link}\n\n"

    if ts > newest_ts:
        newest_ts = ts
    newest_ts = last_ts
    for idx, (ts, title, link) in enumerate(cases, 1):
        message += f"{idx}. {title}\n{link}\n\n"
        if ts > newest_ts:
            newest_ts = ts
    send_whatsapp(message)
    update_timestamp(newest_ts)

if __name__ == "__main__":
    main()
