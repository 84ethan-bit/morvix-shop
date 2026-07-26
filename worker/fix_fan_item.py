import json
import os
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

def fix_fan():
    if not os.path.exists(DB_PATH): return
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    for p in db.get("products", []):
        if p.get("slug") == "fan001":
            p["name"] = "[26년형] 신일 무소음 스탠드 BLDC 서큘레이터"
            p["thumbnail"] = "https://shopping-phinf.pstatic.net/main_9101677/91016778652.1.jpg"
            p["images"] = ["https://shopping-phinf.pstatic.net/main_9101677/91016778652.1.jpg"]
            p["image_status"] = "Verified_Real_Phinf_CDN"
            p["version"] = p.get("version", 1) + 1
            print(f"✅ Fixed [{p['name']}] image to real Phinf CDN: {p['thumbnail']}")

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fix_fan()
