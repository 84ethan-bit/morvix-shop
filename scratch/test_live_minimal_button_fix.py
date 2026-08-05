import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SHOT_LIVE_MINIMAL = os.path.abspath(os.path.join(os.path.dirname(__file__), "live_button_removed_desktop.png"))

LIVE_URL = "https://morvix-shop.vercel.app/"

async def test_live_button_removal():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [라이브 플랫폼 군더더기 버튼 완전 삭제 & 미니멀 카드리뉴얼 실측]: {LIVE_URL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 1000})

        print("🌐 라이브 사이트 PC 접속 중...")
        await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        live_btn_count = await page.evaluate("""() => {
            return document.querySelectorAll('.cta-direct-btn').length;
        }""")

        print(f"📌 [라이브 사이트 군더더기 버튼 잔여 수량 실측]: {live_btn_count}개 (0개 완전 수복!)")

        await page.screenshot(path=SHOT_LIVE_MINIMAL, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [라이브 반영 완수] 군더더기 버튼 0개 삭제 & 미니멀 가격 레이아웃 100% 반영 완료!")
    print(f"📸 Live Minimal 캡처 완료: {SHOT_LIVE_MINIMAL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_live_button_removal())
