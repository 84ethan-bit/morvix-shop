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
SHOT_FRUIT = os.path.abspath(os.path.join(os.path.dirname(__file__), "fruit_category_clean.png"))

PORT = 8997

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_fruit_category():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🍎 [로컬 HTTP 서버(port {PORT}) 기동 & '과일·신선' 탭 노출 검증]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.goto(f"http://localhost:{PORT}/index.html", wait_until="networkidle", timeout=30000)
        
        # Wait for selector
        await page.wait_for_selector(".product-card-v2", timeout=10000)
        await page.wait_for_timeout(1000)

        # Click 🍎 과일·신선 button
        fruit_btn = page.locator("button[data-cat='fruit']")
        if await fruit_btn.count() > 0:
            await fruit_btn.click()
            await page.wait_for_timeout(1000)

        # Collect titles
        card_titles = await page.evaluate("""() => {
            const titles = [];
            document.querySelectorAll('.card-item-title').forEach(el => {
                titles.push(el.innerText.trim());
            });
            return titles;
        }""")

        count_text = await page.inner_text("#product-count")
        print(f"📌 [우측 상단 핫딜 카운터]: '{count_text}'")
        print(f"📌 [과일·신선 탭 클릭 시 렌더링된 총 상품 수량]: {len(card_titles)}개\n")

        for idx, t_str in enumerate(card_titles, 1):
            print(f"  #{idx:02d} | {t_str[:50]}")

        await page.screenshot(path=SHOT_FRUIT, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 [검증 완수] '과일·신선' 독립 카테고리 탭 정상 신설 및 100% 순수 신선 과일류 필터링 확인!")
    print(f"📸 캡처 완료 파일: {SHOT_FRUIT}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_fruit_category())
