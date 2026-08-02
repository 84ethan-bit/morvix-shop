import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def categorize_title(title):
    t = title.lower()

    # 1. 🚗 차량용품 (Car)
    if any(k in t for k in [
        "차량", "콘솔박스", "팔걸이", "햇빛가리개", "복구왁스", "탈취제", "핸들커버", "차량용", "와이퍼", "세차"
    ]):
        return "car"

    # 2. 🏠 생활·주방 (Living & Kitchen) - Highest Priority for Home Appliances (e.g. 비데)
    if any(k in t for k in [
        "비데", "세제", "물티슈", "휴지", "키친타올", "행주", "롤행주", "냄비", "멀티팬", "포트",
        "주전자", "식세기", "식기세척기", "쿠션", "패드", "쿨매트", "베개", "소파", "테이프크리너",
        "세척볼", "거치대", "스탠드", "세정제", "제습제", "건전지", "충전기", "인덕션", "선풍기",
        "마스크", "락앤락", "보온병", "텀블러", "식기", "도마", "가위", "수세미", "지퍼백"
    ]):
        return "living"

    # 3. 👔 패션·뷰티 (Fashion & Beauty)
    if any(k in t for k in [
        "모자", "쿨토시", "토시", "팬티", "드로즈", "나시", "민소매", "잠옷", "팬츠", "바지", "양말",
        "스카프", "향수", "바디워시", "크림", "샴푸", "비누", "의류", "상하의", "세트", "화장품",
        "뷰티", "드라이어", "드라이시트", "수딩", "치약", "두피", "가방"
    ]):
        return "fashion"

    # 4. 💊 건강 (Health & Supplements)
    if any(k in t for k in [
        "영양제", "오메가3", "루테인", "매스틱", "알파시디", "유산균", "락토핏", "밀크씨슬", "효소",
        "다이어트", "블랙컷", "당플랜", "기억력", "캡슐", "정", "건강", "비타민"
    ]):
        return "health"

    # 5. Processed Food Exceptions (must be 'food', not 'fruit')
    if any(k in t for k in ["핫바", "토마토즙", "사과주스", "김치", "감자탕", "짜글이"]):
        return "food"

    # 6. 🍎 과일·신선 (Fruit & Fresh Produce) - INDEPENDENT NEW CATEGORY!
    if any(k in t for k in [
        "무화과", "복숭아", "토마토", "망고", "농산물", "깻잎", "햅쌀", "계란", "구운계란", "다진마늘",
        "버섯", "표고버섯", "고들빼기", "과일", "신선", "채소", "야채", "사과", "딸기", "포도", "감귤", "배"
    ]):
        return "fruit"

    # 7. 🥦 식품 (Processed Food, Meal Kits, Drinks, Meat)
    if any(k in t for k in [
        "삼겹", "치킨", "주스", "커피", "생수",
        "곱창", "쥐포", "두유", "캔디", "마늘", "김자반", "올리브오일", "콜드브루", "애사비",
        "장조림", "갈비", "쿠키", "혼쯔유", "바게트", "오징어", "치즈", "육수",
        "음료", "저당", "사이다", "가리비", "식품", "음식", "차", "디카페인", "아몬드"
    ]):
        return "food"

    return "living"

def run_fruit_remap():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🍎 ['과일·신선' 독립 카테고리 신설 및 128개 정밀 재분류 실행]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    cat_counts = {"fruit": 0, "food": 0, "living": 0, "car": 0, "fashion": 0, "health": 0}
    fruit_items = []

    for p in db.get("products", []):
        name = p.get("name", "")
        cat = categorize_title(name)
        p["category"] = cat
        cat_counts[cat] += 1

        if cat == "fruit":
            fruit_items.append(name)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print("📊 [7대 카테고리 정밀 분류 통계 결과]:")
    print(f"  • 🍎 과일·신선 (fruit)  : {cat_counts['fruit']}개 ⭐ [신설!]")
    print(f"  • 🥦 식품 (food)       : {cat_counts['food']}개")
    print(f"  • 🏠 생활·주방 (living) : {cat_counts['living']}개")
    print(f"  • 🚗 차량용품 (car)     : {cat_counts['car']}개")
    print(f"  • 👔 패션·뷰티 (fashion): {cat_counts['fashion']}개")
    print(f"  • 💊 건강 (health)     : {cat_counts['health']}개")
    print("  ───────────────────────────────────")
    print(f"  • 📦 전체 (all)         : {sum(cat_counts.values())}개")

    print(f"\n🍎 [과일·신선(fruit) 카테고리 독립 매핑 품목 명단 ({len(fruit_items)}개)]:")
    for idx, f_name in enumerate(fruit_items, 1):
        print(f"  #{idx:02d} | {f_name[:55]}")

    print("\n✅ morvix_shop_db.json 과일·신선 카테고리 분리 반영 완수! (NO GIT PUSH)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    run_fruit_remap()
