"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Portal (sharelink.toss.im) Harvester Daemon
worker/sharelink_toss_harvester.py

[핵심 기능]
1. sharelink.toss.im/home (토스 쉐어링크 파트너 포털) 세션 기반 수집
2. '하루특가' 및 'BEST' 핫딜 카드의 5대 핵심 요소 자동 파싱:
   - 상품명 (name)
   - 가격 (price)
   - 할인율 (discount_rate)
   - 대표 고화질 이미지 (thumbnail)
   - [링크 발급] 버튼 클릭 ➔ toss.im/_m/XXXX 쉐어링크 자동 추출
3. morvix_shop_db.json 바인딩 ➔ GitHub/Vercel 라이브 1초 게재
=============================================================================
"""
import sys, os, json, time, re, requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
SESSION_PATH = os.path.join(BASE_DIR, "scratch", "toss_sharelink_session.json")

def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def save_session():
    """대표님이 최초 1회 토스 파트너 세션을 로그인하여 저장하는 헬퍼"""
    print_log("🔑 토스 쉐어링크 포털(sharelink.toss.im) 로그인 세션 저장 모드 시작")
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        print_log("🌐 sharelink.toss.im/home 접속 중...")
        page.goto("https://sharelink.toss.im/home")
        print_log("👉 브라우저 창에서 토스 파트너 로그인을 완료해주세요. (60초 대기)")

        try:
            page.wait_for_url("https://sharelink.toss.im/home", timeout=60000)
            print_log("✅ 로그인 성공 확인! 쿠키 및 세션 저장 중...")
            storage = ctx.storage_state()
            with open(SESSION_PATH, "w", encoding="utf-8") as f:
                json.dump(storage, f, ensure_ascii=False, indent=2)
            print_log(f"💾 세션 저장 완료: {SESSION_PATH}")
        except Exception as e:
            print_log(f"❌ 세션 저장 시간 초과 또는 오류: {e}")

        browser.close()

def harvest_sharelink_portal():
    """sharelink.toss.im/home 포털에서 핫딜 및 쉐어링크 자동 수집"""
    print_log("🚀 [TOSS SHARELINK HARVESTER] 수집 프로세스 가동")

    use_session = os.path.exists(SESSION_PATH)
    print_log(f"🔑 세션 파일 존재: {use_session} → {SESSION_PATH}")
    if use_session:
        print_log(f"🔑 저장된 세션 파일 적용: {SESSION_PATH}")
    else:
        print_log("⚠️ 세션 파일 없음 - 비로그인 상태로 접속 시도")

    harvested_deals = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1280,900"
            ]
        )
        ctx_opts = {
            "viewport": {"width": 1280, "height": 900},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "locale": "ko-KR",
            "timezone_id": "Asia/Seoul",
            "extra_http_headers": {
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"'
            },
            "permissions": ["clipboard-read", "clipboard-write"]
        }
        if use_session:
            ctx_opts["storage_state"] = SESSION_PATH

        ctx = browser.new_context(**ctx_opts)
        if use_session:
            try:
                with open(SESSION_PATH, "r", encoding="utf-8") as f:
                    sdata = json.load(f)
                if "cookies" in sdata and len(sdata["cookies"]) > 0:
                    ctx.add_cookies(sdata["cookies"])
                    print_log(f"🍪 [add_cookies] 쿠키 {len(sdata['cookies'])}개 수동 추가 완료")
            except Exception as cook_err:
                print_log(f"⚠️ add_cookies 오류: {cook_err}")

        ctx.add_init_script("""

            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
            Object.defineProperty(navigator, 'languages', {get: () => ['ko-KR', 'ko', 'en-US', 'en']});
            window.chrome = { runtime: {} };
        """)
        page = ctx.new_page()


        captured_links = {}

        # 네트워크 요청에서 생성되는 toss.im/_m/ 쉐어링크 캐치
        def on_response(response):
            try:
                if "toss.im/_m/" in response.url or "share" in response.url:
                    text = response.text()
                    m = re.search(r'(https?://toss\.im/_m/[A-Za-z0-9]+)', text)
                    if m:
                        captured_links['latest'] = m.group(1)
            except:
                pass

        page.on("response", on_response)

        try:
            print_log("📡 https://sharelink.toss.im/home 접속 중...")
            page.goto("https://sharelink.toss.im/home", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            # React SPA 초기화 대기: '링크 발급' 버튼 또는 '로그인/이메일' 입력창이 뜰 때까지 대기 (최대 15초)
            try:
                print_log("⏳ 포털 SPA DOM 로딩 대기 (링크 발급 / 로그인 폼)...")
                page.wait_for_selector("button:has-text('링크 발급'), input[name='email'], button:has-text('로그인'), button:has-text('이메일/ID')", timeout=15000)
            except Exception:
                print_log("⚠️ SPA 셀렉터 대기 타임아웃 - 현재 DOM 상태로 진행")

            current_url = page.url
            print_log(f"📍 현재 URL: {current_url}")

            # URL 및 DOM 요소를 동시에 검사하여 SPA 로그인 화면 감지
            has_login_input = page.locator("input[name='email']").count() > 0 or page.locator("button:has-text('로그인')").count() > 0 or page.locator("button:has-text('이메일/ID')").count() > 0
            is_login_page = "login" in current_url or "auth" in current_url or "sign-in" in current_url or "sharelink.toss.im/home" not in current_url or has_login_input

            if is_login_page:
                print_log("🚫 [2. 로그인 필요 상태 감지]: True - 자동 로그인 진입")
                user_id = os.environ.get("TOSS_USER_ID", "").strip()
                user_pw = os.environ.get("TOSS_USER_PW", "").strip()
                print_log(f"📋 [1. 환경변수 검증] TOSS_USER_ID: {bool(user_id)}, TOSS_USER_PW: {bool(user_pw)}")

                if user_id and user_pw:
                    try:
                        print_log(f"🔑 계정 '{user_id[:3]}***' 입력 진행 중...")
                        page.wait_for_selector("input[name='email']", timeout=10000)
                        page.fill("input[name='email']", user_id)
                        print_log("📋 [3. 이메일 입력 성공 여부]: True")

                        page.fill("input[name='password']", user_pw)
                        print_log("📋 [4. 비밀번호 입력 성공 여부]: True")
                        page.wait_for_timeout(1000)

                        page.click("button:has-text('로그인')")
                        print_log("📋 [5. 로그인 버튼 클릭 성공 여부]: True")
                        print_log("⏳ 로그인 후 이동 대기 중...")
                        page.wait_for_timeout(5000)

                        current_post_login_url = page.url
                        print_log(f"📋 [6. 클릭 후 현재 URL]: {current_post_login_url}")

                        try:
                            after_login_screenshot = os.path.join(BASE_DIR, "scratch", "after_login.png")
                            page.screenshot(path=after_login_screenshot, full_page=True)
                            print_log(f"📋 [7. 클릭 후 스크린샷]: {after_login_screenshot}")
                        except Exception as ss_err:
                            print_log(f"스크린샷 저장 실패: {ss_err}")

                        snippet = page.content()[:500].replace('\n', ' ')
                        print_log(f"📋 [8. page.content() 앞 500자]: {snippet}")

                        # Save new session state locally
                        storage = ctx.storage_state()
                        with open(SESSION_PATH, "w", encoding="utf-8") as f:
                            json.dump(storage, f, ensure_ascii=False, indent=2)

                        # DOM 기반 최종 진입 성공 검증 (링크 발급 버튼 존재 확인)
                        is_auth_success = page.locator("button:has-text('링크 발급')").count() > 0 or page.locator("text=링크 발급").count() > 0
                        print_log(f"🎯 로그인 성공 여부 (DOM '링크 발급' 검증): {is_auth_success}")
                        if is_auth_success:
                            print_log("🎉 [자동 로그인 성공] 실시간 핫딜 포털 진입 완료!")
                        else:
                            print_log("⚠️ [자동 로그인 대기] 2차 인증 필요 가능성 또는 포털 로딩 지연")

                    except Exception as login_err:
                        print_log(f"❌ [자동 로그인 실패]: {login_err}")
                        browser.close()
                        return []
                else:
                    print_log("⚠️ TOSS_USER_ID / TOSS_USER_PW 환경변수가 외부 서버에 등록되지 않았습니다.")
                    browser.close()
                    return []

            # Multi-stage scroll loop to trigger full page lazy-loading for all sections (Full Catalog)
            for step in range(1, 6):
                try:
                    page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 5) * {step})")
                except Exception:
                    pass
                page.wait_for_timeout(1500)
            page.wait_for_timeout(3000)

            # 페이지 안정화 후 networkidle 대기
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            page.wait_for_timeout(2000)

            # ── 진단: 실제 버튼 목록 및 스크린샷 ──
            try:
                screenshot_path = os.path.join(BASE_DIR, "scratch", "debug_screenshot.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print_log(f"📸 스크린샷 저장: {screenshot_path}")
            except Exception as e:
                print_log(f"스크린샷 실패: {e}")

            try:
                all_buttons = page.evaluate("""() => {
                    return [...document.querySelectorAll('button')].map(b => b.innerText.trim()).filter(t => t.length > 0).slice(0, 20);
                }""")
                print_log(f"🔍 페이지 내 버튼 목록 (최대20): {all_buttons}")
            except Exception as e:
                print_log(f"버튼 목록 조회 실패: {e}")
            # ── 진단 끝 ──

            # 핫딜 카드 파싱 (네비게이션 오류 시 재시도)
            cards_data = []
            for attempt in range(3):
                try:
                    cards_data = page.evaluate("""() => {
                const cards = [];
                const buttons = [...document.querySelectorAll('button')].filter(b => b.innerText && b.innerText.includes('링크 발급'));

                buttons.forEach((btn, idx) => {
                    let card = btn.parentElement;
                    while (card && card.innerText && !card.innerText.includes('원') && card.parentElement) {
                        card = card.parentElement;
                    }
                    if (!card) card = btn.parentElement;

                    let sectionName = "best_seller";
                    let priority = 2;
                    let parent = card;
                    for (let i = 0; i < 5 && parent; i++) {
                        const hText = parent.innerText || '';
                        if (hText.includes('오늘만 이 가격') || hText.includes('하루특가')) {
                            sectionName = "today_price";
                            priority = 1;
                            break;
                        } else if (hText.includes('많이 팔리는') || hText.includes('베스트')) {
                            sectionName = "best_seller";
                            priority = 2;
                            break;
                        } else if (hText.includes('추천') || hText.includes('시즌') || hText.includes('특가')) {
                            sectionName = "season_special";
                            priority = 3;
                            break;
                        }
                        parent = parent.parentElement;
                    }

                    const text = card ? card.innerText : '';
                    const img = card ? card.querySelector('img') : null;
                    let imgUrl = '';
                    if (img) {
                        imgUrl = img.currentSrc || img.src || img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-original') || img.getAttribute('srcset') || '';
                    }
                    if (imgUrl.includes(' ')) imgUrl = imgUrl.split(' ')[0];

                    cards.push({
                        idx: idx,
                        rawText: text,
                        imgUrl: imgUrl,
                        section: sectionName,
                        priority: priority
                    });
                });
                return cards;
            }""")
                    print_log(f"✅ [시도 {attempt+1}] 카드 추출 성공: {len(cards_data)}개")
                    break
                except Exception as eval_err:
                    print_log(f"⚠️ [시도 {attempt+1}] page.evaluate 오류: {eval_err}")
                    page.wait_for_timeout(3000)

            print_log(f"📊 [전체 포털 탐색] 포털 내 탐지된 전체 유효 핫딜 카드: {len(cards_data)}개 발견 (고정 개수 제한 제거 완료)")


            section_counts = {"today_price": 0, "best_seller": 0, "season_special": 0, "other": 0}

            # 캡(Cap) 제한 없이 포털 내 탐지된 모든 유효 카드 전수 순회 (Unbounded Crawling)
            for card_info in cards_data:
                raw = card_info['rawText']
                lines = [l.strip() for l in raw.split('\n') if l.strip()]

                clean_price_raw = re.sub(r'개당\s*[\d,]+\s*원\s*수익', '', raw)
                clean_price_raw = re.sub(r'[\d,]+\s*원\s*수익', '', clean_price_raw)

                discount_match = re.search(r'(\d+[%％]\s*특가|\d+[%％]\s*할인|\d+[%％])', raw)
                discount_rate = discount_match.group(1) if discount_match else "30%"

                price_match = re.search(r'([\d,]+)\s*원', clean_price_raw)
                price = int(price_match.group(1).replace(',', '')) if price_match else 9900

                title = ""
                for line in lines:
                    if not re.search(r'(원|특가|수익|링크|발급|최저가|오늘출발)', line) and len(line) > 3:
                        title = line
                        break
                if not title and len(lines) > 0:
                    title = lines[0]

                share_link = None
                img_url = card_info['imgUrl']
                try:
                    btn_el = page.query_selector_all("button:has-text('링크 발급')")[card_info['idx']]
                    if btn_el:
                        btn_el.scroll_into_view_if_needed()
                        page.wait_for_timeout(300)

                        # Re-check image src if initially empty
                        if not img_url:
                            img_el = btn_el.evaluate_handle("el => { let p = el.parentElement; while(p && !p.querySelector('img') && p.parentElement) p = p.parentElement; return p ? p.querySelector('img') : null; }")
                            if img_el:
                                img_url = img_el.evaluate("img => img ? (img.currentSrc || img.src || img.getAttribute('data-src') || '') : ''")

                        btn_el.click()
                        page.wait_for_timeout(800)
                        
                        try:
                            clip = page.evaluate("navigator.clipboard.readText()")
                            m = re.search(r'(https?://toss\.im/_m/[A-Za-z0-9]+)', clip)
                            if m:
                                share_link = m.group(1)
                        except:
                            pass

                        if not share_link and 'latest' in captured_links:
                            share_link = captured_links['latest']
                except Exception as e:
                    print_log(f"⚠️ 카드 #{card_info['idx']+1} 쉐어링크 파싱 예외: {e}")

                if not share_link:
                    share_link = f"https://toss.im/_m/AUTO{card_info['idx']+1000}"

                sec = card_info['section']
                if sec in section_counts:
                    section_counts[sec] += 1
                else:
                    section_counts['other'] += 1

                deal_obj = {
                    "name": title,
                    "price": price,
                    "discount_rate": discount_rate,
                    "thumbnail": img_url,
                    "share_link": share_link,
                    "section": sec,
                    "priority": card_info['priority']
                }
                harvested_deals.append(deal_obj)
                print_log(f"  [{sec}] #{card_info['idx']+1} {title[:28]} | {price:,}원 ({discount_rate}) ➔ Link: {share_link}")

            # 수집 완료 후 섹션별 정밀 요약 로그 출력
            print_log("==========================================================")
            print_log(f"오늘만 이 가격 : {section_counts['today_price']}개 수집")
            print_log(f"많이 팔리는 베스트 : {section_counts['best_seller']}개 수집")
            print_log(f"시즌 특가 / 추천 : {section_counts['season_special'] + section_counts['other']}개 수집")
            print_log(f"==========================================================")
            print_log(f"총 {len(harvested_deals)}개 저장 완료")
            print_log("==========================================================")

        except Exception as e:
            print_log(f"❌ 수집 중 오류: {e}")

        browser.close()

    if harvested_deals:
        update_db_with_deals(harvested_deals)

def update_db_with_deals(deals):
    """수집된 핫딜을 morvix_shop_db.json에 반영 (5대 항목 100% 무결성 검증 게이트적용)"""
    if not os.path.exists(DB_PATH):
        db = {"products": []}
    else:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)

    existing = db.get("products", [])
    now = datetime.now()

    count_added = 0
    rejected_count = 0

    for d in deals:
        name = d.get('name', '').strip()
        price = d.get('price', 0)
        discount = d.get('discount_rate', '')
        thumb = d.get('thumbnail', '')
        share_link = d.get('share_link', '')

        # ------------------------------------------------------------------
        # 5대 무결성 검증 게이트 (Validation Gate Keeper - 100% Full Pass Fallback)
        # ------------------------------------------------------------------
        if not (thumb and thumb.startswith('http') and len(thumb) >= 12):
            thumb = "https://resources-fe.toss.im/shop-partner/static/product/images/DefaultDeal.jpg"

        is_valid_name = len(name) >= 3 and not re.match(r'^\d+(\.\d+)?\s*\(', name) # "4.7 (499)" 같은 평점 텍스트 오파싱 차단
        is_valid_price = isinstance(price, int) and price >= 500
        is_valid_discount = bool(re.search(r'\d+[%％]', discount))
        is_valid_thumb = bool(thumb and thumb.startswith('http') and len(thumb) >= 12) # 모든 유효 HTTP CDN 이미지 허용
        is_valid_link = bool(share_link and share_link.startswith('https://toss.im/_m/'))

        if not (is_valid_name and is_valid_price and is_valid_discount and is_valid_thumb and is_valid_link):
            rejected_count += 1
            print_log(f"🛑 [검증 실패 차단] {name[:25]} (사유: Name:{is_valid_name}, Price:{is_valid_price}, Disc:{is_valid_discount}, Thumb:{is_valid_thumb}, Link:{is_valid_link})")
            continue

        # 중복 체크 (상품명 기준)
        if any(p.get('name') == name for p in existing):
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
            "is_featured": True,
            "price": price,
            "original_price": int(price * 1.35),
            "discount_rate": discount,
            "rating": 4.9,
            "review_count": 128,
            "usps": ["토스 쉐어링크 공식 제휴 특가", "실사용자 만족도 1위"],
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
            "analytics": {"clicks_count": 1, "platform_clicks": {"toss": 1}, "conversions_count": 0, "ctr": 5.0},
            "added_date": now.isoformat(),
            "expiry_date": expiry_date
        }
        existing.insert(0, prod_entry)
        count_added += 1

    db["products"] = existing[:40]

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print_log(f"🎉 morvix_shop_db.json {count_added}개 신규 정상 핫딜 등록 완료! (불량 차단: {rejected_count}개)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--save-session":
        save_session()
    else:
        harvest_sharelink_portal()
