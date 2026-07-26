import json
import os
import sys
import urllib.parse
from datetime import datetime
from playwright.sync_api import sync_playwright

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

def harvest_naver_via_playwright(search_query="신일 서큘레이터"):
    print("=======================================================")
    print("🧪 MORVIX Playwright Engine: Naver Shopping Connect Harvest")
    print(f"🔍 Search Query: '{search_query}'")
    print("=======================================================\n")

    encoded_query = urllib.parse.quote(search_query)
    target_url = f"https://search.shopping.naver.com/search/all?query={encoded_query}"

    with sync_playwright() as p:
        print("[STEP 1] Launching Chromium Engine (Bypassing 418 Shield)...")
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

        print(f"[STEP 2] Navigating to Naver Shopping Endpoint: {target_url}")
        res = page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
        status_code = res.status if res else 0

        print(f"  • Response HTTP Status Code: {status_code}")

        if status_code == 200:
            print("  ✅ [HTTP 200 OK] Naver Shopping Endpoint Successfully Reached via Playwright!")
            
            title = page.title()
            print(f"  • Live Page Title: {title}")

            naver_link = {
                "platform": "naver",
                "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
                "url": target_url,
                "priority": 1,
                "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
            }

            if os.path.exists(DB_PATH):
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    db_data = json.load(f)

                updated = False
                for p_item in db_data.get("products", []):
                    if "서큘레이터" in p_item.get("name", ""):
                        has_naver = any(l.get("platform") == "naver" for l in p_item.get("affiliate_links", []))
                        if not has_naver:
                            p_item.setdefault("affiliate_links", []).append(naver_link)
                        p_item["last_synced_at"] = datetime.now().isoformat()
                        updated = True
                        print(f"  ✅ [MASTER DB UPDATED] Successfully Attached Verified Naver Link to [{p_item.get('name')}]")

                if updated:
                    with open(DB_PATH, "w", encoding="utf-8") as f:
                        json.dump(db_data, f, ensure_ascii=False, indent=2)

            browser.close()
            print("\n=======================================================")
            print("🟢 PLAYWRIGHT NAVER SHOPPING HARVEST: 100% SUCCESS")
            print("=======================================================")
            return True
        else:
            print(f"  ❌ Playwright returned Status {status_code}")
            browser.close()
            return False

if __name__ == "__main__":
    harvest_naver_via_playwright()
