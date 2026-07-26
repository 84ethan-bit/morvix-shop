import os
import sys
import requests
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_telegram_channel(token=None, chat_id=None):
    print("📱 [MORVIX OS] Testing Telegram Notification Channel Connection...")

    bot_token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    target_chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not target_chat_id:
        print("\n⚠️ [NOTICE] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured in Environment Variables.")
        print("💡 Usage:")
        print("   set TELEGRAM_BOT_TOKEN=123456789:ABCDefgh...")
        print("   set TELEGRAM_CHAT_ID=987654321")
        print("   python worker/test_telegram.py\n")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    test_msg = (
        "🤖 *[MORVIX OS Worker Notification Channel Test]*\n\n"
        "🟢 *Status:* `PROCESS_SUCCESS` (100% Empirically Verified)\n"
        f"⏱️ *Timestamp:* `{now_str}`\n"
        "📦 *Master DB Status:* `4 Products Active`\n"
        "🎯 *Sync Result:* `Sync Audit Log Recorded`\n\n"
        "📱 *Notification Channel:* Telegram Alert Gateway Online! 🚀"
    )

    payload = {
        "chat_id": target_chat_id,
        "text": test_msg,
        "parse_mode": "Markdown"
    }

    try:
        print(f"📡 Sending HTTP POST request to Telegram API (Chat ID: {target_chat_id})...")
        res = requests.post(url, json=payload, timeout=8)
        
        if res.status_code == 200:
            print("=======================================================")
            print("✅ TELEGRAM NOTIFICATION CHANNEL VERIFIED SUCCESSFULLY!")
            print(f"• HTTP Status Code: {res.status_code} OK")
            print(f"• Telegram Response: {res.json().get('ok')}")
            print("• Real Mobile Phone Alert Delivered!")
            print("=======================================================")
            return True
        else:
            print("=======================================================")
            print("❌ TELEGRAM API ERROR RETURNED:")
            print(f"• Status Code: {res.status_code}")
            print(f"• Response Text: {res.text}")
            print("=======================================================")
            return False
    except Exception as e:
        print(f"❌ Network Exception connecting to Telegram API: {e}")
        return False

if __name__ == "__main__":
    test_telegram_channel()
