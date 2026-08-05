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
SHOT_DESK = os.path.abspath(os.path.join(os.path.dirname(__file__), "platform_hero_desktop.png"))
SHOT_MOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "platform_hero_mobile.png"))

PORT = 8994

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_hero_ui():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & MORVIX 실시간 핫딜 플랫폼 히어로 UI 실측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop Viewport
        page_desk = await browser.new_page(viewport={"width": 1200, "height": 950})
        await page_desk.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page_desk.wait_for_selector(".product-card-v2", timeout=10000)
        await page_desk.wait_for_timeout(1000)

        today_text = await page_desk.inner_text("#metric-today-count")
        print(f"📌 [오늘 업데이트 라이브 지표 수량]: '{today_text}'")

        await page_desk.screenshot(path=SHOT_DESK, full_page=False)

        # 2. Mobile Viewport
        page_mob = await browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True
        )
        await page_mob.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page_mob.wait_for_selector(".product-card-v2", timeout=10000)
        await page_mob.wait_for_timeout(1000)
        await page_mob.screenshot(path=SHOT_MOB, full_page=False)

        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🎉 [검증 완수] MORVIX 실시간 핫딜 플랫폼 히어로 & 라이브 지표 패널 구현 완료!")
    print(f"📸 Desktop 캡처 완료: {SHOT_DESK}")
    print(f"📸 Mobile 캡처 완료: {SHOT_MOB}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_hero_ui())
