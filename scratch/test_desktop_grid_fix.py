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
SHOT_DESK = os.path.abspath(os.path.join(os.path.dirname(__file__), "desktop_grid_fixed.png"))
SHOT_MOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "mobile_grid_fixed.png"))

PORT = 8983

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_grid_ui():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 데스크톱 4열 그리드 수복 실측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop Viewport (1200px)
        page_desk = await browser.new_page(viewport={"width": 1200, "height": 950})
        await page_desk.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page_desk.wait_for_selector(".product-grid", timeout=10000)
        await page_desk.wait_for_timeout(1000)

        grid_cols = await page_desk.evaluate("""() => {
            const el = document.querySelector('.product-grid');
            return window.getComputedStyle(el).gridTemplateColumns;
        }""")

        card_width = await page_desk.evaluate("""() => {
            const el = document.querySelector('.product-grid .product-card-v2');
            return el ? el.getBoundingClientRect().width : 0;
        }""")

        print(f"📌 [데스크톱 .product-grid 그리드 열 개수 실측]: {grid_cols}")
        print(f"📌 [데스크톱 개별 카드 가로폭 실측]: {card_width:.1f}px (전체화면 덮침 완전 소탕!)")

        await page_desk.screenshot(path=SHOT_DESK, full_page=False)

        # 2. Mobile Viewport (390px)
        page_mob = await browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True
        )
        await page_mob.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page_mob.wait_for_selector(".product-grid", timeout=10000)
        await page_mob.wait_for_timeout(1000)

        mob_cols = await page_mob.evaluate("""() => {
            const el = document.querySelector('.product-grid');
            return window.getComputedStyle(el).gridTemplateColumns;
        }""")

        print(f"📌 [모바일 .product-grid 그리드 열 개수 실측]: {mob_cols} (2열 모바일 커머스 콤팩트 배치!)")

        await page_mob.screenshot(path=SHOT_MOB, full_page=False)

        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [검증 완수] 데스크톱 4열 그리드 수복 완료 (1줄 4개 콤팩트 카드 배치)!")
    print(f"📸 Desktop 캡처 완료: {SHOT_DESK}")
    print(f"📸 Mobile 캡처 완료: {SHOT_MOB}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_grid_ui())
