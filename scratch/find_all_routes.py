import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def find_portal_routes():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [토스 쉐어링크 파트너 포털 전체 라우트 & API 탐색]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        print("📡 sharelink.toss.im/home 접속 중...")
        await page.goto("https://sharelink.toss.im/home", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. 모든 a 태그 href 추출
        links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href')
            }));
        }""")

        print(f"📌 [포털 내 발견된 모든 <a> 태그 수량] : {len(links)}개")
        for idx, l in enumerate(links, 1):
            print(f"  #{idx:02d} [{l['text']}] -> {l['href']}")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 2. 사이드바 메인 메뉴 클릭 탐색 및 URL 수집
        sidebar_buttons = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll("button, [role='menuitem']")).map(b => ({
                text: b.innerText.trim(),
                title: b.getAttribute('title') || b.getAttribute('aria-label') || ''
            }));
        }""")

        print(f"📌 [사이드바 및 버튼 목록] : {len(sidebar_buttons)}개")
        for idx, b in enumerate(sidebar_buttons[:20], 1):
            print(f"  #{idx:02d} {b['text']} ({b['title']})")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(find_portal_routes())
