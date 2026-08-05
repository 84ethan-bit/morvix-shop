import urllib.request
import json

url = "https://raw.githubusercontent.com/84ethan-bit/morvix-shop/main/morvix_shop_db.json"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    res = urllib.request.urlopen(req, timeout=10)
    if res.status == 200:
        data = json.loads(res.read().decode('utf-8'))
        print("Updated At:", data.get("updatedAt"))
        categories = data.get("categories", {})
        print("All count:", len(categories.get("전체", [])))
        print("Today count:", len(categories.get("오늘만 이가격", [])))
    else:
        print("Status:", res.status)
except Exception as e:
    print("Error:", e)
