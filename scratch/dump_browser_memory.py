import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")

async def dump_browser_globals():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [전역 메모리 정밀 진단] Browser Window & React State Dump")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 1280, "height": 900}
        )

        page = await context.new_page()

        # 네트워크 요청 트래킹
        requests_log = []
        page.on("request", lambda req: requests_log.append((req.method, req.url)))

        print("📡 sharelink.toss.im/home 접속 중...")
        await page.goto("https://sharelink.toss.im/home", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # 1. window 전역 변수 탐색
        window_keys = await page.evaluate("() => Object.keys(window)")
        next_keys = [k for k in window_keys if "next" in k.lower() or "toss" in k.lower() or "store" in k.lower() or "state" in k.lower() or "react" in k.lower()]
        print(f"📌 [탐색된 관련 window 전역 키] : {next_keys}")

        # 2. window.__next_f 전체 내용 Dump
        next_f = await page.evaluate("() => window.__next_f || null")
        if next_f:
            print(f"📌 [window.__next_f 항목 수] : {len(next_f)}")
            with open("scratch/window_next_f_dump.json", "w", encoding="utf-8") as f:
                json.dump(next_f, f, ensure_ascii=False, indent=2)
            print("💾 window.__next_f 덤프 저장 완료: scratch/window_next_f_dump.json")

        # 3. 네트워크 요청 로그 검속
        print(f"📌 [초기 로드 중 발생한 총 네트워크 요청] : {len(requests_log)}건")
        api_requests = [r for r in requests_log if "api" in r[1] or "graphql" in r[1] or "trpc" in r[1] or "data" in r[1] or "toss.im" in r[1]]
        print(f"📌 [toss.im / API 관련 주요 네트워크 요청 샘플 10건]:")
        for method, url in api_requests[:10]:
            print(f"  [{method}] {url[:100]}")

        await browser.close()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(dump_browser_globals())
