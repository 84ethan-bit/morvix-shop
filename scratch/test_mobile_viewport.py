import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def test_mobile_viewport():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📱 [모바일 뷰포트 (iPhone 13 Pro) & Touch Event 계측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # iPhone 13 Pro 에뮬레이션
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        print("📡 [모바일 모드] https://sharelink.toss.im/home 접속 중...")
        await page.goto("https://sharelink.toss.im/home", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 모바일 DOM 수량 계측
        m_btns_before = await page.locator("button:has-text('링크 발급')").count()
        print(f"📌 [모바일 접속 직후 링크 발급 버튼] : {m_btns_before}개")

        # '전체 보기' 터치/클릭 수행
        print("👉 모바일 화면 상 '전체 보기' 터치 실행...")
        all_btn = page.locator("button:has-text('전체 보기'), button:has-text('전체보기')").first
        if await all_btn.is_visible():
            await all_btn.tap()
            await page.wait_for_timeout(3000)

            m_url = page.url
            m_btns_after = await page.locator("button:has-text('링크 발급')").count()
            print(f"  📍 터치 후 URL          : {m_url}")
            print(f"  📌 터치 후 링크 발급 버튼 : {m_btns_after}개")

            # DOM 전체 HTML 길의 덤프
            content = await page.content()
            print(f"  📌 모바일 HTML DOM 길이   : {len(content):,} bytes")
            with open("scratch/mobile_after_click.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("💾 모바일 클릭 덤프 저장 완료: scratch/mobile_after_click.html")

            # 파싱된 상품명 목록 계측
            titles = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll("button[aria-label]"))
                    .map(b => b.getAttribute("aria-label"))
                    .filter(l => l && l.length > 5 && !l.includes("설명") && !l.includes("메뉴"));
            }""")
            unique_t = list(dict.fromkeys(titles))
            print(f"  📌 [모바일 DOM 내 최종 마운트된 상품 수] : {len(unique_t)}개")
            if unique_t:
                print(f"  📌 샘플 5개: {unique_t[:5]}")
        else:
            print("⚠️ 모바일 화면에서 '전체 보기' 버튼을 발견하지 못함")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_mobile_viewport())
