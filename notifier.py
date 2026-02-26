import os
import time
import requests
from flask import Flask
from threading import Thread

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SUBREDDIT = "PhotoshopRequest"
CHECK_INTERVAL = 20  # seconds

last_seen = None

app = Flask(__name__)

@app.route("/")
def home():
    return "PSR Alert Running"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def monitor():
    global last_seen

    while True:
        try:
            url = f"https://www.reddit.com/r/{SUBREDDIT}/new.json?limit=5"
            headers = {"User-Agent": "PSRAlertBot"}

            res = requests.get(url, headers=headers)
            data = res.json()

            posts = data["data"]["children"]

            for post in reversed(posts):
                p = post["data"]

                post_id = p["id"]
                flair = p.get("link_flair_text")

                if last_seen is None:
                    last_seen = post_id
                    continue

                if post_id == last_seen:
                    continue

                last_seen = post_id

                # 🔥 FILTER ONLY PAID POSTS
                if flair != "Paid":
                    continue

                title = p["title"]
                link = f"https://reddit.com{p['permalink']}"

                msg = f"💰 <b>PAID Request Posted</b>\n\n{title}\n\n{link}"
                send_telegram(msg)

        except Exception as e:
            print("Error:", e)

        time.sleep(CHECK_INTERVAL)

def start_monitor():
    Thread(target=monitor).start()

if __name__ == "__main__":
    start_monitor()
    app.run(host="0.0.0.0", port=10000)