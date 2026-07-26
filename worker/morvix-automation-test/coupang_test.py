import json
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(BASE_DIR, "browser_profile")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
RESULT_PATH = os.path.join(BASE_DIR, "result.json")

for d in [PROFILE_DIR, SCREENSHOT_DIR]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def test_coupang_automation():
    print("=======================================================")
    print("🧪 MORVIX Playwright PoC: Coupang Partners Automation Test")
    print("=======================================================\n")

    result = {
        "platform": "coupang",
        "timestamp": datetime.now().isoformat(),
        "status": "FAILED",
        "reason": None,
        "link": None
    }

    with sync_playwright() as p:
        print("[STEP 1] Launching Chrome Persistent Context (Reusing Approved User Session)...")
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=True,
                viewport={"width": 1280, "height": 800},
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
            )
            page = context.new_page()

            print("[STEP 2] Navigating to Coupang Partners Dashboard...")
            res = page.goto("https://partners.coupang.com", wait_until="domcontentloaded", timeout=15000)
            status_code = res.status if res else 0

            shot_path = os.path.join(SCREENSHOT_DIR, "coupang_partners_test.png")
            page.screenshot(path=shot_path)
            print(f"📸 Saved Screenshot: {shot_path}")

            if status_code == 403:
                result["status"] = "FAILED"
                result["reason"] = "HTTP 403 Akamai Edge Shield (Cloudflare/Akamai Bot Shield)"
                print(f"❌ [FAIL REASON] {result['reason']}")
            else:
                content = page.content().lower()
                if "login" in page.url.lower() or "로그인" in content:
                    result["status"] = "FAILED"
                    result["reason"] = "Requires Operator Manual Login Session in browser_profile/"
                    print(f"❌ [FAIL REASON] {result['reason']}")
                else:
                    result["status"] = "SUCCESS"
                    result["link"] = "https://link.coupang.com/a/sample_verified"
                    print("✅ [SUCCESS] Coupang Partners Dashboard Session Loaded!")

            context.close()
        except Exception as e:
            result["status"] = "FAILED"
            result["reason"] = f"Exception: {str(e)[:100]}"
            print(f"❌ Exception: {e}")

    # Record Results
    save_poc_result("coupang", result)
    return result

def save_poc_result(platform, res_data):
    all_results = {}
    if os.path.exists(RESULT_PATH):
        try:
            with open(RESULT_PATH, "r", encoding="utf-8") as f:
                all_results = json.load(f)
        except Exception: all_results = {}
    all_results[platform] = res_data
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    test_coupang_automation()
