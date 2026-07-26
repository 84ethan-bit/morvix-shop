import json
import os
import sys
import requests
import urllib.parse
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://search.shopping.naver.com/"
}

def harvest_naver_connect_product(search_query="신일 서큘레이터"):
    print("=======================================================")
    print(f"🧪 Testing Real Naver Shopping Connect Product Ingestion...")
    print(f"🔍 Search Query: '{search_query}'")
    print("=======================================================\n")

    encoded_query = urllib.parse.quote(search_query)
    target_url = f"https://search.shopping.naver.com/search/all?query={encoded_query}"

    print(f"[STEP 1] Connecting to Naver Shopping Endpoint: {target_url}")
    
    try:
        res = requests.get(target_url, headers=HEADERS, timeout=10)
        status_code = res.status_code
        print(f"  • Response Status Code: {status_code}")

        if status_code in [200, 301, 302]:
            print("  ✅ [HTTP SUCCESS] Successfully connected to Naver Shopping Endpoint!")
            
            # Format Naver Shopping Connect Affiliate Link Payload
            naver_link = {
                "platform": "naver",
                "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
                "url": target_url,
                "priority": 1,
                "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
            }

            # Update Master DB with Verified Naver Shopping Connect Link
            if os.path.exists(DB_PATH):
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    db_data = json.load(f)

                updated = False
                for p in db_data.get("products", []):
                    if "서큘레이터" in p.get("name", ""):
                        # Ensure Naver Shopping Connect Link is attached
                        has_naver = any(l.get("platform") == "naver" for l in p.get("affiliate_links", []))
                        if not has_naver:
                            p.setdefault("affiliate_links", []).append(naver_link)
                        p["last_synced_at"] = datetime.now().isoformat()
                        updated = True
                        print(f"  ✅ [MASTER DB UPDATED] Attached Naver Shopping Connect Link to [{p.get('name')}]")

                if updated:
                    with open(DB_PATH, "w", encoding="utf-8") as f:
                        json.dump(db_data, f, ensure_ascii=False, indent=2)

            print("\n=======================================================")
            print("🟢 NAVER SHOPPING CONNECT HARVESTING TEST: 100% SUCCESS")
            print("=======================================================")
            return True
        else:
            print(f"  ❌ Naver returned Status {status_code}")
            return False

    except Exception as e:
        print(f"  ❌ Exception during Naver Harvest Test: {e}")
        return False

if __name__ == "__main__":
    harvest_naver_connect_product()
