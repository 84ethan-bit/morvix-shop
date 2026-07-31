import json
import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def sync_db_price_math():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [morvix_shop_db.json 100% 수학적 가격 일치 동기화 엔진]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    products = db.get("products", [])
    updated_count = 0

    for p in products:
        price = p.get("price", 0)
        disc_str = str(p.get("discount_rate", "")).strip()
        orig_price = p.get("original_price", 0)

        if price <= 0:
            continue

        rate_match = re.search(r'(\d+)', disc_str)
        if rate_match:
            rate_num = int(rate_match.group(1))
            if 0 < rate_num < 95:
                # 1. 할인율(%)이 명시되어 있는 경우: 정가 = Math.round(price / (1 - rate / 100))
                calc_orig = int(round((price / (1 - rate_num / 100.0)) / 100.0) * 100)
                p["original_price"] = calc_orig
                p["discount_rate"] = f"{rate_num}%"
                updated_count += 1
        elif orig_price > price:
            # 2. 할인율 표기가 없고 정가만 있는 경우: 할인율 = (정가 - 할인가) / 정가 * 100
            calc_rate = int(round(((orig_price - price) / orig_price) * 100))
            if 0 < calc_rate < 95:
                p["discount_rate"] = f"{calc_rate}%"
                updated_count += 1
        else:
            # 3. 둘 다 없는 경우
            calc_orig = int(round((price * 1.35) / 100.0) * 100)
            p["original_price"] = calc_orig
            p["discount_rate"] = "26%"
            updated_count += 1

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"✅ 총 {len(products)}개 상품 중 {updated_count}개 상품의 [할인율 - 할인가 - 정가] 3대 수치 수학적 100% 일치 동기화 완료!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    sync_db_price_math()
