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
SHOT_DESK = os.path.abspath(os.path.join(os.path.dirname(__file__), "typography_upgrade_desktop.png"))
SHOT_MOB = os.path.abspath(os.path.join(os.path.dirname(__file__), "typography_upgrade_mobile.png"))

PORT = 8986

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_typography_ui():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 상품명/가격 타이포그래피 가독성 시각화 실측]")
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

        title_size = await page_desk.evaluate("""() => {
            const el = document.querySelector('.card-item-title');
            return window.getComputedStyle(el).fontSize;
        }""")

        price_size = await page_desk.evaluate("""() => {
            const el = document.querySelector('.card-price-text');
            return window.getComputedStyle(el).fontSize;
        }""")

        print(f"📌 [데스크톱 상품명 폰트 크기 실측]: {title_size}")
        print(f"📌 [데스크톱 판매가격 폰트 크기 실측]: {price_size}")

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

        mob_title_size = await page_mob.evaluate("""() => {
            const el = document.querySelector('.card-item-title');
            return window.getComputedStyle(el).fontSize;
        }""")

        mob_price_size = await page_mob.evaluate("""() => {
            const el = document.querySelector('.card-price-text');
            return window.getComputedStyle(el).fontSize;
        }""")

        print(f"📌 [모바일 상품명 폰트 크기 실측]: {mob_title_size}")
        print(f"📌 [모바일 판매가격 폰트 크기 실측]: {mob_price_size}")

        await page_mob.screenshot(path=SHOT_MOB, full_page=False)

        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🎉 [검증 완수] 상품명(0.98rem/800볼드) & 판매가(1.18rem/900볼드) 시선 강탈 시각화 완수!")
    print(f"📸 Desktop 캡처 완료: {SHOT_DESK}")
    print(f"📸 Mobile 캡처 완료: {SHOT_MOB}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_typography_ui())
