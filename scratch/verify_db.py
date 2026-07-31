import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def verify_db():
    try:
        with open("morvix_shop_db.json", "r", encoding="utf-8") as f:
            db = json.load(f)
    except Exception as e:
        print(f"❌ morvix_shop_db.json 읽기 실패: {e}")
        return

    products = db.get("products", [])
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [morvix_shop_db.json 섹션별 최종 검증 보고]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📌 [DB 총 핫딜 상품 수량] : {len(products)}개")

    sec_today = [p for p in products if p.get("section") == "today_price"]
    sec_best = [p for p in products if p.get("section") == "best_seller"]

    print(f"  🔥 [오늘만 이 가격 (하루특가)] : {len(sec_today)}개")
    print(f"  🏆 [지금 많이 팔리는 BEST]     : {len(sec_best)}개")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print("\n[샘플 - 오늘만 이 가격 3개]")
    for p in sec_today[:3]:
        print(f"  • {p.get('name')} | {p.get('price'):,}원 ({p.get('discount_rate')})")

    print("\n[샘플 - 지금 많이 팔리는 BEST 3개]")
    for p in sec_best[:3]:
        print(f"  • {p.get('name')} | {p.get('price'):,}원 ({p.get('discount_rate')})")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    verify_db()
