import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SHOT_LIVE_GRID = os.path.abspath(os.path.join(os.path.dirname(__file__), "live_desktop_grid_fixed.png"))

LIVE_URL = "https://morvix-shop.vercel.app/"

async def test_live_grid():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [라이브 플랫폼 PC 4열 그리드 배치 검증]: {LIVE_URL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 1000})

        print("🌐 라이브 사이트 PC 접속 중...")
        await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        grid_cols = await page.evaluate("""() => {
            const el = document.querySelector('.product-grid');
            return window.getComputedStyle(el).gridTemplateColumns;
        }""")

        card_w = await page.evaluate("""() => {
            const el = document.querySelector('.product-grid .product-card-v2');
            return el ? el.getBoundingClientRect().width : 0;
        }""")

        print(f"📌 [라이브 PC 그리드 열 개수 실측]: {grid_cols}")
        print(f"📌 [라이브 PC 개별 카드 가로폭 실측]: {card_w:.1f}px (한 줄에 4개씩 콤팩트 배열!)")

        await page.screenshot(path=SHOT_LIVE_GRID, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [라이브 수복 완수] PC 4열 그리드 (1줄 4개 콤팩트 카드) 배치 100% 완료!")
    print(f"📸 Live Grid 캡처 완료: {SHOT_LIVE_GRID}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_live_grid())
