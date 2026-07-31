import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def verify_db():
    try:
        with open("morvix_shop_db.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ morvix_shop_db.json 읽기 실패: {e}")
        return

    deals = data.get("deals", [])
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [morvix_shop_db.json 최종 검증 보고]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📌 [DB 저장된 총 핫딜 상품 수량] : {len(deals)}개")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for idx, d in enumerate(deals[:15], 1):
        print(f"  #{idx:02d} [{d.get('name')}] | {d.get('price'):,}원 | {d.get('discount_rate')} | 링크: {d.get('share_link')}")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    verify_db()
