import os
import time
import requests
import praw
from flask import Flask
from threading import Thread

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

reddit = praw.Reddit(
    client_id=os.environ.get("REDDIT_CLIENT_ID"),
    client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
    user_agent="psr-alert"
)

subreddit = reddit.subreddit("PhotoshopRequest")

seen_posts = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

def monitor():
    print("Monitoring Reddit...")
    while True:
        try:
            for post in subreddit.new(limit=20):
                if post.id in seen_posts:
                    continue

                flair = (post.link_flair_text or "").lower()
                title = (post.title or "").lower()

                if "paid" not in flair and "paid" not in title:
                    continue

                seen_posts.add(post.id)

                message = f"""
💰 <b>Paid Request Found</b>

📝 {post.title}

🔖 Flair: {post.link_flair_text}

🔗 https://reddit.com{post.permalink}
"""
                send_telegram(message)

        except Exception as e:
            print("Error:", e)

        time.sleep(20)

app = Flask(__name__)

@app.route('/')
def home():
    return "Running"

def run():
    monitor()

Thread(target=run).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)