import sys, os, time, re, requests, json
from playwright.sync_api import sync_playwright
from urllib.parse import quote

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

def harvest_real_product_image_playwright(product_name):
    print("=======================================================")
    print(f"🔍 HARVESTING REAL PRODUCT IMAGE FOR: '{product_name}'")
    print("=======================================================")

    clean_query = re.sub(r'\[.*?\]', '', product_name).strip()
    encoded_query = quote(clean_query)
    url = f"https://search.shopping.naver.com/search/all?query={encoded_query}"

    img_url = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(1000)

            # Find product item img tag
            img_elem = page.query_selector("img[src*='shopping-phinf.pstatic.net']") or page.query_selector("img[src*='pstatic.net']")
            if img_elem:
                src = img_elem.get_attribute("src")
                if src:
                    img_url = re.sub(r'type=\w\d+', 'type=f600', src)
                    print(f"✅ Real Product Photo Harvested via Playwright Chromium:\n   {img_url}")
            browser.close()
    except Exception as e:
        print(f"⚠️ Playwright harvest error: {e}")

    return img_url

def update_product_with_real_image():
    if not os.path.exists(DB_PATH): return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    products = db_data.get("products", [])
    if not products: return

    updated_count = 0
    for p in products:
        real_img = harvest_real_product_image_playwright(p.get("name", ""))
        if real_img:
            p["thumbnail"] = real_img
            p["image_status"] = "Verified_Real"
            updated_count += 1

    if updated_count > 0:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 Successfully updated {updated_count} products with REAL product photos!")

if __name__ == "__main__":
    update_product_with_real_image()
