import sys, os, time, requests, json
from datetime import datetime, timedelta
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN", "8303557513:AAH-1PkmgBzPCw0AxJJXGlF0o9bLAaLxADU")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "5145353085")

print("=======================================================")
print("🤖 LISTENING FOR USER'S REAL TELEGRAM DEAL MESSAGE...")
print("=======================================================")

from subprocess import run

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

# Fetch latest offset to get newest message
offset = 0
try:
    res = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=10).json()
    if res.get("result"):
        offset = res["result"][-1]["update_id"]
    print(f"📡 Current Offset: {offset}. Waiting for user message...")
except Exception as e:
    print(f"⚠️ Error getting initial offset: {e}")

start_time = time.time()
detected = False

while time.time() - start_time < 60:  # Listen for up to 60 seconds
    try:
        res = requests.get(f"https://api.telegram.org/bot{token}/getUpdates?offset={offset+1}&timeout=5", timeout=10).json()
        for u in res.get("result", []):
            offset = u["update_id"]
            if 'message' in u:
                msg = u['message']
                text = msg.get('text', '')
                sender = msg.get('from', {}).get('first_name', 'User')
                print(f"\n📩 [NEW MESSAGE RECEIVED FROM {sender}]:\n'{text}'")
                
                # Execute autonomous ingestion
                run([sys.executable, "worker/telegram_watcher_cloud.py", text], cwd=BASE_DIR)
                
                # Auto Commit & Push to GitHub
                run(["git", "add", "."], cwd=BASE_DIR)
                run(["git", "commit", "-m", f"auto: User live Telegram deal ingestion [{text[:20]}...]"], cwd=BASE_DIR)
                run(["git", "push", "origin", "main"], cwd=BASE_DIR)
                
                print(f"🚀 Live Deployed to Vercel (https://morvix-shop.vercel.app)!")
                detected = True
                break
        if detected:
            break
    except Exception as e:
        time.sleep(2)

if not detected:
    print("\n⏳ Still waiting for incoming Telegram message. Daemon remains active in background!")
print("=======================================================")
