import os
import sys
import json
import requests
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEALTH_PATH = os.path.join(BASE_DIR, "system_health.json")
PUBLIC_HEALTH_PATH = os.path.join(BASE_DIR, "public", "system_health.json")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def update_system_health(coupang_status="AUTHENTICATED_ACTIVE", coupang_link_gen="PENDING_VERIFICATION",
                         naver_status="LOGIN_REQUIRED", naver_link_gen="PENDING_VERIFICATION",
                         worker_status="RUNNING"):
    """
    Generates and updates the MORVIX Operational System Health Manifest (system_health.json).
    Serves as the Single Source of Truth for Exception-Based Operations on both Admin UI & Telegram.
    """
    print("==========================================================================")
    print("🩺 UPDATING MORVIX OPERATIONAL SYSTEM HEALTH MANIFEST (system_health.json)")
    print("==========================================================================\n")

    telegram_status = "CONNECTED" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else "READY_TOKEN_PENDING"
    now_iso = datetime.now().isoformat()

    health_data = {
        "version": "1.0.0",
        "last_updated": now_iso,
        "coupang": {
            "session": coupang_status,
            "last_check": now_iso,
            "link_generation": coupang_link_gen
        },
        "naver": {
            "session": naver_status,
            "last_check": now_iso,
            "link_generation": naver_link_gen
        },
        "telegram": {
            "status": telegram_status,
            "last_alert": None
        },
        "worker": {
            "status": worker_status,
            "auto_commit_enabled": True,
            "vercel_deploy_enabled": True
        }
    }

    # Save to workspace root and public directory for Vercel static serving
    with open(HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(health_data, f, ensure_ascii=False, indent=2)

    public_dir = os.path.dirname(PUBLIC_HEALTH_PATH)
    os.makedirs(public_dir, exist_ok=True)
    with open(PUBLIC_HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(health_data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ [HEALTH MANIFEST SAVED]: {HEALTH_PATH}")
    print(f"  • Coupang Session: {coupang_status} ({coupang_link_gen})")
    print(f"  • Naver Session:   {naver_status} ({naver_link_gen})")
    print(f"  • Telegram Alert:  {telegram_status}")
    print(f"  • Worker Engine:   {worker_status}")

    return health_data

if __name__ == "__main__":
    update_system_health()
