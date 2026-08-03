"""
=============================================================================
MORVIX SHOP OS - BEST Ranking Harvester (Slow Scroll & Stable Dynamic Harvester)
- 전용 목적: [지금 많이 팔리는 BEST] 스크롤 대기 시간 4초 보장 및 전체 상품 누락 없는 전수 수집
- 추가 기능: 수집 완료 후 기존 메인 통합 DB(morvix_shop_db.json)와 병합 저장
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
WORKER_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(BASE_DIR, "scratch", "toss_sharelink_session.json")
BEST_DB_PATH = os.path.join(WORKER_DIR, "best_products_db.json")


def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def clean_product_name(raw_name):
    if not raw_name:
        return ""
    cleaned = re.sub(r'개당\s*[\d,]+원\s*수익', '', raw_name)
    cleaned = re.sub(r'[\d,]+원\s*수익', '', cleaned)
    cleaned = re.sub(r'수익금?\s*[\d,]+원', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned.lstrip(',').lstrip('-').strip() if len(cleaned.lstrip(',').lstrip('-').strip()) >= 2 else raw_name


def harvest_best_ranking_exclusively():
    print_log("🏆 [BEST 수집 엔진] 4초 딥 스크롤 안정화 수집 가동...")
    
    harvested = []
    seen_titles = set()

    JUNK_KEYWORDS = [
        '수익', '당 ', '개당', '100g', '100ml', '10g', '1포당', 
        '1롤당', '1매당', '1매입당', '1마리당', '1세트당', '1정당', '1미당',
        '링크 발급', '최저가', '내일출발', '오늘출발', '베스트판매자', 
        '전체 보기', '전체보기', '특가', '역대급특가'
    ]

    use_session = os.path.exists(SESSION_PATH)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # 서버 환경 최적화 (headless 모드 활성화)
            slow_mo=50,
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
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
            print_log("🔑 로그인 세션 파일(Storage State) 로드 완료!")

        ctx = browser.new_context(**ctx_opts)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        page = ctx.new_page()

        try:
            url_best = "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING"
            print_log(f"📡 BEST 전체보기 페이지 접속 중: {url_best}")
            page.goto(url_best, wait_until="domcontentloaded", timeout=60000)
            
            print_log("⏳ 초기 페이지 렌더링 대기 중 (5초)...")
            page.wait_for_timeout(5000)

            print_log("📜 4초 호흡의 안정적 스크롤 확장 진행 중...")
            for step in range(12):
                page.evaluate("window.scrollBy(0, 1500);")
                print_log(f"   - 스크롤 {step+1}회 진행 중... (4초 대기)")
                page.wait_for_timeout(4000)

            print_log("📜 최하단 도달 완료. 상단으로 복귀 후 전수 스캔 시작...")
            page.evaluate("window.scrollTo(0, 0);")
            page.wait_for_timeout(2000)

            total_processed = 0
            
            while True:
                buttons = page.locator("button:has-text('링크 발급')").all()
                unprocessed_buttons = buttons[total_processed:]
                
                if not unprocessed_buttons:
                    break

                print_log(f"📍 [진행 상황] 현재까지 처리된 상품: {total_processed}개 / 발견된 전체 버튼: {len(buttons)}개")

                for btn in unprocessed_buttons:
                    try:
                        total_processed += 1
                        card = btn.locator("xpath=ancestor::*[contains(@class, 'Card') or contains(@class, 'Item') or contains(@class, 'Product') or self::article or self::section or count(descendant::button[text()='링크 발급']) = 1][1]")
                        if not card or not card.count():
                            card = btn.locator("xpath=ancestor::div[4]")

                        raw_text = card.inner_text() if card.count() else ""
                        if not raw_text or '원' not in raw_text:
                            card = btn.locator("xpath=ancestor::div[6]")
                            raw_text = card.inner_text() if card.count() else ""
                            if not raw_text or '원' not in raw_text:
                                continue

                        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                        
                        candidate_titles = []
                        for l in lines:
                            if re.match(r'^\d{1,3}$', l) or re.search(r'\d+.*당', l) or re.search(r'^\d+%\s*특가', l):
                                continue
                            if len(l) >= 4 and not re.match(r'^[\d,%원\-~★☆.()\s]+$', l):
                                if not any(k in l for k in JUNK_KEYWORDS) and '%' not in l:
                                    candidate_titles.append(l)

                        if not candidate_titles:
                            continue
                        
                        raw_title = max(candidate_titles, key=len)
                        title = clean_product_name(raw_title)
                        
                        if not title:
                            continue
                        
                        if title in seen_titles:
                            title = f"{title}_{total_processed}"

                        price_lines = [l for l in lines if '원' in l and not any(k in l for k in ['당 ', '수익', '개당'])]
                        valid_prices = []
                        for pl in price_lines:
                            prices = re.findall(r'([\d,]+)\s*원', pl)
                            for p in prices:
                                val = int(p.replace(',', ''))
                                if val >= 500:
                                    valid_prices.append(val)

                        if not valid_prices:
                            continue
                        price = min(valid_prices)

                        disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                        if disc_match:
                            discount_rate = f"{disc_match.group(1)}%"
                        elif '최저가' in raw_text:
                            discount_rate = "최저가"
                        elif '역대급특가' in raw_text:
                            discount_rate = "역대급특가"
                        else:
                            discount_rate = "BEST 특가"

                        img_url = card.evaluate(r"""el => {
                            const img = el.querySelector('img');
                            return img ? (img.currentSrc || img.src || img.getAttribute('data-src') || '') : '';
                        }""")
                        if not img_url or not img_url.startswith('http'):
                            img_url = "https://static.toss.im/icons/png/4x/icon-toss-logo.png"

                        real_toss_link = None
                        try:
                            btn.scroll_into_view_if_needed()
                            page.wait_for_timeout(50)
                            btn.click(force=True)
                            page.wait_for_timeout(500)

                            clip_content = page.evaluate("async () => await navigator.clipboard.readText()").strip()
                            if clip_content:
                                match_link = re.search(r'https:\/\/toss\.im\/_m\/[a-zA-Z0-9]+', clip_content)
                                if match_link:
                                    real_toss_link = match_link.group(0)
                        except Exception:
                            pass

                        if not real_toss_link:
                            prod_id_match = re.search(r'/product/(\d+)', img_url) or re.search(r'/ai/([a-zA-Z0-9_-]+)', img_url)
                            if prod_id_match:
                                token_id = prod_id_match.group(1)
                                real_toss_link = f"https://sharelink.toss.im/links/product?id={token_id}"
                            else:
                                safe_token = str(abs(hash(title)))[:8]
                                real_toss_link = f"https://sharelink.toss.im/links/product?id=best_{safe_token}"

                        print_log(f"   🔥 [BEST 수집 성공] {title} | {price}원 | {discount_rate}")

                        seen_titles.add(title)
                        harvested.append({
                            "name": title,
                            "price": price,
                            "discount_rate": discount_rate,
                            "thumbnail": img_url,
                            "share_link": real_toss_link,
                            "section": "best_ranking",
                            "priority": 2
                        })
                    except Exception:
                        continue
                
                new_buttons_check = page.locator("button:has-text('링크 발급')").all()
                if len(new_buttons_check) <= len(buttons):
                    break

            print_log(f"✅ [BEST 상품] 안정화 전수 수집 완료: 총 {len(harvested)}개")
        except Exception as err:
            print_log(f"❌ BEST 수집 예외 발생: {err}")

        browser.close()

    # 수집된 BEST 상품들을 기존 메인 통합 DB(morvix_shop_db.json)에 병합 저장
    if harvested:
        db = {"products": []}
        now = datetime.now()
        
        main_db_path = os.path.join(BASE_DIR, "morvix_shop_db.json")
        worker_main_db_path = os.path.join(WORKER_DIR, "morvix_shop_db.json")
        target_main_db = main_db_path if os.path.exists(main_db_path) else worker_main_db_path
        
        existing_products = []
        if os.path.exists(target_main_db):
            try:
                with open(target_main_db, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 1번('today_price') 상품들은 그대로 유지하고 기존 'best_ranking'만 이번 수집분으로 교체
                    existing_products = [p for p in data.get("products", []) if p.get("section") == "today_price"]
            except Exception:
                pass

        best_products = []
        for count_added, d in enumerate(harvested):
            slug = f"toss_best_{int(time.time())}_{count_added}"
            prod_entry = {
                "id": f"TOSS-BEST-{int(time.time())}-{count_added}",
                "slug": slug,
                "short_url": f"morvix.kr/{slug}",
                "name": d['name'],
                "subtitle": f"토스 베스트 특가 {d['discount_rate']} 적용",
                "section": "best_ranking",
                "priority": 2,
                "category": "life",
                "status": "ACTIVE",
                "price": d['price'],
                "original_price": int(d['price'] * 1.35),
                "discount_rate": d['discount_rate'],
                "toss_link": d['share_link'],
                "affiliate_links": [
                    {
                        "platform": "toss",
                        "label": "💙 토스할인가 확인 ➔",
                        "url": d['share_link'],
                        "priority": 1,
                        "bg_gradient": "linear-gradient(135deg, #0052cc, #2684ff)"
                    }
                ],
                "thumbnail": d['thumbnail'],
                "added_date": now.isoformat(),
                "expiry_date": (now + timedelta(hours=48)).isoformat()
            }
            best_products.append(prod_entry)

        # 1번 상품들과 2번 BEST 상품들을 하나의 리스트로 결합
        db["products"] = existing_products + best_products

        # 메인 통합 DB 경로들에 저장
        for path_target in [main_db_path, worker_main_db_path]:
            try:
                with open(path_target, "w", encoding="utf-8") as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        print_log(f"🎉 [통합 DB 적재 완료] 오늘만 이가격({len(existing_products)}개) + BEST 상품({len(best_products)}개) ➔ 총 {len(db['products'])}개 통합 DB 구축 완료!")


if __name__ == "__main__":
    harvest_best_ranking_exclusively()