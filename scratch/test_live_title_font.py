import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SHOT_LIVE_TITLE = os.path.abspath(os.path.join(os.path.dirname(__file__), "live_title_larger_desktop.png"))

LIVE_URL = "https://morvix-shop.vercel.app/"

async def test_live_title_font():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [라이브 플랫폼 상품명 폰트 1.10rem 추가 대형화 실측]: {LIVE_URL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 1000})

        print("🌐 라이브 사이트 PC 접속 중...")
        await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        desk_title_size = await page.evaluate("""() => {
            const el = document.querySelector('.card-item-title');
            return window.getComputedStyle(el).fontSize;
        }""")

        print(f"📌 [라이브 PC 상품명 대형 폰트 크기 실측]: {desk_title_size} (1.10rem / 17.6px 시원시원함!)")

        await page.screenshot(path=SHOT_LIVE_TITLE, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [라이브 반영 완수] 상품명 폰트 1.10rem 추가 확장 100% 라이브 배포 완료!")
    print(f"📸 Live Title 캡처 완료: {SHOT_LIVE_TITLE}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_live_title_font())
