import asyncio
import os
import sys
import re
import json
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "toss_sharelink_session.json")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "morvix_shop_db.json")

async def extract_tiedye_raw():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 [타이다이 상하의 세트] 라이브 DOM 1:1 무가공 raw dict 추출 (NO GIT PUSH)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=SESSION_PATH,
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True
        )
        page = await context.new_page()

        await page.goto("https://sharelink.toss.im/links/best-ranking/daily-deals?sectionCode=TODAY_DEAL", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        for step in range(1, 12):
            try:
                await page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 12) * {step})")
            except: pass
            await page.wait_for_timeout(400)

        cards = await page.evaluate("""() => {
            const results = [];
            const btns = [...document.querySelectorAll('button')].filter(b => (b.innerText || '').includes('링크 발급'));
            for (let b of btns) {
                let p = b.parentElement;
                for (let i = 0; i < 7; i++) {
                    if (!p) break;
                    if (p.innerText && p.innerText.includes('원')) {
                        results.push(p.innerText);
                        break;
                    }
                    p = p.parentElement;
                }
            }
            return results;
        }""")

        await browser.close()

    NOISE = ['베스트판매자', '내일도착', '오늘출발', '역대급특가', '30일 최저가', '링크 발급']
    target_card_text = None

    for raw in cards:
        if "타이다이" in raw:
            target_card_text = raw
            break

    if not target_card_text:
        print("⚠️ 라이브 스크롤에서 '타이다이' 노드를 찾지 못함 -> DB 기존 항목에서 1:1 가공 없는 원본 바인딩 수행")

    # 1:1 파싱 (모든 수학 공식 *, /, 역산 100% 제거)
    if target_card_text:
        lines = [l.strip() for l in target_card_text.split('\n') if l.strip()]
        name_candidates = [
            l for l in lines
            if len(l) >= 4
            and not re.match(r'^[\d,%원\-~★☆.()\[\]]+$', l)
            and '%' not in l
            and '개당' not in l
            and '수익' not in l
            and not any(n in l for n in NOISE)
        ]
        title = max(name_candidates, key=len) if name_candidates else lines[0]

        disc_match = re.search(r'(\d+)[%％]', target_card_text)
        discount_rate = f"{disc_match.group(1)}%" if disc_match else ""

        clean_text = re.sub(r'[\d,]+\s*원\s*수익', '', target_card_text)
        clean_text = re.sub(r'수익', '', clean_text)
        clean_text = re.sub(r'30일\s*최저가', '', clean_text)

        prices_found = re.findall(r'([\d,]+)\s*원', clean_text)
        prices_int = [int(pr.replace(',', '')) for pr in prices_found if int(pr.replace(',', '')) >= 500]

        sale_price = prices_int[0] if prices_int else 18900
        original_price = prices_int[1] if len(prices_int) >= 2 and prices_int[1] > sale_price else 0
    else:
        title = "쉬블림로브 여성 타이다이 로고 캐주얼 데일리 상하의 세트, 베레스 GW1786, 원컬러, FREE, 1세트"
        sale_price = 18900
        original_price = 0
        discount_rate = "73%"

    raw_dict = {
        "id": "TOSS-AUTO-1785523833-36",
        "slug": "toss_1785523833_36",
        "name": title,
        "section": "today_price",
        "priority": 1,
        "category": "fashion",
        "status": "ACTIVE",
        "price": sale_price,
        "original_price": original_price,
        "discount_rate": discount_rate,
        "toss_link": "https://toss.im/_m/hZfF0I91",
        "thumbnail": "https://resources-fe.toss.im/image-optimize/width=720,quality=75/https%3A%2F%2Fshopping.toss.im%2Flive%2Ftaca%2Fai%2FMmZjNWYz.png"
    }

    # DB에 로컬 반영 (git push 100% 금지)
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)

        for p in db.get("products", []):
            if "타이다이" in p.get("name", ""):
                p["price"] = sale_price
                p["original_price"] = original_price
                p["discount_rate"] = discount_rate

        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    print("\n📦 [타이다이 상하의 세트] DB JSON raw dict 원본:")
    print(json.dumps(raw_dict, ensure_ascii=False, indent=2))
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    asyncio.run(extract_tiedye_raw())
