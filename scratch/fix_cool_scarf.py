import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def fix_cool_scarf():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 [아쿠아 쿨 스카프] 토스 실측가 5,900원 / 정가 14,500원 / 59% 수복")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    target_product = None
    for p in db.get("products", []):
        if "아쿠아 쿨 스카프" in p.get("name", ""):
            p["price"] = 5900
            p["original_price"] = 14500
            p["discount_rate"] = "59%"
            p["subtitle"] = "토스 파트너 특가 59% 적용"
            target_product = p
            break

    if target_product:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print("✅ [수복 완료] 아쿠아 쿨 스카프 morvix_shop_db.json 갱신 완료!")
        print("📄 갱신된 raw JSON dict:")
        print(json.dumps(target_product, ensure_ascii=False, indent=2))
    else:
        print("❌ DB에서 '아쿠아 쿨 스카프' 상품을 찾지 못함")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    fix_cool_scarf()
