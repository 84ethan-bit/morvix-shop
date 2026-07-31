import asyncio
import os
import sys
import re
import json
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")
TARGET_URL = "https://sharelink.toss.im/links/best-ranking/daily-deals?sectionCode=TODAY_DEAL"

async def dump_raw_toss_prices():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 [토스 DOM 원본 1:1 직결 가격 추출 덤프 (NO GIT PUSH)]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

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

        print("📡 하루특가 전용 페이지 접속 중...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # 15개 카드의 DOM rawText 분석
        cards = await page.evaluate("""() => {
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

        print(f"📌 [탐지된 토스 카드 수량] : {len(cards)}개 (상위 15개 덤프 출력)\n")

        NOISE = ['베스트판매자', '내일도착', '오늘출발', '역대급특가', '30일 최저가', '링크 발급']

        dump_list = []
        for idx, text in enumerate(cards[:15], 1):
            lines = [l.strip() for l in text.split('\n') if l.strip()]

            # 1. Title
            name_candidates = [
                l for l in lines
                if len(l) >= 4
                and not re.match(r'^[\d,%원\-~★☆.()\[\]]+$', l)
                and '%' not in l
                and '개당' not in l
                and '수익' not in l
                and not any(n in l for n in NOISE)
            ]
            title = max(name_candidates, key=len) if name_candidates else lines[0]

            # 2. Raw Discount Rate
            disc_match = re.search(r'(\d+)[%％]', text)
            discount_rate = f"{disc_match.group(1)}%" if disc_match else "없음 (-)"

            # 3. Raw Clean Prices
            clean_text = re.sub(r'[\d,]+\s*원\s*수익', '', text)
            clean_text = re.sub(r'수익', '', clean_text)
            clean_text = re.sub(r'30일\s*최저가', '', clean_text)

            prices_found = re.findall(r'([\d,]+)\s*원', clean_text)
            prices_int = [int(pr.replace(',', '')) for pr in prices_found if int(pr.replace(',', '')) >= 500]

            sale_price = prices_int[0] if prices_int else 0
            original_price = prices_int[1] if len(prices_int) >= 2 and prices_int[1] > sale_price else 0

            dump_list.append({
                "no": idx,
                "title": title,
                "sale_price": sale_price,
                "original_price": original_price,
                "discount_rate": discount_rate
            })

            print(f"#{idx:02d} | [{title[:25]}]")
            print(f"     └─ 혜택할인가 (price)      : {sale_price:,}원")
            print(f"     └─ 화면 표시 정가 (original) : {original_price:,}원" if original_price > 0 else "     └─ 화면 표시 정가 (original) : 표기 없음 (0원)")
            print(f"     └─ 할인율 태그 (discount)  : {discount_rate}")
            print("----------------------------------------------------------------------------")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎉 [1:1 직결 덤프 출력 완료] 위의 15개 상품 원본 가격이 토스 화면과 일치하는지 확인해 주십시오.")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(dump_raw_toss_prices())
