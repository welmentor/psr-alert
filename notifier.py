import os
import time
import requests
import praw
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "PSR Alert Running"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_flask).start()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="psr-alert"
)

subreddit = reddit.subreddit("PhotoshopRequest")

seen_posts = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }
    requests.post(url, data=data)

print("Monitoring Reddit...")

while True:
    try:
        for post in subreddit.new(limit=10):

            if post.id in seen_posts:
                continue

            seen_posts.add(post.id)

            title = post.title.lower()
            flair = (post.link_flair_text or "").lower()

            combined_text = title + " " + flair

            # 🚫 Ignore FREE
            if "free" in combined_text:
                continue

            # ✅ Only allow PAID
            if "paid" in combined_text:
                message = f"💰 New PAID PhotoshopRequest\n\n{post.title}\n\n{post.url}"
                send_telegram(message)

        time.sleep(20)

    except Exception as e:
        print("Error:", e)
        time.sleep(30)