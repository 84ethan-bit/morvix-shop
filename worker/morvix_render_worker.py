"""
=============================================================================
MORVIX SHOP OS - BEST Ranking Harvester (Smart Auto-Login & Stable Harvester)
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

# 💡 토스 계정 정보 (환경변수 또는 직접 입력)
TOSS_ID = os.environ.get("TOSS_ID", "YOUR_TOSS_ID")
TOSS_PW = os.environ.get("TOSS_PW", "YOUR_TOSS_PASSWORD")


def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def setup_session_from_env():
    env_session = os.environ.get("TOSS_SESSION_JSON", "").strip()
    if env_session:
        try:
            os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
            with open(SESSION_PATH, "w", encoding="utf-8") as f:
                f.write(env_session)
            print_log("🔑 BEST 수집기 환경변수 세션 복원 완료")
        except Exception as e:
            print_log(f"⚠️ 세션 복원 예외: {e}")


def push_to_github_automatically():
    try:
        gh_token = os.environ.get("GH_TOKEN", "").strip()
        print_log("🚀 [최종 통합] 깃허브 자동 동기화 시도...")

        if os.path.exists(WORKER_DB_PATH):
            shutil.copy(WORKER_DB_PATH, ROOT_DB_PATH)

        if not gh_token:
            print_log("ℹ️ [GH_TOKEN 미설정] 로컬 테스트 완료 (Push 스킵)")
            return

        repo_url = f"https://x-access-token:{gh_token}@github.com/84ethan-bit/morvix-shop.git"
        
        subprocess.run(["git", "config", "user.name", "Morvix Auto Bot"], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bot@morvix.kr"], cwd=BASE_DIR, capture_output=True)
        
        subprocess.run(["git", "add", "-f", ROOT_DB_PATH], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "add", "-f", WORKER_DB_PATH], cwd=BASE_DIR, capture_output=True)
        
        commit_msg = f"Auto Sync Final Integrated Deals (V56 Pipeline): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True)
        
        push_res = subprocess.run(["git", "push", repo_url, "HEAD:main", "--force"], cwd=BASE_DIR, capture_output=True, text=True)
        
        if push_res.returncode == 0:
            print_log("🎉 [최종 통합] 깃허브 푸시 성공!")
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
    print_log("🏆 [BEST 수집 엔진] 스마트 자동 로그인 및 수집 가동...")
    setup_session_from_env()
    
    harvested = []
    seen_titles = set()

    JUNK_KEYWORDS = [
        '수익', '당 ', '개당', '100g', '100ml', '10g', '1포당', 
        '1롤당', '1매당', '1매입당', '1마리당', '1세트당', '1정당', '1미당',
        '링크 발급', '최저가', '내일출발', '오늘출발', '베스트판매자', 
        '전체 보기', '전체보기', '특가', '역대급특가'
    ]

    use_session = False
    if os.path.exists(SESSION_PATH):
        try:
            with open(SESSION_PATH, "r", encoding="utf-8") as f:
                session_data = json.load(f)
                if "cookies" in session_data and isinstance(session_data["cookies"], list):
                    use_session = True
                    print_log(f"🔑 세션 파일 검증 통과 (쿠키 개수: {len(session_data['cookies'])}개)")
        except Exception as e:
            print_log(f"⚠️ 세션 파일 파싱 오류 발생: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 서버 환경에서는 True로 변경 가능 (디버깅 시 False)
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

        ctx = browser.new_context(**ctx_opts)
        ctx.grant_permissions(["clipboard-read", "clipboard-write"])
        page = ctx.new_page()

        try:
            url_best = "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING"
            print_log(f"📡 BEST 전체보기 페이지 접속 중: {url_best}")
            page.goto(url_best, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)

            # 💡 [자동 로그인 감지 및 처리 로직]
            # 페이지에 로그인 관련 입력창이나 로그인 버튼이 감지되면 자동 로그인 시도
            if "login" in page.url or page.locator("input[type='text'], input[type='tel']").count() > 0:
                print_log("⚠️ [세션 만료 감지] 로그인 페이지로 진입했습니다. 자동 로그인을 시도합니다...")
                try:
                    # 아이디/전화번호 입력란 찾기
                    id_input = page.locator("input[type='text'], input[type='tel']").first()
                    if id_input.count() > 0:
                        id_input.fill(TOSS_ID)
                        page.wait_for_timeout(500)
                        
                        # 다음 버튼 또는 비밀번호 입력란 처리
                        next_btn = page.locator("button:has-text('다음'), button:has-text('확인'), button[type='submit']").first()
                        if next_btn.count() > 0:
                            next_btn.click()
                            page.wait_for_timeout(2000)

                    # 비밀번호 입력란이 나타나면 입력
                    pw_input = page.locator("input[type='password']").first()
                    if pw_input.count() > 0:
                        pw_input.fill(TOSS_PW)
                        page.wait_for_timeout(500)
                        
                        login_btn = page.locator("button:has-text('로그인'), button:has-text('확인'), button[type='submit']").first()
                        if login_btn.count() > 0:
                            login_btn.click()
                            print_log("🔄 로그인 정보 제출 완료. 인증 대기 중 (10초)...")
                            page.wait_for_timeout(10000)

                    # 로그인 성공 후 원래 목적지 페이지로 다시 이동
                    page.goto(url_best, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(4000)

                    # 💡 새로 갱신된 세션(쿠키)을 자동으로 파일에 저장하여 다음 실행 시 재사용
                    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
                    ctx.storage_state(path=SESSION_PATH)
                    print_log("🎉 [자동 갱신] 새로운 로그인 세션(쿠키)이 성공적으로 저장되었습니다!")

                except Exception as login_err:
                    print_log(f"❌ 자동 로그인 과정 중 예외 발생: {login_err}")

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

                for idx, btn in enumerate(unprocessed_buttons):
                    try:
                        total_processed += 1
                        
                        try:
                            btn.scroll_into_view_if_needed()
                            page.wait_for_timeout(100)
                        except Exception:
                            pass

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

    if harvested:
        db = {"products": []}
        now = datetime.now()
        
        target_main_db = ROOT_DB_PATH if os.path.exists(ROOT_DB_PATH) else WORKER_DB_PATH
        
        existing_products = []
        if os.path.exists(target_main_db):
            try:
                with open(target_main_db, "r", encoding="utf-8") as f:
                    data = json.load(f)
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

        db["products"] = existing_products + best_products

        for path_target in [ROOT_DB_PATH, WORKER_DB_PATH]:
            try:
                with open(path_target, "w", encoding="utf-8") as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        print_log(f"🎉 [통합 DB 적재 완료] 오늘만 이가격({len(existing_products)}개) + BEST 상품({len(best_products)}개) ➔ 총 {len(db['products'])}개 통합 DB 구축 완료!")
        
        push_to_github_automatically()


if __name__ == "__main__":
    harvest_best_ranking_exclusively()