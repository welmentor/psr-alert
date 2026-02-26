import time
import requests
import os
import random
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)

@app.route("/")
def home():
    return "PSR Alert running"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def monitor():
    URL = "https://www.reddit.com/r/PhotoshopRequest/new/.json"
    headers = {"User-Agent": f"PSRalert-{random.randint(1,99999)}"}
    last_seen = None

    print("Monitoring Reddit...")

    while True:
        try:
            response = requests.get(
                URL,
                headers=headers,
                params={"limit":1, "raw_json":1, "_": time.time()}
            )
            data = response.json()
            post = data["data"]["children"][0]["data"]
            post_id = post["id"]

            if last_seen is None:
                last_seen = post_id
                print("Initialized with:", post["title"])

            elif post_id != last_seen:
                last_seen = post_id
                link = "https://reddit.com" + post["permalink"]
                message = f"🆕 New PhotoshopRequest post\n\n{post['title']}\n{link}"
                print(message)
                send_telegram(message)

            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

Thread(target=monitor).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)