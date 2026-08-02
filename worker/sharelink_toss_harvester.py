"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Portal Harvester (Direct URL Perfect V21 - Final Fix)
worker/sharelink_toss_harvester.py

[V21 핵심 보완]
1. URL 이동 후 상품 카드 DOM 렌더링 강제 대기(wait_for_selector) 적용
   -> BEST 랭킹 접속 시 0개 감지 및 조기 종료 현상 원천 차단
2. 스마트 스크롤 최소 5회 강제 수행 보장 -> Render 외부 서버 대량 수집 완결
3. '67% 특가', '100g당 XX원' 등 더미/배지 텍스트 완전 차단 및 결제 판매가 정밀 매핑
=============================================================================
"""
import sys
import os
import json
import time
import re
import subprocess
import shutil
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKER_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
WORKER_DB_PATH = os.path.join(WORKER_DIR, "morvix_shop_db.json")
SESSION_PATH = os.path.join(BASE_DIR, "scratch", "toss_sharelink_session.json")


def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def setup_session_from_env():
    """Render 환경변수(TOSS_SESSION_JSON)로부터 로그인 세션 자동 복원"""
    env_session = os.environ.get("TOSS_SESSION_JSON", "").strip()
    if env_session:
        try:
            os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
            with open(SESSION_PATH, "w", encoding="utf-8") as f:
                f.write(env_session)
            print_log("🔑 [SESSION ENGINE] Render 환경변수로부터 로그인 세션(Storage State) 복원 완료!")
        except Exception as e:
            print_log(f"⚠️ 세션 복원 중 예외 발생: {e}")


def push_to_github_automatically():
    try:
        gh_token = os.environ.get("GH_TOKEN", "").strip()
        print_log("🚀 [AUTO GIT PUSH ENGINE] Render ➔ GitHub 자동 동기화 시도...")

        if os.path.exists(WORKER_DB_PATH):
            shutil.copy(WORKER_DB_PATH, ROOT_DB_PATH)

        if not gh_token:
            print_log("ℹ️ [GH_TOKEN 미설정] 로컬 테스트 완료 (Push 스킵)")
            return

        # Render 토큰 기반 원격 저장소 URL 구성
        repo_url = f"https://x-access-token:{gh_token}@github.com/84ethan-bit/morvix-shop.git"
        
        subprocess.run(["git", "config", "user.name", "Morvix Auto Bot"], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bot@morvix.kr"], cwd=BASE_DIR, capture_output=True)
        
        subprocess.run(["git", "add", "-f", ROOT_DB_PATH], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "add", "-f", WORKER_DB_PATH], cwd=BASE_DIR, capture_output=True)
        
        commit_msg = f"Auto Sync Toss Deals (V21 DOM Wait Fix): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True)
        
        push_res = subprocess.run(["git", "push", repo_url, "HEAD:main", "--force"], cwd=BASE_DIR, capture_output=True, text=True)
        
        if push_res.returncode == 0:
            print_log("🎉 [AUTO PUSH SUCCESS] 깃허브 및 쇼핑몰 반영 완료!")
        else:
            print_log(f"⚠️ Git Push 실패: {push_res.stderr.strip()}")

    except Exception as e:
        print_log(f"❌ Auto Git Push 예외: {e}")


def collect_hybrid_data(page, section_name, section_key, priority_val, target_count=300):
    print_log(f"🔎 [{section_name}] 전수 수집 스마트 스크롤 다운 시작...")
    
    harvested = []
    seen_titles = set()

    # 파싱 시 완전히 배제할 노이즈/더미 키워드 목록
    JUNK_KEYWORDS = [
        '수익', '당 ', '개당', '100g', '100ml', '10g', '1포당', 
        '1롤당', '1매당', '1매입당', '1마리당', '1세트당', '1정당', 
        '링크 발급', '최저가', '내일출발', '오늘출발', '베스트판매자', 
        '전체 보기', '전체보기', '특가', '오늘만'
    ]

    try:
        # Render 클라우드 맞춤형 스마트 무한 스크롤 (최대 40회 / 최소 5회 강제)
        last_height = page.evaluate("document.body.scrollHeight")
        for i in range(40):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            page.wait_for_timeout(1000)  # Render 서버 로딩 대기시간 1초 확보
            
            new_height = page.evaluate("document.body.scrollHeight")
            # 최소 5회 스크롤 이후에만 바닥 감지 동작 수행
            if i >= 5 and new_height == last_height:
                page.wait_for_timeout(1500)  # 지연 로딩 2차 대기
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    print_log(f"   - {i+1}회 스크롤 후 바닥 도달 완료")
                    break
            last_height = new_height

        page.wait_for_timeout(2000)  # 최종 DOM 안정화 대기

        # 전체 카드 구조 포착
        cards = page.locator("article, div[class*='Card'], div[class*='Item'], div[class*='Product'], a[href*='product']").all()
        print_log(f"📍 [{section_name}] 감지된 전체 카드 구조: {len(cards)}개")

        for idx, card in enumerate(cards):
            if len(harvested) >= target_count:
                break
            try:
                raw_text = card.inner_text() if card else ""
                if not raw_text or '원' not in raw_text:
                    continue

                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                
                # 1. 진짜 상품명 후보 추출 (더미/배지/수익금 라인 철저 차단)
                candidate_titles = []
                for l in lines:
                    if len(l) >= 3 and not re.match(r'^[\d,%원\-~★☆.()\s]+$', l):
                        if not any(k in l for k in JUNK_KEYWORDS) and '%' not in l:
                            candidate_titles.append(l)

                if not candidate_titles:
                    continue
                
                title = max(candidate_titles, key=len)  # 가장 긴 텍스트를 진짜 상품명으로 지정
                if title in seen_titles:
                    continue

                # 2. 진짜 결제 판매가 파싱 (단위 가격 및 수익금 라인 차단)
                price_lines = [l for l in lines if '원' in l and not any(k in l for k in ['당 ', '수익', '개당'])]
                valid_prices = []
                for pl in price_lines:
                    prices = re.findall(r'([\d,]+)\s*원', pl)
                    for p in prices:
                        val = int(p.replace(',', ''))
                        if val >= 500:  # 정상 상품가 최소 기준
                            valid_prices.append(val)

                if not valid_prices:
                    continue

                price = min(valid_prices)

                # 3. 할인율 및 배지 파싱
                disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                if disc_match:
                    discount_rate = f"{disc_match.group(1)}%"
                elif '최저가' in raw_text:
                    discount_rate = "최저가"
                else:
                    discount_rate = "특가"

                # 4. 썸네일 및 단축 링크
                img_url = card.evaluate(r"""el => {
                    const img = el.querySelector('img');
                    return img ? (img.currentSrc || img.src || img.getAttribute('data-src') || '') : '';
                }""")
                if not img_url or not img_url.startswith('http'):
                    img_url = "https://static.toss.im/icons/png/4x/icon-toss-logo.png"

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

        print_log(f"✅ [{section_name}] 수집 완료: 총 {len(harvested)}개 정밀 확보!")

    except Exception as sec_err:
        print_log(f"⚠️ [{section_name}] 오류 발생: {sec_err}")

    return harvested


def harvest_sharelink_portal():
    print_log("🚀 [TOSS SHARELINK HARVESTER] 직통 URL 정밀 수집 엔진 가동")

    # Render 환경변수로부터 세션 복원
    setup_session_from_env()

    use_session = os.path.exists(SESSION_PATH)
    all_harvested_deals = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            slow_mo=100,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        ctx_opts = {
            "viewport": {"width": 1280, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR"
        }
        if use_session:
            ctx_opts["storage_state"] = SESSION_PATH
            print_log("🔑 로그인 세션(Storage State) 로드 완료!")

        ctx = browser.new_context(**ctx_opts)
        page = ctx.new_page()

        try:
            # ── 1. '오늘만 이가격' 직통 URL 진입 ──
            url_today = "https://sharelink.toss.im/links/best-ranking/daily-deals?sectionCode=TODAY_DEAL"
            print_log(f"📡 [1/2] 오늘만 이가격 직통 URL 접속 중...\n ➔ {url_today}")
            page.goto(url_today, timeout=30000)
            
            # 카드 엘리먼트 마운트 강제 대기
            try:
                page.wait_for_selector("article, div[class*='Card'], div[class*='Item'], a[href*='product']", timeout=10000)
            except Exception:
                pass
            page.wait_for_timeout(2000)

            today_deals = collect_hybrid_data(page, "오늘만 이가격", "today_price", 1, target_count=200)
            all_harvested_deals.extend(today_deals)

            # ── 2. '지금 많이 팔리는 BEST' 직통 URL 진입 ──
            url_best = "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING"
            print_log(f"📡 [2/2] 지금 많이 팔리는 BEST 직통 URL 접속 중...\n ➔ {url_best}")
            page.goto(url_best, timeout=30000)
            
            # 💡 핵심 보완: 카드 엘리먼트 마운트 강제 대기 (0개 조기 종료 방지)
            try:
                page.wait_for_selector("article, div[class*='Card'], div[class*='Item'], a[href*='product']", timeout=10000)
            except Exception:
                pass
            page.wait_for_timeout(2000)

            best_deals = collect_hybrid_data(page, "BEST 랭킹", "best_seller", 2, target_count=300)
            all_harvested_deals.extend(best_deals)

        except Exception as main_err:
            print_log(f"❌ 전체 예외: {main_err}")

        browser.close()

    print_log(f"🏆 총 {len(all_harvested_deals)}개 정밀 상품 파싱 완결 ➔ DB 저장 진입")
    if all_harvested_deals:
        update_db_with_deals(all_harvested_deals)


def update_db_with_deals(deals):
    target_path = ROOT_DB_PATH
    if not os.path.exists(target_path):
        target_path = WORKER_DB_PATH

    if not os.path.exists(target_path):
        db = {"products": []}
    else:
        with open(target_path, "r", encoding="utf-8") as f:
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
            existing[existing_idx]['original_price'] = int(price * 1.35)
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

    db["products"] = existing[:500]

    with open(ROOT_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    with open(WORKER_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print_log(f"🎉 morvix_shop_db.json DB 저장 완료! (현재 총 {len(db['products'])}개 상품 보유 중)")
    
    push_to_github_automatically()


if __name__ == "__main__":
    harvest_sharelink_portal()