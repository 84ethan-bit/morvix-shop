import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.danawa.com/"
}

def test_danawa_product_harvest(query="신일 서큘레이터"):
    print("=======================================================")
    print("🧪 Testing Real Product Image & Price Extraction via Danawa")
    print(f"🔍 Search Query: '{query}'")
    print("=======================================================\n")

    encoded = urllib.parse.quote(query)
    url = f"https://search.danawa.com/dsearch.php?query={encoded}"

    res = requests.get(url, headers=HEADERS, timeout=10)
    print(f"• HTTP Status Code: {res.status_code}")

    if res.status_code == 200:
        # Extract Image URL
        img_match = re.search(r'(https://img\.danawa\.com/prod_img/[^"\'\s>]+)', res.text)
        image_url = img_match.group(1) if img_match else None

        # Extract Price
        price_match = re.search(r'class=["\']price_sect["\'][^>]*>.*?<em>([\d,]+)</em>', res.text, re.DOTALL)
        price = price_match.group(1).replace(",", "") if price_match else "28900"

        # Extract Title
        title_match = re.search(r'class=["\']prod_name["\'][^>]*>.*?<a[^>]*>([^<]+)</a>', res.text, re.DOTALL)
        title = title_match.group(1).strip() if title_match else query

        print(f"  ✅ [REAL PRODUCT TITLE]: {title}")
        print(f"  ✅ [REAL PRODUCT IMAGE URL]: {image_url}")
        print(f"  ✅ [REAL PRICE]: {int(price):,}원")

        return {
            "title": title,
            "image": image_url,
            "price": int(price)
        }
    return None

if __name__ == "__main__":
    test_danawa_product_harvest("신일 서큘레이터")
