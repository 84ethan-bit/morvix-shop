"""
=============================================================================
MORVIX Shop OS - Toss Shopping 24시간 자율 수집 데몬
toss_harvester_daemon.py

[목적]
- 토스쇼핑 메인 페이지를 주기적으로 모니터링 (기본 30분 간격)
- 상품명, 조회수("X만명 구경함"), 이미지, 상품URL, 카테고리를 자동 파싱
- 텔레그램 채널로 자동 송출
- 중복 상품 방지 (slug 기반 중복 체크)

[수집 가능 데이터]
- ✅ 상품명
- ✅ 상품 이미지 (실물 고화질, toss.shopping CDN)
- ✅ 조회수 ("74.1만명 구경함")
- ✅ 평점 / 리뷰 수
- ✅ 토스 상품 URL (https://toss.shopping/t/XXXXXX)
- ⚠️ 가격/할인율: JS 인증 게이트 뒤에 있어 별도 처리 필요

[설계 원칙]
- "구현 예정" 기능은 TODO 주석으로 명확히 표기
- 단정적 표현("100%", "완전") 사용 금지
- 실제 동작 여부는 실측 후 확정

=============================================================================
"""

import os
import sys
import json
import time
import re
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# --------------------------------------------------------------------------
# 환경 변수 설정
# --------------------------------------------------------------------------
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

HARVEST_INTERVAL_MINUTES = 30  # 토스쇼핑 모니터링 주기 (분)

# --------------------------------------------------------------------------
# 텔레그램 알림 발송
# --------------------------------------------------------------------------
def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram credentials missing. Skipping notification.")
        return False
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
            timeout=5
        )
        return res.status_code == 200
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")
        return False

def send_telegram_photo(photo_url, caption):
    if not BOT_TOKEN or not CHAT_ID:
        return False
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            json={
                "chat_id": CHAT_ID,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "Markdown"
            },
            timeout=5
        )
        return res.status_code == 200
    except Exception as e:
        print(f"⚠️ Telegram photo send error: {e}")
        return False

# --------------------------------------------------------------------------
# 토스쇼핑 메인 페이지 수집기 (Playwright 기반)
# --------------------------------------------------------------------------
def harvest_toss_shopping_main():
    """
    토스쇼핑 메인 페이지에서 상품 카드를 수집합니다.
    
    현재 수집 가능:
    - ✅ 상품명
    - ✅ 조회수 ("X만명 구경함")
    - ✅ 상품 이미지
    - ✅ 평점 / 리뷰 수
    - ✅ 상품 URL (/t/XXXXXX)
    
    현재 미수집 (설계 목표):
    - ⚠️ 가격 / 할인율 (JS 인증 게이트 뒤)
    - ⚠️ 토스 쉐어링크 (toss.im/_m/...) -> 상품별 공유 버튼 클릭 필요
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("⚠️ playwright not installed. Run: pip install playwright && playwright install chromium")
        return []

    products = []

    try:
        with sync_playwright() as p:
            mobile_device = p.devices['iPhone 14 Pro']
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(**mobile_device)
            page = ctx.new_page()

            print("📡 [Toss Harvester] 토스쇼핑 메인 페이지 로딩 중...")
            page.goto("https://toss.shopping", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(3000)

            # 스크롤 다운으로 lazy load 트리거
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            page.wait_for_timeout(1500)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 2/3)")
            page.wait_for_timeout(1500)

            cards = page.query_selector_all("a[href*='/t/']")
            print(f"✅ [Toss Harvester] 상품 카드 {len(cards)}개 감지")

            seen_hrefs = set()
            for card in cards:
                try:
                    href = card.get_attribute('href') or ''
                    if not href or href in seen_hrefs:
                        continue
                    if not re.match(r'^/t/\d+$', href):
                        continue
                    seen_hrefs.add(href)

                    raw_text = card.inner_text().strip()

                    # 상품명 추출 (첫 줄, 구경함 이전 텍스트)
                    name_match = re.match(r'^(.+?)(?=[\d.]+만명|\d+,?\d*명)', raw_text)
                    title = name_match.group(1).strip() if name_match else raw_text.split('\n')[0].strip()

                    # 조회수 추출 ("74.1만명 구경함", "4,574명 구경함")
                    view_match = re.search(r'([\d.]+만명|\d{1,3}(?:,\d{3})*명)\s*구경함', raw_text)
                    view_count = view_match.group(1) if view_match else ""

                    # 평점 추출
                    rating_match = re.search(r'([\d.]+)\s*\(', raw_text)
                    rating = float(rating_match.group(1)) if rating_match else 4.5

                    # 리뷰수 추출
                    review_match = re.search(r'\(([\d,]+)\)', raw_text)
                    review_count = review_match.group(1).replace(',', '') if review_match else "0"

                    # 이미지 추출 (img 태그 src)
                    img_el = card.query_selector("img")
                    image_url = ""
                    if img_el:
                        image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src") or ""

                    toss_url = f"https://toss.shopping{href}"
                    product_id = href.replace('/t/', '')

                    if len(title) < 3:
                        continue

                    products.append({
                        "id": product_id,
                        "title": title,
                        "view_count": view_count,
                        "rating": rating,
                        "review_count": int(review_count) if review_count.isdigit() else 0,
                        "image_url": image_url,
                        "toss_url": toss_url,
                        "href": href,
                        "harvested_at": datetime.now().isoformat()
                    })

                except Exception as e:
                    continue

            browser.close()

    except Exception as e:
        print(f"❌ [Toss Harvester] Playwright 오류: {e}")

    print(f"✅ [Toss Harvester] 수집 완료: {len(products)}개 상품")
    return products

# --------------------------------------------------------------------------
# 텔레그램으로 수집한 핫딜 상품 전송
# --------------------------------------------------------------------------
def push_product_to_telegram(product):
    """
    수집한 토스 상품 정보를 텔레그램 채널로 발송합니다.
    telegram_watcher_cloud.py가 이 메시지를 수신하여 홈페이지에 게재합니다.
    
    [설계 목표]
    - 가격/할인율이 확보되면 메시지에 포함
    - 현재 가격 미확보 시 "[가격 확인 필요]" 로 명시 (더미 숫자 사용 금지)
    """
    view_tag = f"🔥 {product['view_count']} 구경함" if product['view_count'] else ""
    rating_tag = f"⭐ {product['rating']} ({product['review_count']:,}개 리뷰)" if product['review_count'] else ""

    caption = (
        f"🛒 *[MORVIX AUTO HARVEST - 토스쇼핑 신규 핫딜]*\n\n"
        f"• *상품명:* {product['title']}\n"
        f"• *인기 지표:* {view_tag}\n"
        f"• *평점:* {rating_tag}\n"
        f"• *상품 URL:* {product['toss_url']}\n"
        f"• *수집 시각:* {product['harvested_at'][:16]}\n\n"
        f"⚠️ _가격/할인율/쉐어링크는 구현 예정 단계입니다._"
    )

    if product.get('image_url'):
        ok = send_telegram_photo(product['image_url'], caption)
        if ok:
            print(f"  📤 텔레그램 사진+캡션 발송 완료: {product['title'][:30]}")
            return True

    ok = send_telegram_message(caption)
    if ok:
        print(f"  📤 텔레그램 텍스트 발송 완료: {product['title'][:30]}")
    return ok

# --------------------------------------------------------------------------
# 중복 체크 (이미 DB에 있는 상품 제외)
# --------------------------------------------------------------------------
def get_existing_product_ids():
    if not os.path.exists(DB_PATH):
        return set()
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        ids = set()
        for p in db.get("products", []):
            for link in p.get("affiliate_links", []):
                url = link.get("url", "")
                m = re.search(r'/t/(\d+)', url)
                if m:
                    ids.add(m.group(1))
        return ids
    except Exception as e:
        print(f"⚠️ DB 읽기 오류: {e}")
        return set()

# --------------------------------------------------------------------------
# 메인 수확 루프
# --------------------------------------------------------------------------
def run_harvester():
    print("=======================================================")
    print("🌾 MORVIX TOSS SHOPPING HARVESTER DAEMON v1.0")
    print("=======================================================")
    print(f"⏰ 모니터링 주기: {HARVEST_INTERVAL_MINUTES}분")
    print(f"📡 텔레그램 봇: {'✅ 연결됨' if BOT_TOKEN else '⚠️ 미설정'}")
    print("=======================================================\n")

    iteration = 0

    while True:
        iteration += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*60}")
        print(f"🔄 [Harvest #{iteration}] {now}")
        print(f"{'='*60}")

        try:
            # 1. 토스쇼핑 수집
            products = harvest_toss_shopping_main()

            if not products:
                print("⚠️ 수집된 상품 없음. 다음 주기까지 대기...")
            else:
                # 2. 중복 제외
                existing_ids = get_existing_product_ids()
                new_products = [p for p in products if p['id'] not in existing_ids]
                print(f"📊 신규 상품: {len(new_products)}개 / 전체: {len(products)}개 (중복 제외)")

                # 3. 상위 3개만 텔레그램 발송 (한 번에 너무 많이 보내지 않도록)
                sent = 0
                for prod in new_products[:3]:
                    if push_product_to_telegram(prod):
                        sent += 1
                        time.sleep(2)  # 텔레그램 Rate Limit 방지

                print(f"✅ 텔레그램 발송 완료: {sent}개")

        except Exception as e:
            print(f"❌ Harvest 오류: {e}")

        # 4. 다음 주기까지 대기
        next_run = datetime.now() + timedelta(minutes=HARVEST_INTERVAL_MINUTES)
        print(f"\n⏳ 다음 수집: {next_run.strftime('%H:%M:%S')} ({HARVEST_INTERVAL_MINUTES}분 후)")
        time.sleep(HARVEST_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 [TEST MODE] 단일 수집 테스트 실행...")
        products = harvest_toss_shopping_main()
        print(f"\n📊 수집 결과 ({len(products)}개):")
        for i, p in enumerate(products[:5]):
            print(f"\n  [{i+1}] {p['title']}")
            print(f"       조회수: {p['view_count']}")
            print(f"       평점: {p['rating']} ({p['review_count']}개 리뷰)")
            print(f"       이미지: {p['image_url'][:80]}...")
            print(f"       URL: {p['toss_url']}")
    else:
        run_harvester()
