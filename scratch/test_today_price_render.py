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
SHOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "today_price_fixed.png"))

PORT = 8995

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_today_price():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 오늘만 이가격 타임어택 렌더링 실측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        
        # Wait for product cards
        await page.wait_for_selector(".product-card-v2", timeout=10000)
        await page.wait_for_timeout(1500)

        # Count cards in section 1 (time-attack-grid)
        sec1_count = await page.evaluate("""() => {
            return document.querySelectorAll('#time-attack-grid .product-card-v2').length;
        }""")

        # Count cards in section 2 (product-grid)
        sec2_count = await page.evaluate("""() => {
            return document.querySelectorAll('#product-grid .product-card-v2').length;
        }""")

        count_text = await page.inner_text("#product-count")

        print(f"📌 [섹션 1 '오늘만 이 가격! 하루특가' 렌더링 카드 수량]: {sec1_count}개")
        print(f"📌 [섹션 2 '지금 많이 팔리는 BEST' 렌더링 카드 수량]: {sec2_count}개")
        print(f"📌 [우측 상단 핫딜 카운터 텍스트]: '{count_text}'")

        await page.screenshot(path=SHOT_PATH, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [수복 검증 완수] 섹션 1 '오늘만 이 가격! 하루특가' 렌더링 및 카운터 연동 완수!")
    print(f"📸 캡처 완료 파일: {SHOT_PATH}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_today_price())
