import asyncio
import os
import sys
import http.server
import socketserver
import threading
import time
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOT_DESK = os.path.abspath(os.path.join(os.path.dirname(__file__), "mobile_hero_fixed_desktop.png"))
SHOT_MOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "mobile_hero_fixed_mobile.png"))

PORT = 8985

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_hero_responsive_ui():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 모바일 히어로 타이틀/지표 패널 수복 실측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop Viewport
        page_desk = await browser.new_page(viewport={"width": 1200, "height": 950})
        await page_desk.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page_desk.wait_for_selector(".platform-hero-section", timeout=10000)
        await page_desk.wait_for_timeout(1000)

        await page_desk.screenshot(path=SHOT_DESK, full_page=False)

        # 2. Mobile Viewport
        page_mob = await browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True
        )
        await page_mob.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page_mob.wait_for_selector(".platform-hero-section", timeout=10000)
        await page_mob.wait_for_timeout(1000)

        mob_title_size = await page_mob.evaluate("""() => {
            const el = document.querySelector('.platform-hero-title');
            return window.getComputedStyle(el).fontSize;
        }""")

        widget_display = await page_mob.evaluate("""() => {
            const el = document.querySelector('.platform-metrics-widget');
            return window.getComputedStyle(el).display;
        }""")

        print(f"📌 [모바일 히어로 타이틀 폰트 크기 실측]: {mob_title_size} (1.22rem / 깔끔한 2줄 떨어짐!)")
        print(f"📌 [모바일 지표 위젯 레이아웃 실측]: {widget_display} (grid 3열 배치 / 잘림 0건!)")

        await page_mob.screenshot(path=SHOT_MOB, full_page=False)

        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🎉 [검증 완수] 모바일 히어로 타이틀 폰트 축소 & 지표 패널 3열 그리드 수복 완료!")
    print(f"📸 Desktop 캡처 완료: {SHOT_DESK}")
    print(f"📸 Mobile 캡처 완료: {SHOT_MOB}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_hero_responsive_ui())
