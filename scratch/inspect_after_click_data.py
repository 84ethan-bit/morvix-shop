import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def inspect_html_next_data():
    try:
        with open("scratch/after_click.html", "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        print(f"❌ 읽기 실패: {e}")
        return

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [after_click.html 정밀 파싱 계측 리포트]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 1. self.__next_f.push 내용물 조사
    push_matches = re.findall(r'self\.__next_f\.push\((.*?)\);?</script>', html, re.DOTALL)
    print(f"📌 [self.__next_f.push 수량] : {len(push_matches)}개")

    # 2. HTML 내부에 등장하는 상품 카드 title 추출
    # alt 또는 aria-label 또는 innerText 패턴
    aria_labels = re.findall(r'aria-label="([^"]+)"', html)
    print(f"📌 [aria-label 기반 덤프 문장 수] : {len(aria_labels)}개")

    titles = [a for a in aria_labels if len(a) > 5 and not a.startswith("메뉴") and not a.startswith("실 지급액")]
    unique_titles = list(dict.fromkeys(titles))

    print(f"📌 [덤프 HTML 내 실제 상품명 수]  : 총 {len(titles)}개 (중복 제외: {len(unique_titles)}개)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if unique_titles:
        print("📌 [덤프 HTML 내 발견된 상품 샘플 10개]:")
        for idx, t in enumerate(unique_titles[:10], 1):
            print(f"  #{idx:02d} {t[:40]}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    inspect_html_next_data()
