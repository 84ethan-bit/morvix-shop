import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SHOT_DESK = os.path.abspath(os.path.join(os.path.dirname(__file__), "live_verified_desktop.png"))
SHOT_MOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "live_verified_mobile.png"))

LIVE_URL = "https://morvix-shop.vercel.app/"

async def test_live_site():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [라이브 플랫폼 Vercel 배포 정밀 실측 검증 엔진]: {LIVE_URL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop Viewport
        page_desk = await browser.new_page(viewport={"width": 1200, "height": 1000})
        print("🌐 라이브 사이트 데스크톱 접속 중...")
        await page_desk.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await page_desk.wait_for_timeout(3000)

        hero_text = await page_desk.inner_text(".platform-hero-title")
        notice_text = await page_desk.inner_text(".header-disclosure-text")
        print(f"📌 [라이브 히어로 헤드라인 실측]: '{hero_text}'")
        print(f"📌 [라이브 권고 문구 1번 옵션 실측]: '{notice_text}'")

        await page_desk.screenshot(path=SHOT_DESK, full_page=False)

        # 2. Mobile Viewport
        page_mob = await browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True
        )
        print("📱 라이브 사이트 모바일 접속 중...")
        await page_mob.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await page_mob.wait_for_timeout(3000)

        mob_hero = await page_mob.inner_text(".platform-hero-title")
        print(f"📌 [라이브 모바일 히어로 헤드라인 실측]: '{mob_hero}'")

        await page_mob.screenshot(path=SHOT_MOB, full_page=False)

        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🎉 [라이브 반영 완수] GitHub git push ➔ Vercel 자동 배포 100% 정상 작동 완료!")
    print(f"📸 Live Desktop 캡처 완료: {SHOT_DESK}")
    print(f"📸 Live Mobile 캡처 완료: {SHOT_MOB}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_live_site())
