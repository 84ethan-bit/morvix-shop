import json
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def parse_dump():
    try:
        with open("scratch/window_next_f_dump.json", "r", encoding="utf-8") as f:
            dump_data = json.load(f)
    except Exception as e:
        print(f"❌ 읽기 실패: {e}")
        return

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔍 [window_next_f_dump.json 파싱] 항목 수: {len(dump_data)}개")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    all_text = json.dumps(dump_data, ensure_ascii=False)
    print(f"📌 [덤프 JSON 전체 텍스트 크기] : {len(all_text):,} bytes")

    # 1. 덤프 JSON 내부에서 발견되는 한글 텍스트 패턴 추출
    korean_texts = re.findall(r'[\uac00-\ud7a30-9a-zA-Z\s,\(\)\[\]/~%+._-]{5,60}', all_text)
    
    # 2. 상품명에 가까운 패턴 필터링
    product_candidates = []
    for txt in korean_texts:
        txt = txt.strip()
        if any(w in txt for w in ["특가", "세트", "개입", "개", "박스", "kg", "g", "ml", "L", "수익", "최저가", "팬티", "감자탕", "주스", "케이블"]):
            if not any(ex in txt for ex in ["설명 보기", "메뉴", "정산", "의견", "버튼", "레이아웃", "이용 약관", "개인정보"]):
                product_candidates.append(txt)

    unique_products = list(dict.fromkeys(product_candidates))
    print(f"📌 [덤프 JSON 내 탐색된 핫딜 상품 후보 수량] : {len(unique_products)}개")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for idx, p in enumerate(unique_products, 1):
        print(f"  #{idx:02d} {p}")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    parse_dump()
