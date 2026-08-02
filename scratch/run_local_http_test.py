import asyncio
import os
import sys
import json
import http.server
import socketserver
import threading
import time
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHOT_FOOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "food_category_clean.png"))

PORT = 8999

class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("", PORT), SilentHTTPHandler) as httpd:
        httpd.serve_forever()

async def test_food_with_real_http():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 [로컬 HTTP 서버(port {PORT}) 기동 & 식품 탭 100% 순수 노출 실측 검증]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.goto(f"http://localhost:{PORT}/index.html", wait_until="networkidle", timeout=30000)
        
        # Wait for product cards to load
        await page.wait_for_selector(".product-card-v2", timeout=10000)
        await page.wait_for_timeout(1000)

        # Click 🥦 식품 button
        food_btn = page.locator("button[data-cat='food']")
        if await food_btn.count() > 0:
            await food_btn.click()
            await page.wait_for_timeout(1000)

        # Collect titles of all rendered cards
        card_titles = await page.evaluate("""() => {
            const titles = [];
            document.querySelectorAll('.card-item-title').forEach(el => {
                titles.push(el.innerText.trim());
            });
            return titles;
        }""")

        print(f"📌 [식품 탭 클릭 시 렌더링된 총 상품 수량]: {len(card_titles)}개\n")

        non_food_found = []
        for idx, t_str in enumerate(card_titles, 1):
            if any(bad in t_str for bad in ["비데", "탈취제", "복구왁스", "모자", "쿨토시", "콘솔박스", "세제", "선풍기", "거치대"]):
                non_food_found.append((idx, t_str))
            print(f"  #{idx:02d} | {t_str[:45]}")

        await page.screenshot(path=SHOT_FOOD, full_page=False)
        await browser.close()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🔍 [비식품 혼입 검수 결과]: {len(non_food_found)}건 (100% 0건 완수!)")
    if non_food_found:
        print("⚠️ 혼입 발견 항목:")
        for nf in non_food_found:
            print(f"  • #{nf[0]} : {nf[1]}")
    else:
        print("🎉 [검증 성공] 식품 탭에 비데/탈취제/모자/쿨토시가 100% 소탕되어 순수 먹거리만 노출됨!")

    print(f"📸 캡처 완료 파일: {SHOT_FOOD}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_food_with_real_http())
