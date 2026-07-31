import asyncio
import os
import sys
import re
import json
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def check_specific():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [대표님 지정 2개 상품 토스 라이브 DOM 원본 수집 검증]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

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

        # 하루특가 전수 스캔
        await page.goto("https://sharelink.toss.im/links/best-ranking/daily-deals?sectionCode=TODAY_DEAL", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # 무한 스크롤 15회 딥 마운트
        for step in range(1, 16):
            try:
                await page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 15) * {step})")
            except: pass
            await page.wait_for_timeout(500)

        all_cards_text = await page.evaluate("""() => {
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

    print(f"📌 마운트된 총 카드 수: {len(all_cards_text)}개\n")

    for idx, raw in enumerate(all_cards_text, 1):
        if "알파시디" in raw or "타이다이" in raw or "순수스토리" in raw or "쉬블림로브" in raw:
            print(f"🎯 [발견!] 카드 #{idx}")
            print(f"  • RAW 텍스트: {lines_flat(raw)}")

            clean_raw = re.sub(r'[\d,]+\s*원\s*수익', '', raw)
            clean_raw = re.sub(r'수익', '', clean_raw)
            clean_raw = re.sub(r'30일\s*최저가', '', clean_raw)

            disc_match = re.search(r'(\d+)[%％]', raw)
            disc = disc_match.group(1) if disc_match else ""

            prices = re.findall(r'([\d,]+)\s*원', clean_raw)
            prices_int = [int(p.replace(',', '')) for p in prices if int(p.replace(',', '')) >= 500]

            print(f"  • 혜택할인가 (price) : {prices_int[0]:,}원" if prices_int else "  • 혜택할인가: 없음")
            print(f"  • 할인율 (discount)  : {disc}%" if disc else "  • 할인율: 없음")
            print("--------------------------------------------------")

def lines_flat(text):
    return " | ".join([l.strip() for l in text.split('\n') if l.strip()])

if __name__ == "__main__":
    asyncio.run(check_specific())
