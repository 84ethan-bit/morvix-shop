import asyncio
import json
import os
import re
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def run_next_f_extraction():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 [Plan A] window.__next_f (세션 적용) 브라우저 메모리 정밀 파싱 테스트")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    use_session = os.path.exists(SESSION_PATH)
    print(f"🔑 세션 파일 존재: {use_session} ({SESSION_PATH})")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        ctx_kwargs = {
            "viewport": {"width": 1280, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR"
        }
        if use_session:
            ctx_kwargs["storage_state"] = SESSION_PATH

        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()

        print("📡 https://sharelink.toss.im/home 페이지 접속 중...")
        await page.goto("https://sharelink.toss.im/home", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. window.__next_f 객체 읽기
        next_f_raw = await page.evaluate("() => window.__next_f || []")
        print(f"📌 [window.__next_f 청크 개수] : {len(next_f_raw)}개")

        # 2. 모든 청크 텍스트 병합
        combined_text = ""
        for chunk in next_f_raw:
            if isinstance(chunk, list) and len(chunk) >= 2:
                combined_text += str(chunk[1])
            else:
                combined_text += str(chunk)

        print(f"📌 [합쳐진 RSC 페이로드 총 길이] : {len(combined_text):,} bytes")

        # 3. 핫딜/상품 데이터 탐색
        clean_text = combined_text.replace('\\"', '"').replace('\\\\', '\\')
        
        # 키워드 검색 ('오늘만 이 가격' 또는 '하루특가' 또는 'BEST' 또는 상품 속성)
        deal_matches = re.findall(r'"([가-힣a-zA-Z0-9\s,\(\)\[\]/~%+._-]{5,60})"', clean_text)
        
        # 상품 형태 단어 필터링 (가격, 할인, 상품명 등)
        product_candidates = []
        for m in deal_matches:
            if any(w in m for w in ["특가", "세트", "개입", "개", "박스", "kg", "g", "ml", "L", "수익", "최저가"]):
                if not any(ex in m for ex in ["설명 보기", "메뉴", "정산", "의견", "버튼", "레이아웃"]):
                    product_candidates.append(m)

        unique_candidates = list(dict.fromkeys(product_candidates))
        print(f"📌 [RSC 스트리밍 메모리 추출 핫딜 상품 후보 수량] : {len(unique_candidates)}개")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        if unique_candidates:
            print("📌 [추출된 상품 후보 20개 샘플]:")
            for idx, item in enumerate(unique_candidates[:20], 1):
                print(f"  #{idx:02d} {item}")
        else:
            print("⚠️ 파싱 조건 보정 필요: clean_text 500자 샘플:")
            print(clean_text[:500])

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(run_next_f_extraction())
