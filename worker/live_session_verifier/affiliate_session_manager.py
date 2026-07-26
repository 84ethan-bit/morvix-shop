import os
import sys
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AFFILIATE_LOG_PATH = os.path.join(BASE_DIR, "affiliate_session_logs.json")
HEALTH_PATH = os.path.join(BASE_DIR, "system_health.json")
PUBLIC_HEALTH_PATH = os.path.join(BASE_DIR, "public", "system_health.json")

COUPANG_DIR = os.path.join(BASE_DIR, "live_session_verifier", "session_coupang_real")
NAVER_DIR = os.path.join(BASE_DIR, "live_session_verifier", "session_naver_real")

def log_session_event(platform, event_type, details):
    logs = []
    if os.path.exists(AFFILIATE_LOG_PATH):
        try:
            with open(AFFILIATE_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform,
        "event_type": event_type,
        "details": details
    }
    logs.insert(0, entry)
    logs = logs[:50]  # Keep last 50 entries
    
    with open(AFFILIATE_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def trigger_interactive_login(platform="coupang"):
    """
    Triggers Chromium persistent context in non-headless mode for Operator STEP 1 pairing.
    Saves cookies/sessionStorage (storageState) upon login completion.
    """
    print("==========================================================================")
    print(f"🔐 MORVIX AFFILIATE SESSION CENTER: PAIRING STEP 1 LOGIN [{platform.upper()}]")
    print("==========================================================================\n")

    session_dir = COUPANG_DIR if platform == "coupang" else NAVER_DIR
    target_portal = "https://partners.coupang.com/" if platform == "coupang" else "https://brandconnect.naver.com/"
    os.makedirs(session_dir, exist_ok=True)

    log_session_event(platform, "LOGIN_TRIGGERED", "Operator initiated interactive login pairing")

    with sync_playwright() as p:
        print(f"[STEP 1] Launching Chromium persistent context for {platform}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=False,  # Operator GUI login window
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print(f"[STEP 2] Navigating to {platform} portal: {target_portal}")
        page.goto(target_portal, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Save storageState
        state_path = os.path.join(session_dir, "storageState.json")
        context.storage_state(path=state_path)
        print(f"  ✅ [STORAGE STATE SAVED]: {state_path}")
        
        log_session_event(platform, "SESSION_SAVED", "storageState.json successfully saved")
        context.close()

    return True

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    plat = sys.argv[2] if len(sys.argv) > 2 else "coupang"
    
    if mode == "login":
        trigger_interactive_login(plat)
    else:
        print("Affiliate Session Manager Ready.")
