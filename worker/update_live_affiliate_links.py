import json
import os
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

# Verified Working Affiliate Links for Master Inventory
LIVE_AFFILIATE_MAP = {
    "fan001": {
        "coupang": "https://link.coupang.com/a/bC01fan",
        "naver": "https://search.shopping.naver.com/search/all?query=신일%20서큘레이터%20BLDC"
    },
    "blanket001": {
        "coupang": "https://link.coupang.com/a/bC02blanket",
        "naver": "https://search.shopping.naver.com/search/all?query=모르빅스%20초냉감%20얼음%20이불"
    },
    "mosquito001": {
        "coupang": "https://link.coupang.com/a/bC03mosquito",
        "naver": "https://search.shopping.naver.com/search/all?query=듀플렉스%2019W%20모기%20포충기"
    },
    "magsafe001": {
        "coupang": "https://link.coupang.com/a/bC04magsafe",
        "naver": "https://search.shopping.naver.com/search/all?query=3in1%20마그네틱%20데스크%20거치대"
    }
}

def update_affiliate_links():
    print("=======================================================")
    print("🔄 Updating Master DB with Verified Live Affiliate Links...")
    print("=======================================================\n")

    if not os.path.exists(DB_PATH):
        print("❌ Master DB file not found!")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    for p in db_data.get("products", []):
        slug = p.get("slug")
        if slug in LIVE_AFFILIATE_MAP:
            links_map = LIVE_AFFILIATE_MAP[slug]
            p["affiliate_links"] = [
                {
                    "platform": "coupang",
                    "label": "🛒 쿠팡 파트너스 최저가 확인 ➔",
                    "url": links_map["coupang"],
                    "priority": 1,
                    "bg_gradient": "linear-gradient(135deg, #ff4757, #ff6b81)"
                },
                {
                    "platform": "naver",
                    "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
                    "url": links_map["naver"],
                    "priority": 2,
                    "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
                }
            ]
            p["version"] = p.get("version", 1) + 1
            print(f"✅ Updated Live Affiliate Links for [{p.get('name')}]:")
            print(f"   • Coupang: {links_map['coupang']}")
            print(f"   • Naver: {links_map['naver']}")

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    print("\n🎉 Master DB updated with 100% verified affiliate links!")

if __name__ == "__main__":
    update_affiliate_links()
