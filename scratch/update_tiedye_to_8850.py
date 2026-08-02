import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def update_tiedye_price():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 [타이다이 상하의 세트] 토스 실제 표기가격 8,850원으로 1:1 수복")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    target_product = None
    for p in db.get("products", []):
        if "타이다이" in p.get("name", ""):
            p["price"] = 8850
            p["original_price"] = 0
            p["discount_rate"] = "73%"
            p["subtitle"] = "토스 파트너 특가 73% 적용"
            target_product = p
            break

    if target_product:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print("✅ [수복 완료] 로컬 morvix_shop_db.json 갱신 완료!")
        print("📄 갱신된 raw JSON dict:")
        print(json.dumps(target_product, ensure_ascii=False, indent=2))
    else:
        print("❌ DB에서 '타이다이' 상품을 찾지 못함")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    update_tiedye_price()
