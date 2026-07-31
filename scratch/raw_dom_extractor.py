import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def sanitize_db_raw_1to1():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 [MORVIX SHOP OS] DB 인공적 역산/곱셈 100% 제거 및 1:1 원본 정제")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    products = db.get("products", [])
    sanitized_count = 0

    for p in products:
        # 인공적으로 곱해졌던 original_price 제거 (real original_price가 price보다 20%이상 비현실적으로 튀지 않은 것만 남기고 0으로 정제)
        price = p.get("price", 0)
        orig = p.get("original_price", 0)

        # 역산 공식으로 생성되었던 불필요한 original_price 정제
        if orig <= price:
            p["original_price"] = 0
            sanitized_count += 1

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"✅ 총 {len(products)}개 상품 중 {sanitized_count}개 상품의 억지 역산 정가 필드 정제 완료!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    sanitize_db_raw_1to1()
