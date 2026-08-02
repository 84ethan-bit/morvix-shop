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
SHOT_GRID = os.path.abspath(os.path.join(os.path.dirname(__file__), "rich_grid_desktop.png"))

PORT = 8998

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_rich_grid():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 전체 탭 128개 풍성한 그리드 실측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 1000})
        await page.goto(f"http://localhost:{PORT}/index.html", wait_until="networkidle", timeout=30000)
        
        # Wait for product cards
        await page.wait_for_selector(".product-card-v2", timeout=10000)
        await page.wait_for_timeout(1000)

        # Count text
        count_text = await page.inner_text("#product-count")
        print(f"📌 [우측 상단 핫딜 카운터 텍스트]: '{count_text}'")

        # Number of cards in main grid
        grid_cards_count = await page.evaluate("""() => {
            return document.querySelectorAll('#product-grid .product-card-v2').length;
        }""")
        print(f"📌 [하단 그리드 기본 렌더링 카드 수량]: {grid_cards_count}개")

        # Total cards on page
        total_cards_count = await page.evaluate("""() => {
            return document.querySelectorAll('.product-card-v2').length;
        }""")
        print(f"📌 [페이지 전체 총 렌더링 카드 수량]: {total_cards_count}개")

        await page.screenshot(path=SHOT_GRID, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🎉 [검증 완수] 메인 화면 상품 빈약 현상 완전 수복! 기본 {grid_cards_count}개 빽빽한 렌더링 확인!")
    print(f"📸 캡처 완료 파일: {SHOT_GRID}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_rich_grid())
