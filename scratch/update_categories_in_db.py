import json
import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def categorize_title(title):
    t = title.lower()
    
    # 1. 🥦 식품 (Food)
    if any(k in t for k in [
        "김치", "감자탕", "짜글이", "삼겹", "치킨", "주스", "커피", "망고", "복숭아", "생수", "무화과",
        "곱창", "쥐포", "사과", "두유", "캔디", "마늘", "김자반", "올리브오일", "콜드브루", "애사비",
        "장조림", "갈비", "쿠키", "혼쯔유", "바게트", "오징어", "토마토", "유정란", "치즈", "육수",
        "음료", "저당", "사이다", "핫바", "가리비", "식품", "음식", "과일", "차", "디카페인"
    ]):
        return "food"

    # 2. 🚗 차량용품 (Car)
    if any(k in t for k in [
        "차량", "콘솔박스", "팔걸이", "햇빛가리개", "복구왁스", "탈취제", "핸들커버", "차량용", "와이퍼", "세차"
    ]):
        return "car"

    # 3. 👔 패션·뷰티 (Fashion & Beauty)
    if any(k in t for k in [
        "팬티", "드로즈", "나시", "민소매", "잠옷", "팬츠", "바지", "양말", "스카프", "향수", "바디워시",
        "크림", "샴푸", "비누", "쿨토시", "토시", "모자", "의류", "상하의", "세트", "화장품", "뷰티",
        "드라이어", "헤어", "피죤", "드라이시트", "수딩", "치약", "두피"
    ]):
        return "fashion"

    # 4. 💊 건강 (Health & Supplements)
    if any(k in t for k in [
        "영양제", "오메가3", "루테인", "매스틱", "알파시디", "유산균", "락토핏", "밀크씨슬", "효소",
        "다이어트", "블랙컷", "당플랜", "기억력", "캡슐", "정", "박스", "포", "건강", "비타민"
    ]):
        return "health"

    # 5. 🏠 생활·주방 (Living & Kitchen - Default fallback)
    return "living"

def run_categorization():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🏷️ [128개 전체 상품 5대 대표 카테고리 1:1 자동 분류]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    cat_counts = {"food": 0, "living": 0, "car": 0, "fashion": 0, "health": 0}

    for p in db.get("products", []):
        cat = categorize_title(p.get("name", ""))
        p["category"] = cat
        cat_counts[cat] += 1

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("📊 카테고리별 분류 통계:")
    print(f"  • 🥦 식품 (food)       : {cat_counts['food']}개")
    print(f"  • 🏠 생활·주방 (living) : {cat_counts['living']}개")
    print(f"  • 🚗 차량용품 (car)     : {cat_counts['car']}개")
    print(f"  • 👔 패션·뷰티 (fashion): {cat_counts['fashion']}개")
    print(f"  • 💊 건강 (health)     : {cat_counts['health']}개")
    print(f"  ───────────────────────────────────")
    print(f"  • 📦 전체 (all)         : {sum(cat_counts.values())}개")

    print("\n✅ morvix_shop_db.json 카테고리 분류 업데이트 완료! (NO GIT PUSH)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    run_categorization()
