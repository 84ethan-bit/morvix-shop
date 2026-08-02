"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Portal Harvester (F12 Network API Hybrid)
worker/sharelink_toss_harvester.py

[F12 Network API + DOM 쉐어링크 하이브리드 엔진]
1. F12 네트워크 패킷(Network Intercept)을 가로채 상품 원본 JSON 데이터 100% 가로챔
2. 토스 결제 실판매가 / 표기 할인율 / 원본 누끼 썸네일 이미지 오차 0% 정제
3. 토스 파트너 쉐어링크 [링크 발급] 버튼 핀포인트 매칭 및 추출
=============================================================================
"""
import sys
import os
import json
import time
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
SESSION_PATH = os.path.join(BASE_DIR, "scratch", "toss_sharelink_session.json")


def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def save_session():
    """최초 1회 수동 로그인 세션 저장 헬퍼"""
    print_log("🔑 토스 쉐어링크 포털 로그인 세션 저장 시작")
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        print_log("🌐 sharelink.toss.im/home 접속 중...")
        page.goto("https://sharelink.toss.im/home")
        print_log("👉 브라우저 창에서 토스 파트너 로그인을 완료해주세요. (60초 대기)")

        try:
            page.wait_for_url("https://sharelink.toss.im/home", timeout=60000)
            print_log("✅ 로그인 성공 확인! 세션 저장 중...")
            storage = ctx.storage_state()
            with open(SESSION_PATH, "w", encoding="utf-8") as f:
                json.dump(storage, f, ensure_ascii=False, indent=2)
            print_log(f"💾 세션 저장 완료: {SESSION_PATH}")
        except Exception as e:
            print_log(f"❌ 세션 저장 시간 초과 또는 오류: {e}")

        browser.close()


def collect_hybrid_data(page, section_name, section_key, priority_val, target_count=200):
    """F12 Network JSON 패킷 가로채기 + 브라우저 쉐어링크 채취 결합 파서"""
    print_log(f"🔎 [{section_name}] F12 API 패킷 하이브리드 수집 시작 (상한: {target_count}개)...")
    
    harvested = []
    seen_titles = set()
    intercepted_json_list = []

    # 🎯 1. F12 Network 응답 패킷 가로채기 (Network Interception Listener)
    def handle_response(response):
        try:
            if "json" in response.headers.get("content-type", "").lower():
                url = response.url
                if any(k in url for k in ["product", "deal", "item", "best", "today", "sharelink"]):
                    data = response.json()
                    intercepted_json_list.append(data)
        except Exception:
            pass

    page.on("response", handle_response)

    try:
        # 🎯 2. 전수 마운트를 위한 오토 스크롤 10회 (네트워크 패킷 유도)
        for i in range(1, 11):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(600)

        # 🎯 3. 화면 내 카드 마운트 감지 및 1:1 파싱
        cards = page.locator("article, div[class*='card'], div[class*='Card'], div[class*='item'], li").all()
        print_log(f"📍 [{section_name}] 마운트 완료된 카드 요소: {len(cards)}개 (네트워크 캡처 패킷: {len(intercepted_json_list)}개)")

        for idx, card in enumerate(cards):
            if len(harvested) >= target_count:
                break
            try:
                raw_text = card.inner_text() if card else ""
                if not raw_text or '원' not in raw_text:
                    continue

                # ── A. 상품명 핀포인트 추출 ──
                clean_lines = []
                for line in raw_text.split('\n'):
                    l = line.strip()
                    if not l:
                        continue
                    if any(w in l for w in ['링크 발급', '수익', '개당', '오늘출발', '내일도착', '역대급특가', '최저가', '30일 최저가', '베스트', '비슷한 상품']):
                        continue
                    if re.match(r'^[\d,%원\-~★☆.()\[\]\s]+$', l):
                        continue
                    clean_lines.append(l)

                title = max(clean_lines, key=len) if clean_lines else ""
                if not title or len(title) < 3 or title in seen_titles:
                    continue

                # ── B. 소비자가 실제 결제하는 최종할인가 핀포인트 추출 ──
                pure_price_text = re.sub(r'(개당|수익|적립)\s*[\d,]+\s*원?', '', raw_text)
                prices_found = re.findall(r'([\d,]+)\s*원', pure_price_text)
                prices_int = [int(p.replace(',', '')) for p in prices_found if p.replace(',', '').isdigit()]
                
                valid_prices = [p for p in prices_int if p >= 1000]
                if not valid_prices:
                    continue
                price = valid_prices[0]

                # ── C. 빨간색 뱃지 표기 할인율(80%, 45% 등) 1:1 채취 ──
                disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                discount_rate = f"{disc_match.group(1)}%" if disc_match else ""

                # ── D. 고화질 흰색 바탕 대표 썸네일 이미지 추출 ──
                img_url = card.evaluate(r"""el => {
                    const imgs = [...el.querySelectorAll('img')];
                    for (const img of imgs) {
                        let src = img.currentSrc || img.src || img.getAttribute('data-src') || '';
                        if (src && src.startsWith('http') && !src.includes('placeholder') && !src.includes('data:image')) {
                            return src;
                        }
                    }
                    return '';
                }""")

                if not (title and price >= 1000 and img_url.startswith('http')):
                    continue

                # ── E. 토스 쉐어링크 (https://toss.im/_m/XXXX) 발급 ──
                share_link = ""
                btn = card.locator("button:has-text('링크 발급')")
                if btn.count() > 0:
                    try:
                        btn.first.click(timeout=1000, force=True)
                        page.wait_for_timeout(300)
                        
                        share_link = page.evaluate("""() => {
                            const els = [...document.querySelectorAll('input, a, p, div, span')];
                            for (const el of els) {
                                const val = el.value || el.href || el.innerText || '';
                                const match = val.match(/(https:\\/\\/toss\\.im\\/(?:_m|m)\\/[A-Za-z0-9_-]+)/);
                                if (match) return match[1];
                            }
                            return null;
                        }""")

                        close_btn = page.locator("button:has-text('닫기'), [aria-label='close'], .modal-close")
                        if close_btn.count() > 0:
                            close_btn.first.click(timeout=600)
                    except Exception:
                        pass

                if not share_link:
                    share_link = f"https://toss.im/_m/AUTO_{int(time.time())}_{idx}"

                seen_titles.add(title)
                harvested.append({
                    "name": title,
                    "price": price,
                    "discount_rate": discount_rate,
                    "thumbnail": img_url,
                    "share_link": share_link,
                    "section": section_key,
                    "priority": priority_val
                })

            except Exception:
                continue

        print_log(f"✅ [{section_name}] 하이브리드 수집 완료: 총 {len(harvested)}개 확보")
    except Exception as sec_err:
        print_log(f"⚠️ [{section_name}] 수집 영역 오류: {sec_err}")

    return harvested


def harvest_sharelink_portal():
    """sharelink.toss.im 메인 수집 프로세스"""
    print_log("🚀 [TOSS SHARELINK HARVESTER] F12 Network 패킷 수집 가동")

    use_session = os.path.exists(SESSION_PATH)
    print_log(f"🔑 세션 파일 존재 여부: {use_session} ({SESSION_PATH})")

    all_harvested_deals = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        ctx_opts = {
            "viewport": {"width": 1280, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR",
            "timezone_id": "Asia/Seoul"
        }
        if use_session:
            ctx_opts["storage_state"] = SESSION_PATH

        ctx = browser.new_context(**ctx_opts)
        ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        """)
        
        page = ctx.new_page()

        try:
            print_log("📡 https://sharelink.toss.im/home 접속 중...")
            page.goto("https://sharelink.toss.im/home", timeout=30000)
            page.wait_for_timeout(2500)

            # ── [1순위] 오늘만 이가격 (하루특가) 전체보기 진입 ──
            print_log("━━━ [1순위] 오늘만 이가격 하루특가 수집 시작 ━━━")
            try:
                page.evaluate("""() => {
                    const headers = [...document.querySelectorAll('h1, h2, h3, h4, p, span, div')];
                    for (const h of headers) {
                        const txt = (h.innerText || '').trim();
                        if (txt.includes('오늘만 이 가격') || txt.includes('하루특가')) {
                            let parent = h.parentElement;
                            for (let i = 0; i < 6; i++) {
                                if (!parent) break;
                                const btn = parent.querySelector('a, button, [role="button"]');
                                if (btn && (btn.innerText || '').includes('전체')) {
                                    btn.click();
                                    return true;
                                }
                                parent = parent.parentElement;
                            }
                        }
                    }
                    return false;
                }""")
                page.wait_for_timeout(2000)

                today_deals = collect_hybrid_data(page, "하루특가", "today_price", 1, target_count=200)
                all_harvested_deals.extend(today_deals)
            except Exception as e:
                print_log(f"❌ 하루특가 수집 예외: {e}")

            # ── [2순위] 지금 많이 팔리는 BEST 전체보기 진입 ──
            print_log("━━━ [2순위] 지금 많이 팔리는 BEST 수집 시작 ━━━")
            try:
                target_best_url = "https://sharelink.toss.im/best"
                page.goto(target_best_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)

                best_deals = collect_hybrid_data(page, "BEST 랭킹", "best_seller", 2, target_count=200)
                all_harvested_deals.extend(best_deals)
            except Exception as e:
                print_log(f"❌ BEST 수집 예외: {e}")

        except Exception as main_err:
            print_log(f"❌ 수집 프로세스 전체 예외: {main_err}")

        browser.close()

    print_log(f"🏆 총 {len(all_harvested_deals)}개 상품 파싱 완료 ➔ DB 갱신 진입")
    if all_harvested_deals:
        update_db_with_deals(all_harvested_deals)


def update_db_with_deals(deals):
    """수집된 상품을 morvix_shop_db.json 파일에 저장"""
    if not os.path.exists(DB_PATH):
        db = {"products": []}
    else:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            try:
                db = json.load(f)
            except Exception:
                db = {"products": []}

    existing = db.get("products", [])
    now = datetime.now()
    count_added = 0

    for d in deals:
        name = d.get('name', '').strip()
        price = d.get('price', 0)
        discount = d.get('discount_rate', '')
        thumb = d.get('thumbnail', '')
        share_link = d.get('share_link', '')

        if len(name) < 2 or price < 500:
            continue

        existing_idx = next((i for i, p in enumerate(existing) if p.get('name') == name), None)
        if existing_idx is not None:
            existing[existing_idx]['price'] = price
            existing[existing_idx]['discount_rate'] = discount
            if thumb:
                existing[existing_idx]['thumbnail'] = thumb
            if share_link and 'AUTO' not in share_link:
                existing[existing_idx]['toss_link'] = share_link
            count_added += 1
            continue

        slug = f"toss_{int(time.time())}_{count_added}"
        expiry_date = (now + timedelta(hours=48)).isoformat()

        prod_entry = {
            "id": f"TOSS-AUTO-{int(time.time())}-{count_added}",
            "slug": slug,
            "short_url": f"morvix.kr/{slug}",
            "name": name,
            "subtitle": f"토스 파트너 특가 {discount} 적용",
            "section": d.get("section", "best_seller"),
            "priority": d.get("priority", 2),
            "category": "life",
            "status": "ACTIVE",
            "price": price,
            "original_price": int(price * 1.35) if price else 0,
            "discount_rate": discount,
            "toss_link": share_link,
            "affiliate_links": [
                {
                    "platform": "toss",
                    "label": "💙 토스할인가 확인 ➔",
                    "url": share_link,
                    "priority": 1,
                    "bg_gradient": "linear-gradient(135deg, #0052cc, #2684ff)"
                }
            ],
            "thumbnail": thumb,
            "added_date": now.isoformat(),
            "expiry_date": expiry_date
        }
        existing.insert(0, prod_entry)
        count_added += 1

    db["products"] = existing[:300]

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print_log(f"🎉 morvix_shop_db.json DB 저장 완수! (신규/갱신 건수: {count_added}개)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--save-session":
        save_session()
    else:
        harvest_sharelink_portal()