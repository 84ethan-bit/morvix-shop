import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def test_swiper_navigation():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 [Swiper 네비게이션 및 무한 동적 마운트 정밀 계측]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 1280, "height": 900}
        )
        page = await context.new_page()

        print("📡 https://sharelink.toss.im/home 접속 중...")
        await page.goto("https://sharelink.toss.im/home", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. 초기 상태
        btn_count_0 = await page.locator("button:has-text('링크 발급')").count()
        print(f"📌 [1. 초기 상태 링크 발급 버튼] : {btn_count_0}개")

        # 2. '오늘만 이 가격' Swiper 슬라이드 '다음' 버튼 10회 연쇄 클릭 테스트
        next_btns = page.locator("button[aria-label='다음']")
        next_count = await next_btns.count()
        print(f"📌 [페이지 내 발견된 '다음' 네비게이션 버튼 수량] : {next_count}개")

        for idx in range(next_count):
            nb = next_btns.nth(idx)
            if await nb.is_visible():
                print(f"👉 #{idx+1}번째 '다음' 버튼 10회 연속 클릭 수행 중...")
                for click_idx in range(10):
                    try:
                        await nb.click(force=True)
                        await page.wait_for_timeout(300)
                    except Exception as e:
                        print(f"  ⚠️ 클릭 중단 ({click_idx}회차): {e}")
                        break

        await page.wait_for_timeout(2000)

        # 3. 페이지 바닥까지 휠 스크롤 5회 수행
        print("📜 [페이지 수직 스크롤 5회 수행 중]...")
        for _ in range(5):
            await page.evaluate("window.scrollBy(0, 1000)")
            await page.wait_for_timeout(500)

        # 4. Swiper 슬라이드 컨테이너 가로 스크롤 강제 진행
        await page.evaluate("""() => {
            document.querySelectorAll(".swiper-slide, [class*='slide']").forEach(el => {
                el.style.display = 'block';
                el.style.visibility = 'visible';
            });
            document.querySelectorAll(".swiper, [class*='swiper']").forEach(s => {
                s.scrollLeft += 10000;
            });
        }""")

        await page.wait_for_timeout(2000)

        # 5. 수복 후 전체 상품명 및 링크 발급 버튼 계측
        final_buttons = await page.locator("button:has-text('링크 발급')").count()
        print(f"📌 [수복 후 총 마운트된 링크 발급 버튼 수량] : {final_buttons}개")

        # 6. 마운트된 모든 상품명 수집 및 출력
        product_labels = await page.evaluate("""() => {
            const labels = [];
            document.querySelectorAll("button[aria-label]").forEach(b => {
                const label = b.getAttribute("aria-label");
                if (label && label.length > 5 && !label.includes("설명 보기") && !label.includes("메뉴") && !label.includes("의견")) {
                    labels.push(label);
                }
            });
            return Array.from(new Set(labels));
        }""")

        print(f"📌 [최종 마운트된 유일 상품 수량] : {len(product_labels)}개")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        if product_labels:
            print("📌 [수집된 상품 샘플 15개]:")
            for i, p_title in enumerate(product_labels[:15], 1):
                print(f"  #{i:02d} {p_title}")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_swiper_navigation())
