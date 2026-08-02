import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

INDEX_PATH = "file:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html")).replace("\\", "/")
SHOT_DESKTOP = os.path.abspath(os.path.join(os.path.dirname(__file__), "category_ui_desktop.png"))
SHOT_MOBILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "category_ui_mobile.png"))

async def capture_category_ui():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📸 [쇼핑몰 UI 카테고리 필터 바 반응형 실측 캡처 스크립트 실행]")
    print(f"🔗 Target: {INDEX_PATH}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop Viewport (1200x800)
        page_desk = await browser.new_page(viewport={"width": 1200, "height": 800})
        await page_desk.goto(INDEX_PATH, wait_until="networkidle", timeout=30000)
        await page_desk.wait_for_timeout(1500)
        await page_desk.screenshot(path=SHOT_DESKTOP, full_page=False)
        print(f"✅ Desktop UI 캡처 완료: {SHOT_DESKTOP}")

        # 2. Mobile Viewport (390x844)
        page_mob = await browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True
        )
        await page_mob.goto(INDEX_PATH, wait_until="networkidle", timeout=30000)
        await page_mob.wait_for_timeout(1500)

        # '식품' 카테고리 탭 클릭 시뮬레이션
        food_btn = page_mob.locator("button[data-cat='food']")
        if await food_btn.count() > 0:
            await food_btn.click()
            await page_mob.wait_for_timeout(500)

        await page_mob.screenshot(path=SHOT_MOBILE, full_page=False)
        print(f"✅ Mobile UI 캡처 완료: {SHOT_MOBILE}")

        await browser.close()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(capture_category_ui())
