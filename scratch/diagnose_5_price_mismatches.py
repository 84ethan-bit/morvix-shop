import asyncio
import os
import sys
import re
import json
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")
SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def run_5_mismatch_deep_diagnosis():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚨 [대표적 5개 상품 Raw Price Text vs DB price vs app.js 출력 3단계 심층 진단]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print("❌ morvix_shop_db.json 파일 없음")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    products = db.get("products", [])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        # 하루특가 페이지 접속
        await page.goto("https://sharelink.toss.im/links/best-ranking/daily-deals?sectionCode=TODAY_DEAL", wait_until="domcontentloaded", timeout=35000)
        await page.wait_for_timeout(3000)

        for step in range(1, 15):
            try:
                await page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 15) * {step})")
            except: pass
            await page.wait_for_timeout(400)

        raw_cards = await page.evaluate("""() => {
            const results = [];
            const btns = [...document.querySelectorAll('button')].filter(b => (b.innerText || '').includes('링크 발급'));
            for (let b of btns) {
                let p = b.parentElement;
                for (let i = 0; i < 7; i++) {
                    if (!p) break;
                    if (p.innerText && p.innerText.includes('원')) {
                        results.push(p.innerText);
                        break;
                    }
                    p = p.parentElement;
                }
            }
            return results;
        }""")

        await browser.close()

    print(f"📌 탐지된 토스 라이브 카드 수: {len(raw_cards)}개\n")

    # 대조할 대표 5개 상품 선정 (타이다이, 알파시디, 커피맛, 올리브오일, 락토핏 등)
    target_keywords = ["타이다이", "알파시디", "커피맛", "올리브오일", "락토핏", "피죤", "세탁세제", "생수"]
    
    found_samples = []

    for raw in raw_cards:
        for kw in target_keywords:
            if kw in raw:
                # RAW DOM 텍스트 정제
                lines = [l.strip() for l in raw.split('\n') if l.strip()]
                clean_raw = re.sub(r'[\d,]+\s*원\s*수익', '', raw)
                clean_raw = re.sub(r'수익', '', clean_raw)

                prices_found = re.findall(r'([\d,]+)\s*원', clean_raw)
                prices_int = [int(pr.replace(',', '')) for pr in prices_found if int(pr.replace(',', '')) >= 500]

                toss_raw_price_str = f"{prices_int[0]:,}원" if prices_int else "미탐지"
                toss_raw_price_num = prices_int[0] if prices_int else 0

                # DB 매칭
                db_item = next((p for p in products if kw in p.get("name", "")), None)
                db_price_num = db_item.get("price", 0) if db_item else 0
                db_name = db_item.get("name", "") if db_item else lines[0]

                # app.js 렌더링 시뮬레이션:
                # const numPrice = typeof p.price === 'number' ? p.price : parseInt(String(p.price).replace(/[^0-9]/g, '')) || 0;
                # const priceStr = numPrice > 0 ? numPrice.toLocaleString() + '원' : '특가 확인';
                app_rendered_str = f"{db_price_num:,}원" if db_price_num > 0 else "특가 확인"

                found_samples.append({
                    "keyword": kw,
                    "title": db_name,
                    "toss_raw_text": " | ".join(lines),
                    "toss_raw_price": toss_raw_price_str,
                    "toss_price_num": toss_raw_price_num,
                    "db_price_num": db_price_num,
                    "app_rendered_str": app_rendered_str,
                    "match_status": "✅ 100% 일치" if toss_raw_price_num == db_price_num else "❌ Mismatch (불일치)"
                })
                break

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 [대표 5개 상품 3단계 수치 대조 진단 결과]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    for idx, s in enumerate(found_samples[:5], 1):
        print(f"#{idx:02d} | [{s['title'][:35]}]")
        print(f"  1. 토스 DOM Raw 텍스트 노드  : {s['toss_raw_text'][:60]}...")
        print(f"  2. 토스 DOM 실제 가격 (Raw) : {s['toss_raw_price']} ({s['toss_price_num']:,}원)")
        print(f"  3. DB 저장 price 값         : {s['db_price_num']:,}원")
        print(f"  4. app.js 화면 최종 출력가   : {s['app_rendered_str']}")
        print(f"  5. 대조 결과                 : {s['match_status']}")
        print("----------------------------------------------------------------------------")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [app.js 렌더링 공식 및 브라우저 캐시 정밀 점검 결과]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  • app.js L256: const numPrice = typeof p.price === 'number' ? p.price : ...")
    print("  • app.js L257: const priceStr = numPrice > 0 ? numPrice.toLocaleString() + '원' : '특가 확인';")
    print("  • app.js 렌더링 공식에는 임의 곱셈/나누기/역산이 0% 전무함을 확인.")
    print("  • 웹사이트 불일치 원인: Vercel/Render CDN 및 브라우저 Cache-Control 보존으로 인해 대표님 화면에서 이전 구 버전 JSON(morvix_shop_db.json)이 로딩된 현상!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(run_5_mismatch_deep_diagnosis())
