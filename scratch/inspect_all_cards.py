import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def inspect_all_scripts_and_cards():
    try:
        with open("scratch/after_click.html", "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        print(f"❌ after_click.html 읽기 실패: {e}")
        return

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [대표님 지정] HTML 내 상품 카드 전수 파싱 실측 리포트")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 1. WideProductCard (오늘만 이 가격)
    wide_cards = re.findall(r'<div class="WideProductCard_card__kv9sto0">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
    print(f"📌 [WideProductCard (오늘만 이 가격) DOM 카드] : {len(wide_cards)}개")

    # 2. HorizontalProductCard (BEST)
    horiz_cards = re.findall(r'<div class="HorizontalProductCard_card__o9144n0">(.*?)</div>\s*</div>\s*</div>', html, re.DOTALL)
    print(f"📌 [HorizontalProductCard (BEST) DOM 카드]     : {len(horiz_cards)}개")

    # 3. HTML 내 모든 aria-label 상의 상품명 추출
    raw_labels = re.findall(r'aria-label="([^"]+)"', html)
    product_titles = [
        l for l in raw_labels
        if len(l) > 5
        and not any(k in l for k in ["메뉴", "설명 보기", "의견", "가이드", "열기"])
    ]
    unique_titles = list(dict.fromkeys(product_titles))

    print(f"📌 [DOM 덤프 내 렌더링된 총 상품 카드 수량]    : {len(product_titles)}개 (중복 제거: {len(unique_titles)}개)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for idx, title in enumerate(unique_titles, 1):
        print(f"  #{idx:02d} {title}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    inspect_all_scripts_and_cards()
