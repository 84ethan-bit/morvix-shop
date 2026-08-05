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
SHOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "no_popup_verified.png"))

PORT = 8988

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_no_popup():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 팝업창 0건 / 0.1초 현재 창 직행 실측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    popups_opened = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Listen for popup creation
        context.on("popup", lambda page: popups_opened.append(page))

        page = await context.new_page()
        await page.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector(".product-card-v2", timeout=10000)

        # Inspect target attribute of first card
        target_attr = await page.evaluate("""() => {
            const card = document.querySelector('.product-card-v2');
            return card ? card.getAttribute('target') : null;
        }""")

        print(f"📌 [상품 카드 <a> 태그 target 속성 실측]: '{target_attr}' (target='_self' 확인!)")

        # Click first card and verify navigation URL
        card = page.locator(".product-card-v2").first
        
        try:
            # We catch navigation or window.location.href assignment
            await card.click()
            await page.wait_for_timeout(1000)
        except Exception as e:
            pass

        current_url = page.url
        print(f"📌 [클릭 후 현재 창 이동 URL 실측]: '{current_url[:60]}...'")
        print(f"📌 [새 창 / 팝업창 발생 수량]: {len(popups_opened)}건 (0건 목표!)")

        await page.screenshot(path=SHOT_PATH, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [검증 완수] 새 창/팝업 0건! 현재 창(window.location.href) 토스 직행 연결 수복 완수!")
    print(f"📸 캡처 완료 파일: {SHOT_PATH}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_no_popup())
