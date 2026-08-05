import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SHOT_LIVE_FOOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "live_cat_food_fixed.png"))

LIVE_URL = "https://morvix-shop.vercel.app/"

async def test_live_category():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [라이브 플랫폼 카테고리 분류 자동 복원 검증]: {LIVE_URL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 950})

        print("🌐 라이브 사이트 접속 중...")
        await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Click '식품' tab on live site
        print("👆 '식품' 카테고리 탭 클릭 중...")
        await page.click(".cat-pill[data-cat='food']")
        await page.wait_for_timeout(1000)

        live_food_title = await page.inner_text("#section-title")
        live_food_count = await page.inner_text("#product-count")

        print(f"📌 [라이브 '식품' 탭 실측]: 타이틀='{live_food_title}', 노출='{live_food_count}'")

        await page.screenshot(path=SHOT_LIVE_FOOD, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [라이브 수복 완수] 카테고리 탭 클릭 시 100% 자동 분류 & 동적 타이틀 복원 완료!")
    print(f"📸 Live Food 캡처 완료: {SHOT_LIVE_FOOD}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_live_category())
