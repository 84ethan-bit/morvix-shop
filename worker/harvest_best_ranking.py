"""
=============================================================================
MORVIX SHOP OS - BEST Ranking Harvester (Worker 2)
worker/harvest_best_ranking.py
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

TOSS_ID = os.environ.get("TOSS_ID", "YOUR_TOSS_ID")
TOSS_PW = os.environ.get("TOSS_PW", "YOUR_TOSS_PASSWORD")

def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [WORKER 2] {msg}", flush=True)

def setup_session_from_env():
    env_session = os.environ.get("TOSS_SESSION_JSON", "").strip()
    if env_session:
        try:
            os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
            with open(SESSION_PATH, "w", encoding="utf-8") as f:
                f.write(env_session)
            print_log("🔑 2번 수집기 환경변수 세션 복원 완료")
        except Exception as e:
            print_log(f"⚠️ 세션 복원 예외: {e}")

def push_to_github_automatically():
    try:
        gh_token = os.environ.get("GH_TOKEN", "").strip()
        print_log("🚀 깃허브 자동 동기화 시도...")

        if os.path.exists(WORKER_DB_PATH):
            shutil.copy(WORKER_DB_PATH, ROOT_DB_PATH)

        if not gh_token:
            print_log("ℹ️ GH_TOKEN 미설정 (푸시 스킵)")
            return

        repo_url = f"https://x-access-token:{gh_token}@github.com/84ethan-bit/morvix-shop.git"
        
        subprocess.run(["git", "config", "user.name", "Morvix Auto Bot"], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bot@morvix.kr"], cwd=BASE_DIR, capture_output=True)
        
        subprocess.run(["git", "add", "-f", ROOT_DB_PATH], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "add", "-f", WORKER_DB_PATH], cwd=BASE_DIR, capture_output=True)
        
        commit_msg = f"Auto Sync Pipeline V56: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True)
        
        push_res = subprocess.run(["git", "push", repo_url, "HEAD:main", "--force"], cwd=BASE_DIR, capture_output=True, text=True)
        
        if push_res.returncode == 0:
            print_log("🎉 깃허브 푸시 성공!")
        else:
            print_log(f"⚠️ Git Push 실패: {push_res.stderr.strip()}")
    except Exception as e:
        print_log(f"❌ Auto Git Push 예외: {e}")

def clean_product_name(raw_name):
    if not raw_name:
        return ""
    cleaned = re.sub(r'개당\s*[\d,]+원\s*수익', '', raw_name)
    cleaned = re.sub(r'[\d,]+원\s*수익', '', cleaned)
    cleaned = re.sub(r'수익금?\s*[\d,]+원', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned.lstrip(',').lstrip('-').strip() if len(cleaned.lstrip(',').lstrip('-').strip()) >= 2 else raw_name

def harvest_best_ranking_exclusively():
    print_log("🏆 [BEST 랭킹] 수집 엔진 가동...")
    setup_session_from_env()
    
    harvested = []
    seen_titles = set()
    use_session = os.path.exists(SESSION_PATH)

    JUNK_KEYWORDS = [
        '수익', '당 ', '개당', '100g', '100ml', '10g', '1포당', 
        '1롤당', '1매당', '1매입당', '1마리당', '1세트당', '1정당', '1미당',
        '링크 발급', '최저가', '내일출발', '오늘출발', '베스트판매자', 
        '전체 보기', '전체보기', '특가', '역대급특가'
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        
        ctx_opts = {
            "viewport": {"width": 1440, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR",
            "permissions": ["clipboard-read", "clipboard-write"]
        }
        if use_session:
            ctx_opts["storage_state"] = SESSION_PATH

        ctx = browser.new_context(**ctx_opts)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        page = ctx.new_page()

        try:
            url_best = "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING"
            print_log(f"📡 페이지 접속 중: {url_best}")
            page.goto(url_best, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

            if "login" in page.url or page.locator("input[type='text'], input[type='tel']").count() > 0:
                print_log("⚠️ 로그인 필요 감지. 자동 로그인 시도...")
                try:
                    id_inp = page.locator("input[type='text'], input[type='tel']").first()
                    if id_inp.count() > 0:
                        id_inp.fill(TOSS_ID)
                        page.wait_for_timeout(500)
                        nxt = page.locator("button:has-text('다음'), button:has-text('확인')").first()
                        if nxt.count() > 0:
                            nxt.click()
                            page.wait_for_timeout(2000)

                    pw_inp = page.locator("input[type='password']").first()
                    if pw_inp.count() > 0:
                        pw_inp.fill(TOSS_PW)
                        page.wait_for_timeout(500)
                        l_btn = page.locator("button:has-text('로그인'), button:has-text('확인')").first()
                        if l_btn.count() > 0:
                            l_btn.click()
                            page.wait_for_timeout(8000)

                    page.goto(url_best, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(4000)
                    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
                    ctx.storage_state(path=SESSION_PATH)
                    print_log("🎉 신규 세션 갱신 및 저장 완료")
                except Exception as ex:
                    print_log(f"⚠️ 자동 로그인 실패: {ex}")

            for step in range(12):
                page.evaluate("window.scrollBy(0, 1500);")
                page.wait_for_timeout(3000)

            buttons = page.locator("button:has-text('링크 발급')").all()
            print_log(f"🔍 발견된 링크 발급 버튼: {len(buttons)}개")

            for btn in buttons:
                try:
                    card = btn.locator("xpath=ancestor::*[contains(@class, 'Card') or contains(@class, 'Item') or contains(@class, 'Product') or self::article or self::section][1]")
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
                    if not title or title in seen_titles:
                        continue

                    prices = re.findall(r'([\d,]+)\s*원', raw_text)
                    valid_prices = [int(p.replace(',', '')) for p in prices if int(p.replace(',', '')) >= 500]
                    if not valid_prices:
                        continue
                    price = min(valid_prices)

                    disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                    discount_rate = f"{disc_match.group(1)}%" if disc_match else "BEST 특가"

                    real_toss_link = None
                    try:
                        btn.click(force=True)
                        page.wait_for_timeout(300)
                        clip_content = page.evaluate("async () => await navigator.clipboard.readText()").strip()
                        if clip_content:
                            match_link = re.search(r'https:\/\/toss\.im\/_m\/[a-zA-Z0-9]+', clip_content)
                            if match_link:
                                real_toss_link = match_link.group(0)
                    except Exception:
                        pass

                    if not real_toss_link:
                        real_toss_link = f"https://sharelink.toss.im/links/best-ranking"

                    seen_titles.add(title)
                    harvested.append({
                        "name": title,
                        "price": price,
                        "discount_rate": discount_rate,
                        "thumbnail": "https://static.toss.im/icons/png/4x/icon-toss-logo.png",
                        "share_link": real_toss_link,
                        "section": "best_ranking",
                        "priority": 2
                    })
                except Exception:
                    continue

            print_log(f"✅ BEST 수집 완료: 총 {len(harvested)}개")
        except Exception as err:
            print_log(f"❌ BEST 수집 예외: {err}")
        finally:
            browser.close()

    if harvested:
        db = {"products": []}
        now = datetime.now()
        
        existing_products = []
        if os.path.exists(ROOT_DB_PATH):
            try:
                with open(ROOT_DB_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    existing_products = [p for p in data.get("products", []) if p.get("section") == "today_price"]
            except Exception:
                pass

        best_products = []
        for i, d in enumerate(harvested):
            slug = f"toss_best_{int(time.time())}_{i}"
            best_products.append({
                "id": f"TOSS-BEST-{int(time.time())}-{i}",
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
                "affiliate_links": [{"platform": "toss", "label": "💙 토스할인가 확인 ➔", "url": d['share_link'], "priority": 1}],
                "thumbnail": d['thumbnail'],
                "added_date": now.isoformat(),
                "expiry_date": (now + timedelta(hours=48)).isoformat()
            })

        db["products"] = existing_products + best_products

        for path_target in [ROOT_DB_PATH, WORKER_DB_PATH]:
            try:
                os.makedirs(os.path.dirname(path_target), exist_ok=True)
                with open(path_target, "w", encoding="utf-8") as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        print_log(f"🎉 통합 DB 적재 완료 (총 {len(db['products'])}개)")
        push_to_github_automatically()

if __name__ == "__main__":
    harvest_best_ranking_exclusively()