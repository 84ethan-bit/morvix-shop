"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Portal Harvester (Direct URL Perfect V18 - Render Final)
worker/sharelink_toss_harvester.py

[직통 URL 전용 100% 수집 엔진]
1. 오늘만 이가격 직통: https://sharelink.toss.im/links/best-ranking/daily-deals?sectionCode=TODAY_DEAL
2. 지금 많이 팔리는 BEST 직통: https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING
3. Render 외부 서버 세션 복원 & Git Auto Push 완결판
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
        
        commit_msg = f"Auto Sync Toss Deals: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True)
        
        push_res = subprocess.run(["git", "push", repo_url, "HEAD:main", "--force"], cwd=BASE_DIR, capture_output=True, text=True)
        
        if push_res.returncode == 0:
            print_log("🎉 [AUTO PUSH SUCCESS] 깃허브 및 쇼핑몰 반영 완료!")
        else:
            print_log(f"⚠️ Git Push 실패: {push_res.stderr.strip()}")

    except Exception as e:
        print_log(f"❌ Auto Git Push 예외: {e}")


def collect_hybrid_data(page, section_name, section_key, priority_val, target_count=300):
    print_log(f"🔎 [{section_name}] 전수 수집 스크롤 다운 시작...")
    
    harvested = []
    seen_titles = set()

    try:
        # 무한 스크롤 다운 (35회)
        for _ in range(35):
            page.evaluate("window.scrollBy(0, 1000)")
            page.wait_for_timeout(250)

        page.wait_for_timeout(1500)

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
                
                candidate_titles = []
                for l in lines:
                    if len(l) >= 3 and not re.match(r'^[\d,%원\-~★☆.()\s]+$', l):
                        if not any(k in l for k in ['링크 발급', '개당', '수익', '최저가', '내일출발', '오늘출발', '베스트판매자', '전체 보기', '전체보기']):
                            candidate_titles.append(l)

                if not candidate_titles:
                    continue
                
                title = max(candidate_titles, key=len)
                if title in seen_titles:
                    continue

                prices = re.findall(r'([\d,]+)\s*원', raw_text)
                valid_prices = [int(p.replace(',', '')) for p in prices if int(p.replace(',', '')) >= 500]

                if not valid_prices:
                    continue
                price = min(valid_prices)

                disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                if disc_match:
                    discount_rate = f"{disc_match.group(1)}%"
                elif '최저가' in raw_text:
                    discount_rate = "최저가"
                else:
                    discount_rate = "특가"

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

        print_log(f"✅ [{section_name}] 수집 완료: 총 {len(harvested)}개 확보!")

    except Exception as sec_err:
        print_log(f"⚠️ [{section_name}] 오류 발생: {sec_err}")

    return harvested


def harvest_sharelink_portal():
    print_log("🚀 [TOSS SHARELINK HARVESTER] 직통 URL 무적 수집 엔진 가동")

    # Render 환경변수로부터 세션 복원
    setup_session_from_env()

    use_session = os.path.exists(SESSION_PATH)
    all_harvested_deals = []

    with sync_playwright() as p:
        # Render 서버 환경 대응 headless=True 및 스텔스 옵션
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
            page.wait_for_timeout(3000)

            today_deals = collect_hybrid_data(page, "오늘만 이가격", "today_price", 1, target_count=200)
            all_harvested_deals.extend(today_deals)

            # ── 2. '지금 많이 팔리는 BEST' 직통 URL 진입 ──
            url_best = "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING"
            print_log(f"📡 [2/2] 지금 많이 팔리는 BEST 직통 URL 접속 중...\n ➔ {url_best}")
            page.goto(url_best, timeout=30000)
            page.wait_for_timeout(3000)

            best_deals = collect_hybrid_data(page, "BEST 랭킹", "best_seller", 2, target_count=300)
            all_harvested_deals.extend(best_deals)

        except Exception as main_err:
            print_log(f"❌ 전체 예외: {main_err}")

        browser.close()

    print_log(f"🏆 총 {len(all_harvested_deals)}개 상품 파싱 완결 ➔ DB 저장 진입")
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