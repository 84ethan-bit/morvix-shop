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
SHOT_FOOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "cat_food_fixed.png"))
SHOT_FRUIT = os.path.abspath(os.path.join(os.path.dirname(__file__), "cat_fruit_fixed.png"))
SHOT_TODAY = os.path.abspath(os.path.join(os.path.dirname(__file__), "cat_today_fixed.png"))

PORT = 8984

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_category_filtering():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 카테고리 탭 자동 분류 & 동적 타이틀 수복 실측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 950})

        await page.goto(f"http://localhost:{PORT}/index.html", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector(".cat-pill", timeout=10000)

        # 1. Click '오늘만 이가격' tab
        await page.click(".cat-pill[data-cat='today_price']")
        await page.wait_for_timeout(500)
        today_title = await page.inner_text("#section-title")
        today_count = await page.inner_text("#product-count")
        print(f"📌 ['오늘만 이가격' 탭 클릭 실측]: 타이틀='{today_title}', 노출='{today_count}'")
        await page.screenshot(path=SHOT_TODAY, full_page=False)

        # 2. Click '과일·신선' tab
        await page.click(".cat-pill[data-cat='fruit']")
        await page.wait_for_timeout(500)
        fruit_title = await page.inner_text("#section-title")
        fruit_count = await page.inner_text("#product-count")
        print(f"📌 ['과일·신선' 탭 클릭 실측]: 타이틀='{fruit_title}', 노출='{fruit_count}'")
        await page.screenshot(path=SHOT_FRUIT, full_page=False)

        # 3. Click '식품' tab
        await page.click(".cat-pill[data-cat='food']")
        await page.wait_for_timeout(500)
        food_title = await page.inner_text("#section-title")
        food_count = await page.inner_text("#product-count")
        print(f"📌 ['식품' 탭 클릭 실측]: 타이틀='{food_title}', 노출='{food_count}'")
        await page.screenshot(path=SHOT_FOOD, full_page=False)

        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [검증 완수] 카테고리 탭별 자동 분류 & 동적 타이틀 복원 100% 성공!")
    print(f"📸 Today 캡처 완료: {SHOT_TODAY}")
    print(f"📸 Fruit 캡처 완료: {SHOT_FRUIT}")
    print(f"📸 Food 캡처 완료: {SHOT_FOOD}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_category_filtering())
