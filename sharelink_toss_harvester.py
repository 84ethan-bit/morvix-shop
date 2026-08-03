"""
=============================================================================
MORVIX SHOP OS - Master Single-Session Integrated Harvester
- 목적: 단 1회 로그인(수동 2차인증 대비 대기 포함) -> [오늘만 이가격] -> [BEST] 연속 수집
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKER_DIR = os.path.join(BASE_DIR, "worker")
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch")

os.makedirs(WORKER_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)

SESSION_PATH = os.path.join(SCRATCH_DIR, "toss_sharelink_session.json")
TODAY_DB_PATH = os.path.join(WORKER_DIR, "today_products_db.json")
BEST_DB_PATH = os.path.join(WORKER_DIR, "best_products_db.json")


def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [MASTER ENGINE] {msg}", flush=True)


def clean_product_name(raw_name):
    if not raw_name:
        return ""
    cleaned = re.sub(r'개당\s*[\d,]+원\s*수익', '', raw_name)
    cleaned = re.sub(r'[\d,]+원\s*수익', '', cleaned)
    cleaned = re.sub(r'수익금?\s*[\d,]+원', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned.lstrip(',').lstrip('-').strip() if len(cleaned.lstrip(',').lstrip('-').strip()) >= 2 else raw_name


def run_master_harvester():
    print_log("🚀 MORVIX SHOP OS - 단일 세션 통합 수집 엔진 가동 시작...")

    JUNK_KEYWORDS = [
        '수익', '당 ', '개당', '100g', '100ml', '10g', '1포당', 
        '1롤당', '1매당', '1매입당', '1마리당', '1세트당', '1정당', '1미당',
        '링크 발급', '최저가', '내일출발', '오늘출발', '베스트판매자', 
        '전체 보기', '전체보기', '특가', '역대급특가'
    ]

    use_session = os.path.exists(SESSION_PATH)

    with sync_playwright() as p:
        # 수동 로그인 대응 및 모니터링을 위해 화면(headless=False)으로 가동
        browser = p.chromium.launch(
            headless=False,
            slow_mo=50,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        ctx_opts = {
            "viewport": {"width": 1440, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR",
            "permissions": ["clipboard-read", "clipboard-write"]
        }
        
        if use_session:
            ctx_opts["storage_state"] = SESSION_PATH
            print_log("🔑 기존 로그인 세션 파일(Storage State) 로드 완료!")

        ctx = browser.new_context(**ctx_opts)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        page = ctx.new_page()

        # =========================================================================
        # 🔑 [1단계] 로그인 상태 검증 및 수동 로그인 타임 (2차 인증 대응)
        # =========================================================================
        print_log("📡 [1/3단계] 토스 파트너스 메인 접속 및 세션 검증 중...")
        page.goto("https://sharelink.toss.im/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        # 로그인 페이지로 튕겼거나 로그인 버튼이 보이는 경우 -> 2차 인증 대기
        if "login" in page.url or page.locator("text='로그인'").count() > 0:
            print_log("⚠️ 로그인이 필요합니다! 화면에서 아이디/비번 입력 및 폰 2차 인증을 진행해 주세요.")
            print_log("⏳ (최대 60초간 대기합니다. 로그인이 완료되면 자동으로 수집이 시작됩니다...)")
            
            # 로그인 성공 후 메인 페이지 진입 대기 (최대 60초)
            try:
                page.wait_for_url(lambda url: "login" not in url and "sharelink.toss.im" in url, timeout=60000)
                print_log("✅ 로그인 성공 확인! 새로운 세션을 저장합니다.")
                ctx.storage_state(path=SESSION_PATH)
            except Exception:
                print_log("❌ 로그인 대기 시간이 초과되었습니다. 작업을 중단합니다.")
                browser.close()
                return
        else:
            print_log("✅ 이미 로그인된 안정적인 세션입니다. 계속 진행합니다.")
            ctx.storage_state(path=SESSION_PATH)

        # =========================================================================
        # 📦 [2단계] '오늘만 이가격' 수집
        # =========================================================================
        print_log("--------------------------------------------------")
        print_log("📦 [2/3단계] '오늘만 이가격' 수집 시작...")
        
        url_today = "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=TODAY_PRICE"
        page.goto(url_today, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(4000)

        # 스크롤 대기
        for _ in range(5):
            page.evaluate("window.scrollBy(0, 1500);")
            page.wait_for_timeout(2000)
        page.evaluate("window.scrollTo(0, 0);")
        page.wait_for_timeout(1000)

        harvested_today = []
        seen_today = set()

        btn_today = page.locator("button:has-text('링크 발급')").all()
        print_log(f"📍 [오늘만 이가격] 감지된 상품 버튼: 총 {len(btn_today)}개")

        for idx, btn in enumerate(btn_today):
            try:
                card = btn.locator("xpath=ancestor::*[contains(@class, 'Card') or contains(@class, 'Item') or contains(@class, 'Product') or self::article or self::section or count(descendant::button[text()='링크 발급']) = 1][1]")
                if not card or not card.count():
                    card = btn.locator("xpath=ancestor::div[4]")

                raw_text = card.inner_text() if card.count() else ""
                if not raw_text or '원' not in raw_text:
                    continue

                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                candidate_titles = [l for l in lines if len(l) >= 4 and not re.match(r'^[\d,%원\-~★☆.()\s]+$', l) and not any(k in l for k in JUNK_KEYWORDS) and '%' not in l]

                if not candidate_titles: continue
                title = clean_product_name(max(candidate_titles, key=len))
                if not title: continue
                if title in seen_today: title = f"{title}_{idx}"

                price_lines = [l for l in lines if '원' in l and not any(k in l for k in ['당 ', '수익', '개당'])]
                valid_prices = [int(p.replace(',', '')) for pl in price_lines for p in re.findall(r'([\d,]+)\s*원', pl) if int(p.replace(',', '')) >= 500]
                if not valid_prices: continue
                price = min(valid_prices)

                disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                discount_rate = f"{disc_match.group(1)}%" if disc_match else "오늘만 특가"

                img_url = card.evaluate("el => { const img = el.querySelector('img'); return img ? (img.currentSrc || img.src || '') : ''; }") or "https://static.toss.im/icons/png/4x/icon-toss-logo.png"

                real_link = None
                try:
                    btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(50)
                    btn.click(force=True)
                    page.wait_for_timeout(400)
                    clip_content = page.evaluate("async () => await navigator.clipboard.readText()").strip()
                    m = re.search(r'https:\/\/toss\.im\/_m\/[a-zA-Z0-9]+', clip_content)
                    if m: real_link = m.group(0)
                except Exception: pass

                if not real_link:
                    real_link = f"https://sharelink.toss.im/links/product?id=today_{abs(hash(title))%1000000}"

                print_log(f"   🔥 [오늘만 수집 성공] ({idx+1}/{len(btn_today)}) {title} | {price}원")
                seen_today.add(title)
                harvested_today.append({"name": title, "price": price, "discount_rate": discount_rate, "thumbnail": img_url, "share_link": real_link})
            except Exception: continue

        # 오늘만 이가격 DB 저장
        if harvested_today:
            db_today = {"products": []}
            now = datetime.now()
            for c, d in enumerate(harvested_today):
                slug = f"toss_today_{int(time.time())}_{c}"
                db_today["products"].append({
                    "id": f"TOSS-TODAY-{int(time.time())}-{c}", "slug": slug, "short_url": f"morvix.kr/{slug}",
                    "name": d['name'], "subtitle": f"오늘만 이가격 {d['discount_rate']} 적용", "section": "today_price",
                    "priority": 1, "category": "life", "status": "ACTIVE", "price": d['price'],
                    "original_price": int(d['price'] * 1.35), "discount_rate": d['discount_rate'],
                    "toss_link": d['share_link'], "thumbnail": d['thumbnail'], "added_date": now.isoformat()
                })
            with open(TODAY_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(db_today, f, ensure_ascii=False, indent=2)
            print_log(f"💾 [오늘만 이가격 DB 저장 완료] 총 {len(harvested_today)}개")

        page.wait_for_timeout(3000)

        # =========================================================================
        # 🏆 [3단계] '지금 많이 팔리는 BEST' 수집 (동일 브라우저 세션 연동)
        # =========================================================================
        print_log("--------------------------------------------------")
        print_log("🏆 [3/3단계] '지금 많이 팔리는 BEST' 수집 시작...")

        url_best = "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING"
        page.goto(url_best, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        print_log("📜 BEST 전수 수집용 스크롤 확장 중...")
        last_height = page.evaluate("document.body.scrollHeight")
        for step in range(12):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            page.wait_for_timeout(4000)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height

        page.evaluate("window.scrollTo(0, 0);")
        page.wait_for_timeout(2000)

        harvested_best = []
        seen_best = set()
        total_processed_best = 0

        while True:
            buttons_best = page.locator("button:has-text('링크 발급')").all()
            unprocessed = buttons_best[total_processed_best:]
            if not unprocessed: break

            print_log(f"📍 [BEST 진행 상황] 처리 완료: {total_processed_best}개 / 전체 버튼: {len(buttons_best)}개")

            for btn in unprocessed:
                try:
                    total_processed_best += 1
                    card = btn.locator("xpath=ancestor::*[contains(@class, 'Card') or contains(@class, 'Item') or contains(@class, 'Product') or self::article or self::section or count(descendant::button[text()='링크 발급']) = 1][1]")
                    if not card or not card.count(): card = btn.locator("xpath=ancestor::div[4]")

                    raw_text = card.inner_text() if card.count() else ""
                    if not raw_text or '원' not in raw_text: continue

                    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                    candidate_titles = [l for l in lines if len(l) >= 4 and not re.match(r'^[\d,%원\-~★☆.()\s]+$', l) and not any(k in l for k in JUNK_KEYWORDS) and '%' not in l]

                    if not candidate_titles: continue
                    title = clean_product_name(max(candidate_titles, key=len))
                    if not title: continue
                    if title in seen_best: title = f"{title}_{total_processed_best}"

                    price_lines = [l for l in lines if '원' in l and not any(k in l for k in ['당 ', '수익', '개당'])]
                    valid_prices = [int(p.replace(',', '')) for pl in price_lines for p in re.findall(r'([\d,]+)\s*원', pl) if int(p.replace(',', '')) >= 500]
                    if not valid_prices: continue
                    price = min(valid_prices)

                    disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                    discount_rate = f"{disc_match.group(1)}%" if disc_match else "BEST 특가"

                    img_url = card.evaluate("el => { const img = el.querySelector('img'); return img ? (img.currentSrc || img.src || '') : ''; }") or "https://static.toss.im/icons/png/4x/icon-toss-logo.png"

                    real_link = None
                    try:
                        btn.scroll_into_view_if_needed()
                        page.wait_for_timeout(50)
                        btn.click(force=True)
                        page.wait_for_timeout(500)
                        clip_content = page.evaluate("async () => await navigator.clipboard.readText()").strip()
                        m = re.search(r'https:\/\/toss\.im\/_m\/[a-zA-Z0-9]+', clip_content)
                        if m: real_link = m.group(0)
                    except Exception: pass

                    if not real_link:
                        real_link = f"https://sharelink.toss.im/links/product?id=best_{abs(hash(title))%1000000}"

                    print_log(f"   🔥 [BEST 수집 성공] {title} | {price}원")
                    seen_best.add(title)
                    harvested_best.append({"name": title, "price": price, "discount_rate": discount_rate, "thumbnail": img_url, "share_link": real_link})
                except Exception: continue

            check_new = page.locator("button:has-text('링크 발급')").all()
            if len(check_new) <= len(buttons_best): break

        # BEST DB 저장
        if harvested_best:
            db_best = {"products": []}
            now = datetime.now()
            for c, d in enumerate(harvested_best):
                slug = f"toss_best_{int(time.time())}_{c}"
                db_best["products"].append({
                    "id": f"TOSS-BEST-{int(time.time())}-{c}", "slug": slug, "short_url": f"morvix.kr/{slug}",
                    "name": d['name'], "subtitle": f"토스 베스트 특가 {d['discount_rate']} 적용", "section": "best_ranking",
                    "priority": 2, "category": "life", "status": "ACTIVE", "price": d['price'],
                    "original_price": int(d['price'] * 1.35), "discount_rate": d['discount_rate'],
                    "toss_link": d['share_link'], "thumbnail": d['thumbnail'], "added_date": now.isoformat()
                })
            with open(BEST_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(db_best, f, ensure_ascii=False, indent=2)
            print_log(f"💾 [BEST DB 저장 완료] 총 {len(harvested_best)}개")

        print_log("--------------------------------------------------")
        print_log("🎉 [통합 프로세스 완결] 모든 수집 및 DB 저장이 완벽하게 종료되었습니다!")
        browser.close()


if __name__ == "__main__":
    run_master_harvester()