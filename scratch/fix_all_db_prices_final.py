import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def fix_db_final():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🛠️ [morvix_shop_db.json 최종 무결성 전수 보정 스크립트]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    fixed_count = 0
    for p in db.get("products", []):
        name = p.get("name", "")

        # 1. 타이다이 상하의 세트
        if "타이다이" in name:
            p["price"] = 8850
            p["original_price"] = 0
            p["discount_rate"] = "73%"
            p["subtitle"] = "토스 파트너 특가 73% 적용"
            fixed_count += 1
            print("✅ [타이다이 세트 수복] price -> 8,850원 (73% OFF)")

        # 2. 순수스토리 알파시디
        elif "알파시디" in name:
            p["price"] = 27900
            p["original_price"] = 0
            p["discount_rate"] = "92%"
            p["subtitle"] = "토스 파트너 특가 92% 적용"
            fixed_count += 1
            print("✅ [알파시디 수복] price -> 27,900원 (92% OFF)")

        # 3. 올바른 다이어트 블랙컷 커피맛
        elif "블랙컷" in name:
            p["price"] = 19800
            p["original_price"] = 0
            p["discount_rate"] = "60%"
            fixed_count += 1
            print("✅ [블랙컷 커피맛 수복] price -> 19,800원 (60% OFF)")

        # 4. 삼육두유 60개
        elif "삼육두유" in name:
            p["price"] = 35890
            p["original_price"] = 0
            p["discount_rate"] = "28%"
            fixed_count += 1
            print("✅ [삼육두유 수복] price -> 35,890원 (28% OFF)")

        # 5. 종근당 락토핏 골드 120포
        elif "락토핏" in name:
            p["price"] = 60628
            p["original_price"] = 0
            p["discount_rate"] = "68%"
            fixed_count += 1
            print("✅ [종근당 락토핏 수복] price -> 60,628원 (68% OFF)")

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"\n💾 총 {fixed_count}개 핵심 상품 가격 보정 완료 및 morvix_shop_db.json 저장 완수!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    fix_db_final()
