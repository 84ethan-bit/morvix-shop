import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def test_ui_unblock():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 [Plan B] UI PointerEvent 및 React Fiber 직접 트리거 계측")
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

        # 1. 이전 DOM 상태 수량 계측
        cards_before = await page.locator("button:has-text('링크 발급')").count()
        print(f"📌 [클릭 전 링크 발급 버튼 수량] : {cards_before}개")

        # 2. React Fiber internal onClick 핸들러 직접 invoke 테스트
        print("⚡ [React Fiber onClick 직접 실행 시도]...")
        invoke_res = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll("button"));
            const targetBtn = btns.find(b => b.textContent.includes("전체 보기") || b.textContent.includes("전체보기"));
            if (!targetBtn) return { success: false, reason: "Button not found" };

            // PointerEvent 시퀀스 발화
            const opts = { bubbles: true, cancelable: true, view: window };
            targetBtn.dispatchEvent(new PointerEvent("pointerdown", opts));
            targetBtn.dispatchEvent(new MouseEvent("mousedown", opts));
            targetBtn.dispatchEvent(new PointerEvent("pointerup", opts));
            targetBtn.dispatchEvent(new MouseEvent("mouseup", opts));
            targetBtn.dispatchEvent(new MouseEvent("click", opts));

            // React Fiber key 찾기
            const fiberKey = Object.keys(targetBtn).find(k => k.startsWith("__reactProps$"));
            if (fiberKey && targetBtn[fiberKey] && typeof targetBtn[fiberKey].onClick === 'function') {
                try {
                    targetBtn[fiberKey].onClick({ preventDefault: () => {}, stopPropagation: () => {} });
                    return { success: true, via: "React Fiber Direct Invoke" };
                } catch(e) {
                    return { success: false, reason: e.message };
                }
            }

            return { success: true, via: "Synthetic Pointer/Mouse Events" };
        }""")

        print(f"📌 [React Fiber 실행 결과] : {invoke_res}")
        await page.wait_for_timeout(3000)

        # 3. Swiper 스크롤 및 무한 스크롤 트리거 테스트
        print("📜 [Swiper 슬라이드 및 마우스 스크롤 트리거]...")
        await page.evaluate("""async () => {
            window.scrollTo(0, document.body.scrollHeight);
            const swiperWrappers = document.querySelectorAll(".swiper-wrapper");
            swiperWrappers.forEach(w => {
                w.scrollLeft += 5000;
            });
        }""")
        await page.wait_for_timeout(2000)

        # 4. 클릭 및 스크롤 후 DOM 변화 계측
        cards_after = await page.locator("button:has-text('링크 발급')").count()
        print(f"📌 [클릭 및 스크롤 후 링크 발급 버튼 수량] : {cards_after}개")

        # 5. Swiper 슬라이드 전체 개수 계측
        swiper_slides_count = await page.locator(".swiper-slide").count()
        print(f"📌 [DOM 상 Swiper-slide 전체 노드 수량] : {swiper_slides_count}개")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(test_ui_unblock())
