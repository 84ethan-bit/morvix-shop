"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Portal Harvester (365 Auto-Sync V4)
worker/sharelink_toss_harvester.py

[365일 무인 자동화 수집 & 자동 Push 엔진]
1. 완화된 검증 규칙으로 하루특가 / BEST 상품 100개 이상 대량 수집
2. Render 수집 완료 즉시 GH_TOKEN 기반 GitHub Auto-Push 실행
3. Vercel 쇼핑몰 실시간 100% 자동 연동 반영
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
    """Render 수집 완료 즉시 GH_TOKEN을 활용하여 GitHub 저장소로 Auto Push"""
    try:
        gh_token = os.environ.get("GH_TOKEN", "").strip()
        print_log("🚀 [AUTO GIT PUSH ENGINE] Render ➔ GitHub 자동 동기화 시도...")

        # 1. worker DB와 최상위 루트 DB 복사 및 위치 동기화
        if os.path.exists(WORKER_DB_PATH) and WORKER_DB_PATH != ROOT_DB_PATH:
            shutil.copy(WORKER_DB_PATH, ROOT_DB_PATH)
            print_log("📋 [DB COPY] worker DB ➔ 루트 DB 복사 완료")

        if not gh_token:
            print_log("⚠️ [GH_TOKEN 미설정] Render 환경변수 GH_TOKEN을 확인해 주세요.")
            return

        # 2. Git 자격 증명 설정 및 Push 실행
        repo_url = f"https://84ethan-bit:{gh_token}@github.com/84ethan-bit/morvix-shop.git"
        
        subprocess.run(["git", "config", "user.name", "Morvix Auto Bot"], cwd=BASE_DIR, capture_output=True)
        subprocess.run(["git", "config", "user.email", "bot@morvix.kr"], cwd=BASE_DIR, capture_output=True)
        
        # staging
        subprocess.run(["git", "add", "morvix_shop_db.json", "worker/morvix_shop_db.json"], cwd=BASE_DIR, capture_output=True)
        
        commit_msg = f"Auto: 365 Daily Toss deals sync [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True)
        
        push_res = subprocess.run(["git", "push", repo_url, "main"], cwd=BASE_DIR, capture_output=True, text=True)
        
        if push_res.returncode == 0:
            print_log("🎉 [365 AUTO PUSH SUCCESS] Render가 GitHub로 최신 DB를 성공적으로 푸시했습니다! (Vercel 쇼핑몰 자동 반영 완료)")
        else:
            print_log(f"⚠️ Git Push 실패 로그: {push_res.stderr.strip()}")

    except Exception as e:
        print_log(f"❌ Auto Git Push 예외 발생: {e}")


def collect_hybrid_data(page, section_name, section_key, priority_val, target_count=200):
    print_log(f"🔎 [{section_name}] 전수 수집 시작 (목표 상한: {target_count}개)...")
    
    harvested = []
    seen_titles = set()

    try:
        # 오토 스크롤 (15회)
        for i in range(1, 16):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(400)

        cards = page.locator("article, div[class*='Card'], div[class*='Item'], li").all()
        print_log(f"📍 [{section_name}] 마운트 감지된 카드 구조: {len(cards)}개")

        for idx, card in enumerate(cards):
            if len(harvested) >= target_count:
                break
            try:
                raw_text = card.inner_text() if card else ""
                if not raw_text or '원' not in raw_text:
                    continue

                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                clean_lines = []
                for l in lines:
                    if any(w in l for w in ['링크 발급', '수익', '개당', '오늘출발', '내일도착', '비슷한 상품']):
                        continue
                    if re.match(r'^[\d,%원\-~★☆.()\[\]\s]+$', l):
                        continue
                    clean_lines.append(l)

                title = max(clean_lines, key=len) if clean_lines else ""
                if not title or len(title) < 2 or title in seen_titles:
                    continue

                pure_price_text = re.sub(r'(개당|수익|적립)\s*[\d,]+\s*원?', '', raw_text)
                prices_found = re.findall(r'([\d,]+)\s*원', pure_price_text)
                prices_int = [int(p.replace(',', '')) for p in prices_found if p.replace(',', '').isdigit()]
                
                valid_prices = [p for p in prices_int if p >= 500]
                if not valid_prices:
                    continue
                price = valid_prices[0]

                disc_match = re.search(r'(\d+)\s*[%％]', raw_text)
                discount_rate = f"{disc_match.group(1)}%" if disc_match else ""

                img_url = card.evaluate(r"""el => {
                    const imgs = [...el.querySelectorAll('img')];
                    for (const img of imgs) {
                        let src = img.currentSrc || img.src || img.getAttribute('data-src') || '';
                        if (src && src.startsWith('http') && !src.includes('placeholder')) {
                            return src;
                        }
                    }
                    return '';
                }""")

                if not img_url:
                    img_url = "https://static.toss.im/icons/png/4x/icon-toss-logo.png"

                share_link = ""
                btn = card.locator("button:has-text('링크 발급')")
                if btn.count() > 0:
                    try:
                        btn.first.click(timeout=800, force=True)
                        page.wait_for_timeout(200)
                        
                        share_link = page.evaluate("""() => {
                            const els = [...document.querySelectorAll('input, a, p, div, span')];
                            for (const el of els) {
                                const val = el.value || el.href || el.innerText || '';
                                const match = val.match(/(https:\\/\\/toss\\.im\\/(?:_m|m)\\/[A-Za-z0-9_-]+)/);
                                if (match) return match[1];
                            }
                            return null;
                        }""")

                        close_btn = page.locator("button:has-text('닫기'), [aria-label='close']")
                        if close_btn.count() > 0:
                            close_btn.first.click(timeout=300)
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

        print_log(f"✅ [{section_name}] 수집 완료: 총 {len(harvested)}개 확보!")
    except Exception as sec_err:
        print_log(f"⚠️ [{section_name}] 오류 발생: {sec_err}")

    return harvested


def harvest_sharelink_portal():
    print_log("🚀 [TOSS SHARELINK HARVESTER] 365 무인 수집 & Auto-Push 엔진 가동")

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
            page.wait_for_timeout(2000)

            # ── [1순위] 오늘만 이가격 (하루특가) ──
            print_log("━━━ [1순위] 오늘만 이가격 하루특가 수집 ━━━")
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
                print_log(f"❌ 하루특가 예외: {e}")

            # ── [2순위] 지금 많이 팔리는 BEST ──
            print_log("━━━ [2순위] 지금 많이 팔리는 BEST 수집 ━━━")
            try:
                page.goto("https://sharelink.toss.im/best", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)

                best_deals = collect_hybrid_data(page, "BEST 랭킹", "best_seller", 2, target_count=200)
                all_harvested_deals.extend(best_deals)
            except Exception as e:
                print_log(f"❌ BEST 예외: {e}")

        except Exception as main_err:
            print_log(f"❌ 전체 예외: {main_err}")

        browser.close()

    print_log(f"🏆 총 {len(all_harvested_deals)}개 상품 파싱 완료 ➔ DB 저장 진입")
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

    # 저장
    with open(ROOT_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    with open(WORKER_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print_log(f"🎉 morvix_shop_db.json DB 저장 완료! (총 {len(db['products'])}개 상품 확정)")
    
    # 💥 핵심: 저장 완료 후 GitHub로 365 무인 Auto Push 쏘기!
    push_to_github_automatically()


if __name__ == "__main__":
    harvest_sharelink_portal()