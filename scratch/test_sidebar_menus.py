import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def test_sidebar_navigation():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [토스 쉐어링크 사이드바 메뉴별 상품 수량 정밀 계측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        print("📡 sharelink.toss.im/home 접속 중...")
        await page.goto("https://sharelink.toss.im/home", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 사이드바 메뉴 타겟들
        menu_targets = ["베스트 랭킹", "상품 조회", "링크"]

        for menu_name in menu_targets:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"👉 사이드바 메뉴 [{menu_name}] 클릭 시도...")
            try:
                # 메뉴 클릭
                menu_btn = page.locator(f"button:has-text('{menu_name}'), div:has-text('{menu_name}')").first
                if await menu_btn.is_visible():
                    await menu_btn.click()
                    await page.wait_for_timeout(3000)

                    cur_url = page.url
                    btn_count = await page.locator("button:has-text('링크 발급')").count()
                    
                    # 상품 카드 계측
                    titles = await page.evaluate("""() => {
                        return Array.from(document.querySelectorAll("button[aria-label]"))
                            .map(b => b.getAttribute("aria-label"))
                            .filter(l => l && l.length > 5 && !l.includes("설명") && !l.includes("메뉴"));
                    }""")
                    unique_t = list(dict.fromkeys(titles))

                    print(f"  📍 이동된 URL       : {cur_url}")
                    print(f"  📌 링크 발급 버튼 수량 : {btn_count}개")
                    print(f"  📌 마운트된 상품 수량 : {len(unique_t)}개")

                    if unique_t:
                        print(f"  📌 샘플 3개: {unique_t[:3]}")
                else:
                    print(f"  ⚠️ [{menu_name}] 메뉴 버튼을 찾을 수 없거나 노출되지 않음")
            except Exception as e:
                print(f"  ❌ [{menu_name}] 이동 중 오류: {e}")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_sidebar_navigation())
