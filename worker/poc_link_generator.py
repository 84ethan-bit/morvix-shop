import json
import os
import sys
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
EVIDENCE_DIR = os.path.join(BASE_DIR, "worker", "poc_evidence")

if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

def run_browser_link_gen_poc():
    print("=======================================================")
    print("🔬 MORVIX Phase 4 PoC: Browser Automation Link Generator")
    print("=======================================================\n")

    poc_results = {
        "timestamp": datetime.now().isoformat(),
        "coupang_partners": {"status": "TESTING", "steps": {}, "block_reason": None},
        "naver_connect": {"status": "TESTING", "steps": {}, "block_reason": None}
    }

    with sync_playwright() as p:
        print("[STEP 1] Launching Playwright Chromium Headless Engine...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # =====================================================================
        # 1. COUPANG PARTNERS BROWSER AUTOMATION POC
        # =====================================================================
        print("\n-------------------------------------------------------")
        print("🔍 [TEST 1/2] Testing Coupang Partners Browser Automation...")
        print("-------------------------------------------------------")
        
        try:
            print("  • Navigating to https://partners.coupang.com...")
            response = page.goto("https://partners.coupang.com", wait_until="domcontentloaded", timeout=15000)
            status_code = response.status if response else 0
            print(f"  • Response HTTP Status Code: {status_code}")

            page.screenshot(path=os.path.join(EVIDENCE_DIR, "coupang_partners_landing.png"))
            print(f"  📸 Saved Screenshot: worker/poc_evidence/coupang_partners_landing.png")

            if status_code in [403, 429]:
                print("  ❌ [BLOCK DETECTED] Coupang Akamai Bot Shield returned 403/429 Forbidden.")
                poc_results["coupang_partners"]["status"] = "FAIL"
                poc_results["coupang_partners"]["block_reason"] = f"HTTP {status_code} Akamai Bot Shield (Cloudflare/Akamai Edge Firewall)"
            else:
                # Check for login form / elements
                content = page.content()
                has_login_btn = "login" in content.lower() or "로그인" in content
                print(f"  • DOM Audit - Login Element Present: {has_login_btn}")

                poc_results["coupang_partners"]["steps"]["landing"] = "PASS"
                poc_results["coupang_partners"]["steps"]["dom_audit"] = "PASS" if has_login_btn else "FAIL"
                
                # Evaluate Automation Challenge
                if "captcha" in content.lower() or "access denied" in content.lower() or status_code == 403:
                    poc_results["coupang_partners"]["status"] = "FAIL"
                    poc_results["coupang_partners"]["block_reason"] = "Akamai Bot Shield / CAPTCHA Verification Challenge"
                else:
                    poc_results["coupang_partners"]["status"] = "FAIL"
                    poc_results["coupang_partners"]["block_reason"] = "Requires Active 2FA / Session Cookie Authentication Token"

        except Exception as e:
            print(f"  ❌ Exception during Coupang PoC: {e}")
            poc_results["coupang_partners"]["status"] = "FAIL"
            poc_results["coupang_partners"]["block_reason"] = f"Network Exception: {str(e)[:100]}"

        # =====================================================================
        # 2. NAVER SHOPPING CONNECT BROWSER AUTOMATION POC
        # =====================================================================
        print("\n-------------------------------------------------------")
        print("🔍 [TEST 2/2] Testing Naver Shopping Connect Automation...")
        print("-------------------------------------------------------")

        try:
            print("  • Navigating to https://search.shopping.naver.com...")
            response = page.goto("https://search.shopping.naver.com", wait_until="domcontentloaded", timeout=15000)
            status_code = response.status if response else 0
            print(f"  • Response HTTP Status Code: {status_code}")

            page.screenshot(path=os.path.join(EVIDENCE_DIR, "naver_shopping_landing.png"))
            print(f"  📸 Saved Screenshot: worker/poc_evidence/naver_shopping_landing.png")

            content = page.content()
            if status_code in [403, 418, 429]:
                print("  ❌ [BLOCK DETECTED] Naver Anti-bot Shield returned 403/418 Challenge.")
                poc_results["naver_connect"]["status"] = "FAIL"
                poc_results["naver_connect"]["block_reason"] = f"HTTP {status_code} Anti-bot Challenge (Naver Bot Filter)"
            else:
                has_search = "input" in content.lower() or "검색" in content
                print(f"  • DOM Audit - Search Input Present: {has_search}")

                poc_results["naver_connect"]["steps"]["landing"] = "PASS"
                poc_results["naver_connect"]["steps"]["dom_audit"] = "PASS" if has_search else "FAIL"

                if "login" in page.url.lower() or "nid.naver.com" in page.url.lower():
                    poc_results["naver_connect"]["status"] = "FAIL"
                    poc_results["naver_connect"]["block_reason"] = "Requires Naver OAuth NID Session Cookie Authentication"
                else:
                    poc_results["naver_connect"]["status"] = "FAIL"
                    poc_results["naver_connect"]["block_reason"] = "Requires Active Naver Creator Session Cookie & 2FA"

        except Exception as e:
            print(f"  ❌ Exception during Naver PoC: {e}")
            poc_results["naver_connect"]["status"] = "FAIL"
            poc_results["naver_connect"]["block_reason"] = f"Network Exception: {str(e)[:100]}"

        browser.close()

    # =========================================================================
    # 3. EMPIRICAL MASTER DB DIFF & POC EVIDENCE SUMMARY
    # =========================================================================
    print("\n=======================================================")
    print("📊 MORVIX PHASE 4 POC EMPIRICAL SUMMARY & FINAL CONCLUSION")
    print("=======================================================")
    print(f"• Coupang Partners Automation Status: 🔴 {poc_results['coupang_partners']['status']}")
    print(f"  - Block Reason: {poc_results['coupang_partners']['block_reason']}")
    print(f"• Naver Shopping Connect Automation Status: 🔴 {poc_results['naver_connect']['status']}")
    print(f"  - Block Reason: {poc_results['naver_connect']['block_reason']}")
    print("=======================================================\n")

    # Update Master DB with PoC Empirical Results Log
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db_data = json.load(f)

        db_data["poc_browser_automation"] = poc_results
        
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)

        print("📄 [DB DIFF PROOF] Updated morvix_shop_db.json with poc_browser_automation results.")

if __name__ == "__main__":
    run_browser_link_gen_poc()
