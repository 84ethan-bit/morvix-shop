"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Portal Harvester (Max Yield Harvester V8)
worker/sharelink_toss_harvester.py

[최대 수집 확보 보완]
1. 깊은 무한 스크롤(25회)로 200개+ 숨겨진 카드 마운트
2. 상품 링크(a[href*='product']) & 카드 상자 정밀 타겟팅으로 유효 상품 탈락률 0% 지향
3. 현 구조 유지 (기존 DB 누적 유지) -> 수집량 검증용
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


def push_to_github_automatically():
    """Render 수집 완료 즉시 GH_TOKEN을 활용하여 GitHub & Vercel로 Auto Push"""
    try:
        gh_token = os.environ.get("GH_TOKEN", "").strip()
        print_log("🚀 [AUTO GIT PUSH ENGINE] Render ➔ GitHub 자동 동기화 시도...")

        if os.path.exists(WORKER_DB_PATH):
            shutil.copy(WORKER_DB_PATH, ROOT_DB_PATH)

        if not gh_token:
            print_log("⚠️ [GH_TOKEN 미설정] Render 환경변수 GH_TOKEN을 확인해 주세요.")
            return

        repo_url = f"https://84ethan-bit:{gh_token}@github.com/84ethan-bit/morvix-shop.git"
        
        subprocess.run(["git", "config", "user.name", "Morvix Auto Bot"], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bot@morvix.kr"], cwd=BASE_DIR, capture_output=True)
        
        subprocess.run(["git", "add", "-f", ROOT_DB_PATH], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "add", "-f", WORKER_DB_PATH], cwd=BASE_DIR, capture_output=True)
        
        commit_msg = f"Auto Harvest Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True)
        
        push_res = subprocess.run(["git", "push", repo_url, "main", "--force"], cwd=BASE_DIR, capture_output=True, text=True)
        
        if push_res.returncode == 0:
            print_log("🎉 [AUTO PUSH SUCCESS] 깃허브 반영 완료")
        else:
            print_log(f"⚠️ Git Push 실패: {push_res.stderr.strip()}")

    except Exception as e:
        print_log(f"❌ Auto Git Push 예외: {e}")


def collect_hybrid_data(page, section_name, section_key, priority_val, target_count=300):
    print_log(f"🔎 [{section_name}] 최대 확보 수집 시작 (목표: {target_count}개)...")
    
    harvested = []
    seen_titles = set()

    try:
        # 1. 무한 스크롤 깊게 수행 (25회)
        print_log(f"📜 [{section_name}] 스크롤 다운 진행 중...")
        for _ in range(25):
            page.evaluate("window.scrollBy(0, 1000)")
            page.wait_for_timeout(250)

        page.wait_for_timeout(1000)

        # 2. 카드 요소 다각도 포착 (중복 껍데기 제거하고 상품 단위 요소 추출)
        cards = page.locator("a[href*='product'], div[class*='Product'], div[class*='ItemCard'], article").all()
        print_log(f"📍 [{section_name}] 감지된 전체 카드 구조: {len(cards)}개")

        for idx, card in enumerate(cards):
            if len(harvested) >= target_count:
                break
            try:
                raw_text = card.inner_text() if card else ""
                if not raw_text or '원' not in raw_text:
                    continue

                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                
                # 상품명 유연성 확보 (탈락 최소화)
                candidate_titles = []
                for l in lines:
                    if len(l) >= 3 and not re.match(r'^[\d,%원\-~★☆.()\s]+$', l):
                        if not any(k == l for k in ['링크 발급', '오늘특가', '무료배송', '적립', '오늘출발', '혜택']):
                            candidate_titles.append(l)

                if not candidate_titles:
                    continue
                
                title = max(candidate_titles, key=len)
                if title in seen_titles:
                    continue

                # 가격 정밀 파싱
                prices = re.findall(r'([\d,]+)\s*원', raw_text)
                valid_prices = []
                for p in prices:
                    num = int(p.replace(',', ''))
                    if 500 <= num <= 20000000:
                        valid_prices.append(num)

                if not valid_prices:
                    continue
                price = min(valid_prices)

                # 할인율
                disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                discount_rate = f"{disc_match.group(1)}%" if disc_match else ""

                # 썸네일
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

        print_log(f"✅ [{section_name}] 최종 유효 수집 완료: 총 {len(harvested)}개 확보!")
    except Exception as sec_err:
        print_log(f"⚠️ [{section_name}] 오류 발생: {sec_err}")

    return harvested


def harvest_sharelink_portal():
    print_log("🚀 [TOSS SHARELINK HARVESTER] 최대 수집 확보 파서 가동")

    use_session = os.path.exists(SESSION_PATH)
    all_harvested_deals = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        ctx_opts = {
            "viewport": {"width": 1280, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR"
        }
        if use_session:
            ctx_opts["storage_state"] = SESSION_PATH

        ctx = browser.new_context(**ctx_opts)
        page = ctx.new_page()

        try:
            print_log("📡 https://sharelink.toss.im/home 접속 중...")
            page.goto("https://sharelink.toss.im/home", timeout=30000)
            page.wait_for_timeout(3000)

            # 1. 하루특가 수집
            print_log("━━━ [1순위] 하루특가 영역 수집 ━━━")
            try:
                page.evaluate("""() => {
                    const btns = [...document.querySelectorAll('button, a, div, span')];
                    for (const b of btns) {
                        const txt = (b.innerText || '').trim();
                        if (txt === '하루특가' || txt === '오늘만 이 가격' || txt.includes('하루특가')) {
                            b.click();
                            return true;
                        }
                    }
                    return false;
                }""")
                page.wait_for_timeout(2500)

                today_deals = collect_hybrid_data(page, "하루특가", "today_price", 1, target_count=300)
                all_harvested_deals.extend(today_deals)
            except Exception as e:
                print_log(f"❌ 하루특가 예외: {e}")

            # 2. BEST 수집
            print_log("━━━ [2순위] BEST 영역 수집 ━━━")
            try:
                page.goto("https://sharelink.toss.im/home", timeout=30000)
                page.wait_for_timeout(2000)

                page.evaluate("""() => {
                    const btns = [...document.querySelectorAll('button, a, div, span')];
                    for (const b of btns) {
                        const txt = (b.innerText || '').trim();
                        if (txt === 'BEST' || txt.includes('베스트') || txt.includes('인기')) {
                            b.click();
                            return true;
                        }
                    }
                    return false;
                }""")
                page.wait_for_timeout(2500)

                best_deals = collect_hybrid_data(page, "BEST 랭킹", "best_seller", 2, target_count=300)
                all_harvested_deals.extend(best_deals)
            except Exception as e:
                print_log(f"❌ BEST 예외: {e}")

        except Exception as main_err:
            print_log(f"❌ 전체 예외: {main_err}")

        browser.close()

    print_log(f"🏆 총 {len(all_harvested_deals)}개 신규 수집 완료 ➔ DB 저장 진입")
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

    print_log(f"🎉 morvix_shop_db.json DB 저장 완료! (현재 총 {len(db['products'])}개 상품 유지 중)")
    
    push_to_github_automatically()


if __name__ == "__main__":
    harvest_sharelink_portal()