import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def print_local_db_tiedye():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [로컬 morvix_shop_db.json 파일 내 타이다이 상품 JSON 직접 검증]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ morvix_shop_db.json 파일이 존재하지 않습니다.")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    target = None
    for p in db.get("products", []):
        if "타이다이" in p.get("name", ""):
            target = p
            break

    if target:
        print("📄 [로컬 morvix_shop_db.json 텍스트 원본]:")
        print(json.dumps(target, ensure_ascii=False, indent=2))
        print("\n✅ 타이다이 할인가(price):", f"{target.get('price'):,}원")
        print("✅ 타이다이 정가(original_price):", f"{target.get('original_price'):,}원")
        print("✅ 타이다이 할인율(discount_rate):", target.get("discount_rate"))
    else:
        print("❌ DB 내 '타이다이' 상품을 찾을 수 없습니다.")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    print_local_db_tiedye()
