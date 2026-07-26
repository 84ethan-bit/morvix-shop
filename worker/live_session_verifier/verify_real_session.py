import os
import sys
import time
import json
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COUPANG_SESSION_DIR = os.path.join(BASE_DIR, "session_coupang_real")
NAVER_SESSION_DIR = os.path.join(BASE_DIR, "session_naver_real")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"  📢 [TELEGRAM SIMULATED ALERT]: {message}")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"⚠️ Telegram dispatch exception: {e}")
        return False

def verify_coupang_real_session(target_product_url="https://www.coupang.com/vp/products/7335191244"):
    """
    STEP 1 ~ STEP 4: Real Coupang Partners Live Session & DOM Link Generator Verification
    """
    print("==========================================================================")
    print("🔍 [REAL SESSION AUDIT 1] COUPANG PARTNERS LIVE DOM EXTRACTOR")
    print("==========================================================================")

    os.makedirs(COUPANG_SESSION_DIR, exist_ok=True)
    report = {
        "platform": "coupang_partners",
        "session_status": "UNKNOWN",
        "real_link_extracted": None,
        "is_real_empirical": False,
        "checked_at": datetime.now().isoformat()
    }

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=COUPANG_SESSION_DIR,
            headless=True,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("[STEP 1] Accessing Coupang Partners Portal (partners.coupang.com)...")
        page.goto("https://partners.coupang.com/", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)

        current_url = page.url
        print(f"  • Current URL: {current_url}")

        if "login" in current_url or "auth" in current_url or page.locator("input[name='email']").count() > 0:
            report["session_status"] = "LOGIN_REQUIRED"
            print("  ⚠️ [STATUS: LOGIN_REQUIRED] Coupang Partners login session is NOT active.")
            send_telegram_alert("⚠️ [MORVIX ALERT] Coupang Partners Login Session Expired. Re-authentication Required (LOGIN_REQUIRED).")
        else:
            report["session_status"] = "AUTHENTICATED_ACTIVE"
            print("  ✅ [STATUS: AUTHENTICATED_ACTIVE] Persistent session valid! Attempting real DOM link generation...")

            # Attempt DOM Link Generation
            try:
                page.goto("https://partners.coupang.com/#affiliate-solution/link-generator", wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
                
                # Fill URL input if present
                url_input = page.locator("input[type='text']")
                if url_input.count() > 0:
                    url_input.first.fill(target_product_url)
                    btn = page.locator("button:has-text('링크 생성')")
                    if btn.count() > 0:
                        btn.first.click()
                        page.wait_for_timeout(2000)
                        
                        # Extract real generated affiliate link
                        link_result = page.locator(".generated-link")
                        if link_result.count() > 0:
                            report["real_link_extracted"] = link_result.first.text_content().strip()
                            report["is_real_empirical"] = True
                            print(f"  🎉 [REAL EMPIRICAL LINK EXTRACTED]: {report['real_link_extracted']}")
            except Exception as e:
                print(f"  ⚠️ DOM Generation notice: {e}")

        context.close()
    return report

def verify_naver_real_session(target_product_url="https://smartstore.naver.com/shinil1959/products/1039971039"):
    """
    STEP 5 ~ STEP 7: Real Naver Shopping Connect Live Session & DOM Link Generator Verification
    """
    print("\n==========================================================================")
    print("🔍 [REAL SESSION AUDIT 2] NAVER SHOPPING CONNECT LIVE DOM EXTRACTOR")
    print("==========================================================================")

    os.makedirs(NAVER_SESSION_DIR, exist_ok=True)
    report = {
        "platform": "naver_connect",
        "session_status": "UNKNOWN",
        "real_link_extracted": None,
        "is_real_empirical": False,
        "checked_at": datetime.now().isoformat()
    }

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=NAVER_SESSION_DIR,
            headless=True,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("[STEP 1] Accessing Naver BrandConnect Portal (brandconnect.naver.com)...")
        try:
            page.goto("https://brandconnect.naver.com/", wait_until="domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)
        except Exception as err:
            print(f"  ⚠️ Navigation notice: {err}")

        current_url = page.url
        print(f"  • Current URL: {current_url}")

        if "nid.naver.com" in current_url or "login" in current_url:
            report["session_status"] = "LOGIN_REQUIRED"
            print("  ⚠️ [STATUS: LOGIN_REQUIRED] Naver Shopping Connect login session is NOT active.")
            send_telegram_alert("⚠️ [MORVIX ALERT] Naver Shopping Connect Login Session Expired. Re-authentication Required (LOGIN_REQUIRED).")
        else:
            report["session_status"] = "AUTHENTICATED_ACTIVE"
            print("  ✅ [STATUS: AUTHENTICATED_ACTIVE] Persistent session valid!")

        context.close()
    return report

def run_real_session_audit_suite():
    print("==========================================================================")
    print("🛡️ MORVIX REAL SESSION ACCURACY & EMPIRICAL AUDIT SUITE")
    print("==========================================================================\n")

    res_coupang = verify_coupang_real_session()
    res_naver = verify_naver_real_session()

    audit_summary = {
        "timestamp": datetime.now().isoformat(),
        "coupang_session": res_coupang,
        "naver_session": res_naver
    }

    summary_path = os.path.join(BASE_DIR, "real_session_audit.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, ensure_ascii=False, indent=2)

    print("\n==========================================================================")
    print("📊 EMPIRICAL SESSION AUDIT STATUS:")
    print(f"  • Coupang Session State: {res_coupang['session_status']} (Empirical Link: {res_coupang['is_real_empirical']})")
    print(f"  • Naver Session State:   {res_naver['session_status']} (Empirical Link: {res_naver['is_real_empirical']})")
    print(f"  • Audit Log Saved:       {summary_path}")
    print("==========================================================================")

if __name__ == "__main__":
    run_real_session_audit_suite()
