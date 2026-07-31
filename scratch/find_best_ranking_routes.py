import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

CANDIDATE_URLS = [
    "https://sharelink.toss.im/links/best-ranking",
    "https://sharelink.toss.im/links/best-ranking/best-seller",
    "https://sharelink.toss.im/links/best-ranking/best-seller?sectionCode=BEST_SELLER",
    "https://sharelink.toss.im/links/best-ranking/best-seller?sectionCode=BEST",
    "https://sharelink.toss.im/links/best-ranking/weekly-deals",
    "https://sharelink.toss.im/links/best-ranking/today-best",
    "https://sharelink.toss.im/links/search"
]

async def test_best_ranking_routes():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [지금 많이 팔리는 BEST 전용 라우트 탐색 테스트]")
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

        for target_url in CANDIDATE_URLS:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📡 타겟 시도: {target_url}")
            try:
                resp = await page.goto(target_url, wait_until="networkidle")
                await page.wait_for_timeout(2000)

                status = resp.status if resp else "N/A"
                actual_url = page.url
                
                # '링크 발급' 버튼 수 계측
                btn_count = await page.locator("button:has-text('링크 발급')").count()
                
                # 유일 상품명 추출
                titles = await page.evaluate("""() => {
                    return Array.from(document.querySelectorAll("button[aria-label]"))
                        .map(b => b.getAttribute("aria-label"))
                        .filter(l => l && l.length > 5 && !l.includes("설명") && !l.includes("메뉴"));
                }""")
                unique_t = list(dict.fromkeys(titles))

                print(f"  📌 HTTP Status: {status} | Actual URL: {actual_url}")
                print(f"  📌 '링크 발급' 버튼: {btn_count}개 | 유일 상품: {len(unique_t)}개")
                if unique_t:
                    print(f"  📌 샘플 3개: {unique_t[:3]}")

            except Exception as e:
                print(f"  ❌ 접속 예외: {e}")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_best_ranking_routes())
