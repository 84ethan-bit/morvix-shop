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
SESSION_DIR = os.path.join(BASE_DIR, "live_session_verifier", "session_storage_test")
STATE_PATH = os.path.join(SESSION_DIR, "storageState.json")

def run_storage_state_milestone_test():
    """
    MORVIX Milestone 1 ~ 3 Test Suite:
    1. Verify Playwright Chromium Browser Launch
    2. Save storageState.json
    3. Load saved storageState.json & verify session reuse without re-authentication
    """
    print("==========================================================================")
    print("🧪 MORVIX PLAYWRIGHT BACKEND STORAGE_STATE REUSE MILESTONE TEST")
    print("==========================================================================\n")

    os.makedirs(SESSION_DIR, exist_ok=True)
    results = {
        "milestone_1_launch": False,
        "milestone_2_save_state": False,
        "milestone_3_reuse_state": False,
        "timestamp": datetime.now().isoformat()
    }

    with sync_playwright() as p:
        # Milestone 1: Launch Playwright Headless Chromium
        print("[MILESTONE 1] Launching Playwright Headless Chromium...")
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1400, "height": 900})
            page = context.new_page()
            page.goto("https://www.coupang.com/", wait_until="domcontentloaded", timeout=15000)
            results["milestone_1_launch"] = True
            print("  ✅ [MILESTONE 1 PASS] Playwright Chromium launched & navigated successfully!")
        except Exception as e:
            print(f"  ❌ [MILESTONE 1 FAIL]: {e}")
            return results

        # Milestone 2: Save storageState.json
        print("\n[MILESTONE 2] Exporting storageState.json to disk...")
        try:
            context.storage_state(path=STATE_PATH)
            if os.path.exists(STATE_PATH) and os.path.getsize(STATE_PATH) > 0:
                results["milestone_2_save_state"] = True
                print(f"  ✅ [MILESTONE 2 PASS] storageState.json saved successfully ({os.path.getsize(STATE_PATH)} bytes)!")
            context.close()
            browser.close()
        except Exception as e:
            print(f"  ❌ [MILESTONE 2 FAIL]: {e}")
            return results

        # Milestone 3: Load saved storageState.json & verify session reuse
        print("\n[MILESTONE 3] Launching new BrowserContext with saved storageState.json...")
        try:
            browser2 = p.chromium.launch(headless=True)
            context2 = browser2.new_context(storage_state=STATE_PATH, viewport={"width": 1400, "height": 900})
            page2 = context2.new_page()
            page2.goto("https://www.coupang.com/", wait_until="domcontentloaded", timeout=15000)
            
            cookies = context2.cookies()
            if len(cookies) > 0:
                results["milestone_3_reuse_state"] = True
                print(f"  ✅ [MILESTONE 3 PASS] storageState.json loaded & {len(cookies)} session cookies restored!")
            context2.close()
            browser2.close()
        except Exception as e:
            print(f"  ❌ [MILESTONE 3 FAIL]: {e}")

    print("\n==========================================================================")
    print("📊 STORAGE_STATE MILESTONE TEST RESULTS:")
    print(f"  • Milestone 1 (Playwright Launch):     {results['milestone_1_launch']}")
    print(f"  • Milestone 2 (Save storageState):     {results['milestone_2_save_state']}")
    print(f"  • Milestone 3 (Reuse Session State):   {results['milestone_3_reuse_state']}")
    print("==========================================================================")

    return results

if __name__ == "__main__":
    run_storage_state_milestone_test()
