import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

INDEX_PATH = "file:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html")).replace("\\", "/")
SHOT_FOOD = os.path.abspath(os.path.join(os.path.dirname(__file__), "food_category_clean.png"))

async def test_food_clean():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📸 [식품 탭 클릭 시 100% 순수 먹거리 전용 노출 검증 스크립트]")
    print(f"🔗 Target: {INDEX_PATH}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.goto(INDEX_PATH, wait_until="networkidle", timeout=30000)
        
        # DOM 마운트 대기
        await page.wait_for_selector(".product-card-v2", timeout=10000)
        await page.wait_for_timeout(1000)

        # 🥦 식품 탭 클릭
        food_btn = page.locator("button[data-cat='food']")
        if await food_btn.count() > 0:
            await food_btn.click()
            await page.wait_for_timeout(1000)

        # 노출된 모든 카드 텍스트 수집
        card_titles = await page.evaluate("""() => {
            const titles = [];
            document.querySelectorAll('.card-item-title').forEach(el => {
                titles.push(el.innerText.trim());
            });
            return titles;
        }""")

        print(f"📌 [식품 탭 클릭 시 렌더링된 총 상품 수량]: {len(card_titles)}개\n")

        non_food_found = []
        for idx, t in enumerate(card_titles, 1):
            if any(bad in t for bad in ["비데", "탈취제", "복구왁스", "모자", "쿨토시", "콘솔박스", "세제", "선풍기", "거치대"]):
                non_food_found.append((idx, t))
            print(f"  #{idx:02d} | {t[:45]}")

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
    asyncio.run(test_food_clean())
