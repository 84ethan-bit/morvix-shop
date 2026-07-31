import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")
TARGET_URL = "https://sharelink.toss.im/links/best-ranking"

async def test_best_ranking_scroll():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🏆 [발굴된 BEST 랭킹 전용 URL 무한 스크롤 수집 테스트]")
    print(f"📡 타겟 URL: {TARGET_URL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        print("📡 BEST 랭킹 페이지 접속 중...")
        await page.goto(TARGET_URL, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. 초기 마운트 버튼 수 계측
        btns_0 = await page.locator("button:has-text('링크 발급')").count()
        print(f"📌 [접속 직후 링크 발급 버튼 수량] : {btns_0}개")

        # 2. 무한 스크롤 (Infinite Scroll) 15회 반복 수행
        print("📜 [무한 스크롤 15회 연쇄 수행 중]...")
        prev_count = 0
        for scroll_idx in range(1, 16):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)

            cur_count = await page.locator("button:has-text('링크 발급')").count()
            print(f"  [Scroll #{scroll_idx:02d}] 링크 발급 버튼 수: {cur_count}개")
            if cur_count == prev_count and scroll_idx > 5:
                print("  ✅ 스크롤 최하단 도달 (더 이상 상품이 늘어나지 않음)")
                break
            prev_count = cur_count

        # 3. 전수 상품명 추출
        products = await page.evaluate("""() => {
            const items = [];
            document.querySelectorAll("button[aria-label]").forEach(b => {
                const label = b.getAttribute("aria-label");
                if (label && label.length > 5 && !label.includes("설명") && !label.includes("메뉴")) {
                    items.push(label);
                }
            });
            return Array.from(new Set(items));
        }""")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🎉 [BEST 랭킹 수집 성공 팩트 수치] : 총 {len(products)}개 상품 발굴!")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        for idx, title in enumerate(products, 1):
            print(f"  #{idx:02d} {title}")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_best_ranking_scroll())
