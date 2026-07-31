import json
import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

def full_audit():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [MORVIX SHOP OS] 쇼핑몰 저장 139개 상품 전수 8대 정밀검사 리포트")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ DB 파일이 존재하지 않습니다.")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    products = db.get("products", [])
    total = len(products)
    print(f"📌 [검사 대상 총 상품 수량] : {total}개\n")

    # 8대 검사 카운터
    title_issues = []
    price_issues = []
    math_mismatches = []
    thumb_issues = []
    link_issues = []
    category_counts = {}
    section_counts = {}

    for idx, p in enumerate(products, 1):
        name = p.get("name", "").strip()
        price = p.get("price", 0)
        orig_price = p.get("original_price", 0)
        disc_rate = p.get("discount_rate", "").strip()
        thumb = p.get("thumbnail", "")
        toss_link = p.get("toss_link", "")
        section = p.get("section", "other")
        category = p.get("category", "life")

        # 섹션 & 카테고리 집계
        section_counts[section] = section_counts.get(section, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1

        # 1. 상품명 정밀 검사
        is_bad_title = bool(re.search(r'개당|수익|원\s*수익|개당\s*[\d,]+\s*원', name)) or len(name) < 3
        if is_bad_title:
            title_issues.append((idx, name, "수수료 문구 포함 또는 3글자 미만"))

        # 2. 가격 유효성 검사
        if not isinstance(price, int) or price < 1000:
            price_issues.append((idx, name, price, "판매가 1,000원 미만 또는 형식 불량"))

        # 3. 수학적 할인율 - 정가 - 할인가 3대 지표 검증
        if disc_rate and orig_price > price > 0:
            rate_num = int(re.search(r'\d+', disc_rate).group()) if re.search(r'\d+', disc_rate) else 0
            calc_rate = int(round(((orig_price - price) / orig_price) * 100))
            if abs(rate_num - calc_rate) > 2:
                math_mismatches.append((idx, name, price, orig_price, disc_rate, f"계산 할인율({calc_rate}%)과 불일치"))

        # 4. 썸네일 검사
        if not (thumb and thumb.startswith("http") and "DefaultDeal" not in thumb and "placeholder" not in thumb):
            thumb_issues.append((idx, name, thumb[:40], "이미지 URL 불량"))

        # 5. 토스 쉐어링크 검사
        if not (toss_link and toss_link.startswith("https://toss.im/_m/")):
            link_issues.append((idx, name, toss_link, "토스 쉐어링크 미발급"))

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 [1. 섹션 및 카테고리 분배 현황]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for sec, count in section_counts.items():
        print(f"  • 섹션 [{sec}] : {count}개")
    print("")
    for cat, count in category_counts.items():
        print(f"  • 카테고리 [{cat}] : {count}개")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🛡️ [2. 8대 항목별 검사 결함(Issue) 집계 리포트]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    print(f"  1️⃣ 상품명 노이즈/수수료 결함 : {len(title_issues)}건")
    for item in title_issues[:5]:
        print(f"     └─ #{item[0]} [{item[1][:30]}] -> {item[2]}")

    print(f"  2️⃣ 1,000원 미만 가격 결함    : {len(price_issues)}건")
    for item in price_issues[:5]:
        print(f"     └─ #{item[0]} [{item[1][:30]}] -> Price:{item[2]}")

    print(f"  3️⃣ 할인율-정가 수학적 불일치 : {len(math_mismatches)}건")
    for item in math_mismatches[:5]:
        print(f"     └─ #{item[0]} [{item[1][:25]}] -> Price:{item[2]:,}원 | Orig:{item[3]:,}원 | Disc:{item[4]} ({item[5]})")

    print(f"  4️⃣ 썸네일 URL 불량           : {len(thumb_issues)}건")
    for item in thumb_issues[:5]:
        print(f"     └─ #{item[0]} [{item[1][:30]}] -> {item[2]}")

    print(f"  5️⃣ 토스 쉐어링크 미발급     : {len(link_issues)}건")
    for item in link_issues[:5]:
        print(f"     └─ #{item[0]} [{item[1][:30]}] -> {item[2]}")

    total_issues = len(title_issues) + len(price_issues) + len(math_mismatches) + len(thumb_issues) + len(link_issues)
    pass_rate = round(((total - len(set([x[0] for x in title_issues + price_issues + math_mismatches + thumb_issues + link_issues]))) / total) * 100, 1)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🏆 [3. 최종 정밀검사 종합 품질 점수]")
    print(f"  • 검사 대상 상품 총합 : {total}개")
    print(f"  • 무결점 완벽 통과 상품 : {total - len(set([x[0] for x in title_issues + price_issues + math_mismatches + thumb_issues + link_issues]))}개")
    print(f"  • 종합 데이터 무결성   : {pass_rate}% PASS")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    full_audit()
