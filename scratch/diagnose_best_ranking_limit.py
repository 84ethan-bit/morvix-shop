import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")
TARGET_URL = "https://sharelink.toss.im/links/best-ranking"

async def diagnose_best_limit():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [지금 많이 팔리는 BEST 48개 한계 정밀 계측 진단]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        print("📡 BEST 랭킹 페이지 접속 중...")
        await page.goto(TARGET_URL, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. 48개 카드의 상세 텍스트 및 할인율/가격 구조 분석
        cards_analysis = await page.evaluate("""() => {
            const cards = [];
            const btns = [...document.querySelectorAll('button')].filter(b => (b.innerText || '').includes('링크 발급'));
            for (let b of btns) {
                let p = b.parentElement;
                for (let i = 0; i < 7; i++) {
                    if (!p) break;
                    if (p.innerText && p.innerText.length > 20) {
                        cards.push({
                            rawText: p.innerText,
                            html: p.outerHTML.slice(0, 300)
                        });
                        break;
                    }
                    p = p.parentElement;
                }
            }
            return cards;
        }""")

        print(f"📌 [ProductCard DOM 요소 개수] : {len(cards_analysis)}개")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        no_discount_count = 0
        has_discount_count = 0

        for idx, c in enumerate(cards_analysis, 1):
            text = c['rawText']
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            has_disc = any('%' in l for l in lines)
            if has_disc:
                has_discount_count += 1
            else:
                no_discount_count += 1
                if no_discount_count <= 5:
                    print(f"  ⚠️ [할인율 태그 없음 샘플 #{no_discount_count}] {lines[:4]}")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📊 [카드 할인율 태그 존재 여부 분석]")
        print(f"  ✅ 할인율(%) 표기 카드  : {has_discount_count}개")
        print(f"  ❌ 할인율(%) 미표기 카드: {no_discount_count}개 (Safety Filter에 의해 Reject됨)")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(diagnose_best_limit())
