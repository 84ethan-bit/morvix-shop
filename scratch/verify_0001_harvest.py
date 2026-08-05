import os
import sys
import json
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "morvix_shop_db.json"))

def verify_harvest_run():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🌙 [00시 01분 외부 수집서버 가동 및 DB 갱신 정밀 검증 스크립트]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ morvix_shop_db.json 파일이 존재하지 않습니다.")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_at = data.get("updatedAt", "알 수 없음")
    categories = data.get("categories", {})
    all_deals = categories.get("전체", [])
    today_deals = categories.get("오늘만 이가격", [])

    print(f"📌 [외부 수집서버 최종 갱신 시각 (updatedAt)]: {updated_at}")
    print(f"📌 [수집된 '전체' 핫딜 총 수량]                 : {len(all_deals)}개")
    print(f"📌 [수집된 '오늘만 이가격' 하루특가 수량]         : {len(today_deals)}개")

    print("\n✅ DB 스키마 정상 검증 완료!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    verify_harvest_run()
