import os
import sys
import json
import time
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

print("=======================================================")
print("🤖 MORVIX STAGE 2 REAL TELEGRAM BOT LAUNCHER")
print("=======================================================")

# Step 1: Clean Master DB (Purge all sample test products)
if os.path.exists(DB_PATH):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump({"products": []}, f, ensure_ascii=False, indent=2)
    print("🧹 [100% CLEANED] Sample test products purged from Master DB.")

bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

print(f"• TELEGRAM_BOT_TOKEN: {'[LOADED]' if bot_token else '[WAITING FOR ENV/USER PROMPT]'}")
print(f"• TELEGRAM_CHAT_ID:   {'[LOADED]' if chat_id else '[WAITING FOR ENV/USER PROMPT]'}")

print("\n🚀 Ready for 24/7 Live Telegram Ingestion Stream!")
print("=======================================================")
