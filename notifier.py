import os
import time
import requests
import praw
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
    print("❌ Missing values in .env file")
    exit()

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    except Exception as e:
        print("Telegram error:", e)

subreddit = reddit.subreddit("PhotoshopRequest")

print("✅ Monitoring new posts in r/PhotoshopRequest...")

last_seen = None

while True:
    try:
        for post in subreddit.new(limit=1):

            # first run: just store latest post id
            if last_seen is None:
                last_seen = post.id
                print("Initialized with latest post:", post.title)

            # new post detected
            elif post.id != last_seen:
                last_seen = post.id

                message = (
                    f"🆕 New PhotoshopRequest post\n\n"
                    f"{post.title}\n"
                    f"https://reddit.com{post.permalink}"
                )

                print(message)
                send_telegram(message)

        time.sleep(3)

    except Exception as e:
        print("Loop error:", e)
        time.sleep(10)