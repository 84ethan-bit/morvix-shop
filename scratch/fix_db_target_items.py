import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def fix_db_items():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    updated = False
    for p in db.get("products", []):
        name = p.get("name", "")
        if "알파시디" in name:
            p["price"] = 27900
            p["original_price"] = 0
            p["discount_rate"] = "92%"
            updated = True
            print("✅ [알파시디 1:1 수복] price -> 27,900원 (92% OFF)")
        elif "타이다이" in name:
            p["price"] = 18900
            p["original_price"] = 0
            p["discount_rate"] = "73%"
            updated = True
            print("✅ [타이다이 1:1 수복] price -> 18,900원 (73% OFF)")

    if updated:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print("💾 DB 파일 저장 완료!")

if __name__ == "__main__":
    fix_db_items()
