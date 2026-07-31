import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def parse_next_f_from_dump():
    try:
        with open("scratch/after_click.html", "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        print(f"❌ after_click.html 읽기 실패: {e}")
        return

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [대표님 지정] __next_f 스트리밍 데이터 전수 파싱 실측 리포트")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # self.__next_f.push(...) 청크 추출
    chunks = re.findall(r'self\.__next_f\.push\((.*?)\)</script>', html, re.DOTALL)
    print(f"📌 [__next_f 청크 발견 수량] : {len(chunks)}개")

    full_payload = "".join(chunks)
    print(f"📌 [전체 스트리밍 데이터 크기] : {len(full_payload):,} bytes")

    # 상품 정보 패턴 수색 (가격 + 원/할인율/상품명)
    # price/title 패턴 추출 시도
    titles = re.findall(r'"title"\s*:\s*"([^"]+)"', full_payload)
    prices = re.findall(r'"price"\s*:\s*(\d+)', full_payload)
    discount_rates = re.findall(r'"discountRate"\s*:\s*(\d+)', full_payload)
    product_ids = re.findall(r'"productId"\s*:\s*"?([A-Za-z0-9_-]+)"?', full_payload)

    unique_titles = list(dict.fromkeys(titles))

    print(f"📌 [추출된 상품명 수량]     : 총 {len(titles)}개 (중복 제거 후: {len(unique_titles)}개)")
    print(f"📌 [추출된 가격 수량]       : 총 {len(prices)}개")
    print(f"📌 [추출된 할인율 수량]     : 총 {len(discount_rates)}개")
    print(f"📌 [추출된 Product ID 수량] : 총 {len(product_ids)}개")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if unique_titles:
        print("📌 [__next_f 파싱 추출 상품 샘플 10개]:")
        for idx, title in enumerate(unique_titles[:10], 1):
            p = prices[idx-1] if idx-1 < len(prices) else 'N/A'
            d = discount_rates[idx-1] if idx-1 < len(discount_rates) else 'N/A'
            print(f"  #{idx:02d} {title[:35]} | 가격: {p}원 | 할인율: {d}%")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    parse_next_f_from_dump()
