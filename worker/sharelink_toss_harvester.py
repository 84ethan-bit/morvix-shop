"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Portal Harvester (V61 - Stronger Filtering Fix)
worker/sharelink_toss_harvester.py
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

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKER_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
WORKER_DB_PATH = os.path.join(WORKER_DIR, "morvix_shop_db.json")
SESSION_DIR = os.path.join(BASE_DIR, "scratch")
SESSION_PATH = os.path.join(SESSION_DIR, "toss_sharelink_session.json")


def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [1번 수집기] {msg}", flush=True)


def setup_session_from_env():
    env_session = os.environ.get("TOSS_SESSION_JSON", "").strip()
    if env_session:
        try:
            os.makedirs(SESSION_DIR, exist_ok=True)
            with open(SESSION_PATH, "w", encoding="utf-8") as f:
                f.write(env_session)
            print_log("🔑 환경 변수에서 세션 복원 완료")
        except Exception as e:
            print_log(f"⚠️ 세션 복원 예외: {e}")


def push_to_github_automatically():
    try:
        gh_token = os.environ.get("GH_TOKEN", "").strip()
        print_log("🚀 깃허브 자동 동기화 시도...")

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
        
        commit_msg = f"Auto Sync Today Deals (V61 Strong Filter): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
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


def harvest_today_deals_exclusively(page):
    print_log("🔎 [오늘만 이가격] 강력 필터링 스마트 스크롤 수집 엔진 가동...")
    
    harvested = []
    seen_titles = set()

    # 💡 정크 키워드 대폭 강화 (UI 문구 및 배송/이벤트성 잡다한 텍스트 차단)
    JUNK_KEYWORDS = [
        '수익', '당 ', '개당', '100g', '100ml', '10g', '1포당', 
        '1롤당', '1매당', '1매입당', '1마리당', '1세트당', '1정당', '1미당',
        '링크 발급', '최저가', '내일출발', '오늘출발', '베스트판매자', 
        '전체 보기', '전체보기', '특가', '오늘만', '늦으면보상', '무료배송',
        '배송보장', '쿠폰받기', '혜택받기', '포인트'
    ]

    try:
        page.evaluate("""
            const style = document.createElement('style');
            style.innerHTML = `
                body { zoom: 75%; }
                main, div[class*="content"], div[class*="container"] { max-width: 100% !important; margin: 0 auto !important; }
            `;
            document.head.appendChild(style);
        """)
        page.wait_for_timeout(1000)

        print_log("📜 '오늘만 이가격' 하단 로딩 스크롤 진행 중...")
        last_height = page.evaluate("document.body.scrollHeight")
        same_height_count = 0

        for step in range(30):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            page.wait_for_timeout(2000)
            
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                same_height_count += 1
                if same_height_count >= 3:
                    print_log(f"🛑 [스크롤 완료] (총 {step + 1}회 시도)")
                    break
            else:
                same_height_count = 0
                last_height = new_height

        page.wait_for_timeout(2000)

        btn_locators = page.locator("button:has-text('링크 발급')").all()
        print_log(f"📍 감지된 [링크 발급] 버튼: 총 {len(btn_locators)}개")

        for idx, btn in enumerate(btn_locators):
            try:
                card = btn.locator("xpath=ancestor::*[contains(@class, 'Card') or contains(@class, 'Item') or contains(@class, 'Product') or self::article or self::section][1]")
                if not card or not card.count():
                    card = btn.locator("xpath=ancestor::div[3]")

                raw_text = card.inner_text() if card.count() else ""
                if not raw_text or '원' not in raw_text:
                    continue

                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                
                candidate_titles = []
                for l in lines:
                    # 💡 정크 키워드가 포함된 줄은 후보에서 강력하게 제외
                    if any(jk in l for jk in JUNK_KEYWORDS):
                        continue
                    if re.search(r'\d+.*당', l) or re.search(r'^\d+%\s*특가', l):
                        continue
                    if len(l) >= 4 and not re.match(r'^[\d,%원\-~★☆.()\s]+$', l):
                        if '%' not in l:
                            candidate_titles.append(l)

                if not candidate_titles:
                    continue
                
                raw_title = max(candidate_titles, key=len)
                title = clean_product_name(raw_title)
                
                # 💡 최종 타이틀이 정크 키워드와 정확히 일치하거나 너무 짧으면 스킵
                if not title or title in seen_titles or title in JUNK_KEYWORDS or len(title) < 3:
                    continue

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
                else:
                    discount_rate = "특가"

                img_url = card.evaluate(r"""el => {
                    const img = el.querySelector('img');
                    return img ? (img.currentSrc || img.src || img.getAttribute('data-src') || '') : '';
                }""")
                if not img_url or not img_url.startswith('http'):
                    img_url = "https://static.toss.im/icons/png/4x/icon-toss-logo.png"

                real_toss_link = None
                try:
                    btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(300)
                    btn.click(force=True)
                    page.wait_for_timeout(2000)

                    clip_content = page.evaluate("async () => await navigator.clipboard.readText()").strip()
                    if clip_content:
                        match_link = re.search(r'https:\/\/toss\.im\/_m\/[a-zA-Z0-9]+', clip_content)
                        if match_link:
                            real_toss_link = match_link.group(0)
                except Exception:
                    pass

                if not real_toss_link:
                    extracted_url = card.evaluate(r"""el => {
                        const allEls = Array.from(el.querySelectorAll('a, input, textarea'));
                        for (const el of allEls) {
                            const href = el.href || el.value || '';
                            if (href && href.includes('toss.im/_m/')) {
                                return href.trim();
                            }
                        }
                        return '';
                    }""")
                    if extracted_url:
                        match_link = re.search(r'https:\/\/toss\.im\/_m\/[a-zA-Z0-9]+', extracted_url)
                        if match_link:
                            real_toss_link = match_link.group(0)

                if not real_toss_link:
                    prod_id_match = re.search(r'/product/(\d+)', img_url) or re.search(r'/ai/([a-zA-Z0-9_-]+)', img_url)
                    if prod_id_match:
                        token_id = prod_id_match.group(1)
                        real_toss_link = f"https://sharelink.toss.im/links/product?id={token_id}"
                    else:
                        continue

                seen_titles.add(title)
                harvested.append({
                    "name": title,
                    "price": price,
                    "discount_rate": discount_rate,
                    "thumbnail": img_url,
                    "share_link": real_toss_link,
                    "section": "today_price",
                    "priority": 1
                })

            except Exception:
                continue

        print_log(f"✅ 정제된 수집 완료: 총 {len(harvested)}개")

    except Exception as sec_err:
        print_log(f"⚠️ 오류 발생: {sec_err}")

    return harvested


def harvest_sharelink_portal():
    print_log("🚀 스마트 스크롤 수집 엔진 가동 (Firefox)")
    setup_session_from_env()

    use_session = os.path.exists(SESSION_PATH)
    all_harvested_deals = []

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True, slow_mo=100)
        
        ctx_opts = {
            "viewport": {"width": 1440, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR"
        }
        if use_session:
            ctx_opts["storage_state"] = SESSION_PATH
            print_log("🔑 로그인 세션 파일 로드 완료!")

        ctx = browser.new_context(**ctx_opts)
        page = ctx.new_page()

        try:
            url_home = "https://sharelink.toss.im/home"
            print_log(f"📡 토스 쉐어링크 홈 접속 중: {url_home}")
            page.goto(url_home, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            
            try:
                page.wait_for_url("**/home**", timeout=120000)
                page.wait_for_timeout(3000)
                
                os.makedirs(SESSION_DIR, exist_ok=True)
                ctx.storage_state(path=SESSION_PATH)
            except Exception:
                pass

            print_log("🖱️ '오늘만 이가격' 섹션 탐색 및 클릭 시도...")
            try:
                full_view_btn = page.locator("text='오늘만 이 가격에 살 수 있는 하루특가'").locator("xpath=following::*[contains(text(), '전체 보기') or contains(text(), '전체보기')][1]")
                if not full_view_btn.count():
                    full_view_btn = page.locator("text='전체 보기'").first
                
                if full_view_btn.count() > 0:
                    full_view_btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    full_view_btn.click(force=True)
                    page.wait_for_timeout(3000)
            except Exception:
                pass

            all_harvested_deals.extend(harvest_today_deals_exclusively(page))

        except Exception as main_err:
            print_log(f"❌ 전체 예외: {main_err}")

        try:
            os.makedirs(SESSION_DIR, exist_ok=True)
            ctx.storage_state(path=SESSION_PATH)
        except Exception:
            pass

        browser.close()

    if all_harvested_deals:
        update_db_with_deals(all_harvested_deals)
    else:
        print_log("⚠️ 수집된 상품이 0개입니다.")


def update_db_with_deals(deals):
    db = {"products": []}
    now = datetime.now()
    count_added = 0

    for d in deals:
        name = d.get('name', '').strip()
        price = d.get('price', 0)
        discount = d.get('discount_rate', '')
        thumb = d.get('thumbnail', '')
        share_link = d.get('share_link', '')

        if len(name) < 2 or price < 500 or not share_link or share_link == "https://sharelink.toss.im":
            continue

        slug = f"toss_{int(time.time())}_{count_added}"
        prod_entry = {
            "id": f"TOSS-AUTO-{int(time.time())}-{count_added}",
            "slug": slug,
            "short_url": f"morvix.kr/{slug}",
            "name": name,
            "subtitle": f"토스 파트너 특가 {discount} 적용",
            "section": d.get("section", "today_price"),
            "priority": d.get("priority", 1),
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
            "expiry_date": (now + timedelta(hours=48)).isoformat()
        }
        db["products"].append(prod_entry)
        count_added += 1

    os.makedirs(os.path.dirname(ROOT_DB_PATH), exist_ok=True)
    with open(ROOT_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    with open(WORKER_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print_log(f"🎉 정제된 DB 적재 완료 (총 {len(db['products'])}개)")
    push_to_github_automatically()


if __name__ == "__main__":
    harvest_sharelink_portal()