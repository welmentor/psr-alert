import os
import time
import requests
import threading
from collections import deque
from flask import Flask
from dotenv import load_dotenv

# Load local .env variables for testing in Cursor
load_dotenv()

app = Flask(__name__)

# Keep only the last 50 post IDs to prevent memory leaks
seen_posts = deque(maxlen=50)

def send_telegram(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")

def monitor_reddit():
    print("Starting background Reddit JSON monitor...")
    
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("CRITICAL: Missing Telegram Environment Variables! Bot will not send alerts.")
        return

    # A custom User-Agent is strictly required when hitting Reddit's JSON feed
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = "https://www.reddit.com/r/PhotoshopRequest/new.json?limit=10"

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                # Reverse the list so we process the oldest posts in the batch first
                for post in reversed(posts):
                    post_data = post.get('data', {})
                    post_id = post_data.get('id')
                    
                    if not post_id or post_id in seen_posts:
                        continue
                        
                    seen_posts.append(post_id)
                    
                    title = (post_data.get('title') or '').lower()
                    flair = (post_data.get('link_flair_text') or '').lower()
                    combined_text = title + " " + flair
                    
                    # 🚫 Ignore FREE
                    if "free" in combined_text:
                        continue
                        
                    # ✅ Only allow PAID
                    if "paid" in combined_text:
                        permalink = post_data.get('permalink')
                        full_url = f"https://www.reddit.com{permalink}"
                        clean_title = post_data.get('title')
                        
                        message = f"💰 New PAID Request\n\n{clean_title}\n\n{full_url}"
                        send_telegram(message, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
                        print(f"Alert sent for: {clean_title}")
            else:
                print(f"Reddit API returned status: {response.status_code}")
                
        except Exception as e:
            print(f"Reddit Monitoring Error: {e}")
            
        # Poll every 30 seconds
        time.sleep(30)

# Start the background worker BEFORE starting Flask
worker_thread = threading.Thread(target=monitor_reddit)
worker_thread.daemon = True 
worker_thread.start()

@app.route('/')
def home():
    return "PSR Alert JSON System Running Flawlessly"

if __name__ == "__main__":
    # Render assigns a dynamic PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)