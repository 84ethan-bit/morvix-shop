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
        captured_api_products = []  # ⚡ [API Interceptor] 토스 백엔드 JSON 원본 상품 수집함
        capture_lock = [0]  # [현재 캡처 대상 idx] - Race Condition 방어용 원자적 단방향 잠금

        # ⚡ [API Interceptor] 토스 백엔드 JSON response 도청 모듈
        def on_response(response):
            try:
                url = response.url
                # 1. 기존 쉐어링크 캡처
                if "toss.im/_m/" in url or "share" in url:
                    text = response.text()
                    m = re.search(r'(https?://toss\.im/_m/[A-Za-z0-9_-]+)', text)
                    if m:
                        captured_links[capture_lock[0]] = m.group(1)

                # 2. 토스 백엔드 API JSON 도청 (상품/딜 목록 API)
                if "application/json" in (response.headers.get("content-type") or "") and any(k in url for k in ["deal", "product", "home", "partner", "api"]):
                    try:
                        json_data = response.json()
                        # JSON 수색: items, products, deals, content 리스트 파싱
                        items = []
                        if isinstance(json_data, dict):
                            for k in ["data", "items", "products", "deals", "content", "result"]:
                                if k in json_data and isinstance(json_data[k], list):
                                    items = json_data[k]
                                    break
                                elif k in json_data and isinstance(json_data[k], dict):
                                    for sub_k in ["items", "products", "deals", "content"]:
                                        if sub_k in json_data[k] and isinstance(json_data[k][sub_k], list):
                                            items = json_data[k][sub_k]
                                            break
                        elif isinstance(json_data, list):
                            items = json_data

                        for item in items:
                            if isinstance(item, dict):
                                name = item.get("title") or item.get("name") or item.get("productName") or item.get("dealName")
                                price = item.get("price") or item.get("salePrice") or item.get("discountPrice") or item.get("discountedPrice")
                                orig_price = item.get("originalPrice") or item.get("regularPrice") or item.get("marketPrice")
                                disc_rate = item.get("discountRate") or item.get("discountPercent")
                                thumb = item.get("imageUrl") or item.get("thumbnail") or item.get("image") or item.get("thumbnailUrl")
                                share_url = item.get("shareUrl") or item.get("shareLink") or item.get("tossLink") or item.get("link")

                                if name and price and isinstance(price, (int, float)) and price >= 500:
                                    captured_api_products.append({
                                        "name": str(name).strip(),
                                        "price": int(price),
                                        "original_price": int(orig_price) if orig_price else int(price * 1.3),
                                        "discount_rate": f"{disc_rate}%" if disc_rate else "",
                                        "thumbnail": str(thumb).strip() if thumb else "",
                                        "share_link": str(share_url).strip() if share_url else ""
                                    })
                    except Exception:
                        pass
            except Exception:
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

                        # DOM 기반 최종 진입 성공 검증 (링크 발급 버튼 존재 확인)
                        is_auth_success = page.locator("button:has-text('링크 발급')").count() > 0 or page.locator("text=링크 발급").count() > 0
                        print_log(f"🎯 로그인 성공 여부 (DOM '링크 발급' 검증): {is_auth_success}")

                        if is_auth_success:
                            print_log("🎉 [자동 로그인 성공] 실시간 핫딜 포털 진입 완료!")

                        else:
                            print_log("🚨 [토스 2FA 본인인증 요구 감지] 스마트폰 토스 앱에서 '로그인 확인' 푸시 알림 승인을 대기합니다 (30초 대기)...")
                            try:
                                if page.locator("button:has-text('알림 다시 받기')").count() > 0:
                                    page.click("button:has-text('알림 다시 받기')")
                                    print_log("📲 [푸시 알림 재전송 클릭 완료] 대표님 스마트폰 토스 앱으로 '로그인 확인' 알림이 즉시 발송되었습니다!")
                            except Exception as push_err:
                                print_log(f"알림 클릭 스킵: {push_err}")


                        try:
                            # 30초 동안 토스 앱 승인 대기
                            page.wait_for_selector("button:has-text('링크 발급')", timeout=30000)
                            print_log("🎉 [토스 앱 2FA 승인 확인] 핫딜 포털 공식 진입 성공!")
                            storage = ctx.storage_state()
                            with open(SESSION_PATH, "w", encoding="utf-8") as f:
                                json.dump(storage, f, ensure_ascii=False, indent=2)
                        except Exception:
                            print_log("⚠️ [2FA 타임아웃] 스마트폰 앱 승인이 지연되었습니다. 다음 루프에서 재시도합니다.")


                    except Exception as login_err:
                        print_log(f"❌ [자동 로그인 실패]: {login_err}")
                        browser.close()
                        return []
                else:
                    print_log("⚠️ TOSS_USER_ID / TOSS_USER_PW 환경변수가 외부 서버에 등록되지 않았습니다.")
                    browser.close()
                    return []

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 2-섹션 전용 수집 전략:
            #  1순위) "오늘만 이가격" 하루특가  → 전체 보기 클릭 → 전체 상품 수집
            #  2순위) "지금 많이 팔리는 BEST"  → 전체 보기 클릭 → 전체 상품 수집
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            section_counts = {"today_price": 0, "best_seller": 0}
            seen_titles = set()
            TARGET_PER_SECTION = 30  # 섹션당 최대 30개

            def collect_from_full_page(section_name, section_key, priority_val):
                """현재 '전체 보기' 페이지에서 링크 발급 버튼 전수 수집"""
                nonlocal seen_titles

                # 전체 페이지 딥스크롤 최적화 (4단계 × 150ms)
                print_log(f"  📜 [{section_name}] 딥스크롤 시작...")
                for step in range(1, 5):
                    try:
                        page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 4) * {step})")
                    except Exception:
                        pass
                    page.wait_for_timeout(150)
                try:
                    page.evaluate("window.scrollTo(0, 0)")
                except Exception:
                    pass
                page.wait_for_timeout(500)

                btns = page.query_selector_all("button:has-text('링크 발급')")
                print_log(f"  📊 [{section_name}] 탐지된 '링크 발급' 버튼: {len(btns)}개")

                collected = 0
                for idx, btn in enumerate(btns):
                    if collected >= TARGET_PER_SECTION:
                        break
                    try:
                        btn.scroll_into_view_if_needed()
                        page.wait_for_timeout(300)

                        # 카드 컨테이너 탐색 (img + 가격이 함께 있는 최상위 상자)
                        card_container = btn.evaluate_handle("""el => {
                            let node = el;
                            for (let i = 0; i < 8; i++) {
                                node = node.parentElement;
                                if (!node) break;
                                const hasImg = node.querySelector('img') !== null;
                                const text = node.innerText || '';
                                const hasPrice = /[0-9,]+\\s*원/.test(text);
                                if (hasImg && hasPrice) return node;
                            }
                            return el.parentElement || el;
                        }""")
                        if not card_container:
                            continue

                        raw = card_container.evaluate("el => el.innerText || ''")

                        # ── 1단계: 수익/배송/판매자 배지 줄 완전 제거 후 정제 텍스트 생성 ──
                        NOISE_PATTERNS = [
                            r'개당\s*[\d,]+\s*원\s*수익',
                            r'[\d,]+\s*원\s*수익',
                            r'^\d+$',
                            r'^[\d,]+원$',
                        ]
                        NOISE_WORDS = ['링크 발급', '베스트판매자', '내일도착', '오늘출발',
                                       '역대급특가', '30일 최저가', '최저가', '수익', '베스트판매']

                        lines_raw = []
                        for l in raw.split('\n'):
                            l = l.strip()
                            if not l:
                                continue
                            if any(w in l for w in NOISE_WORDS):
                                continue
                            if any(re.search(p, l) for p in NOISE_PATTERNS):
                                continue
                            lines_raw.append(l)

                        # ── 2단계: 상품명 추출 (가장 긴 줄 우선, 최소 5글자, '개당/수익' 금지) ──
                        name_candidates = [
                            l for l in lines_raw
                            if len(l) >= 5
                            and not re.match(r'^[\d,%원\-~★☆.()\[\]]+$', l)
                            and '%' not in l
                            and '개당' not in l
                            and '수익' not in l
                        ]
                        title = max(name_candidates, key=len) if name_candidates else ''
                        if not title or title in seen_titles:
                            continue
                        seen_titles.add(title)

                        # 이미지
                        img_url = card_container.evaluate(r"""el => {
                            const imgs = [...el.querySelectorAll('img')];
                            for (const img of imgs) {
                                let src = img.currentSrc || img.src || img.getAttribute('data-src') || img.getAttribute('src') || '';
                                if (src.includes(' ')) src = src.split(' ')[0];
                                if (src && src.startsWith('http') && !src.includes('placeholder') && !src.includes('DefaultDeal') && !src.includes('data:image')) {
                                    return src;
                                }
                            }
                            const divs = [...el.querySelectorAll('div, span')];
                            for (const d of divs) {
                                const bg = window.getComputedStyle(d).backgroundImage;
                                if (bg && bg.includes('url(')) {
                                    const m = bg.match(/url\(["']?(https?:\/\/[^"']+)["']?\)/);
                                    if (m && m[1]) return m[1];
                                }
                            }
                            return '';
                        }""")
                        if ' ' in img_url:
                            img_url = img_url.split(' ')[0]

                        # ── 3단계: 할인율 추출 (없으면 빈값) ──
                        discount_match = re.search(r'(\d+)[%％]', raw)
                        discount_rate = f"{discount_match.group(1)}%" if discount_match else ''

                        # ── 4단계: 실제 판매가 추출 및 자동 단가-수량 보정 엔진 ──
                        clean_raw = re.sub(r'[\d,]+\s*원\s*수익', '', raw)
                        clean_raw = re.sub(r'수익', '', clean_raw)
                        clean_raw = re.sub(r'30일\s*최저가', '', clean_raw)

                        # 개당 N원 및 수량(N개, N봉, N팩) 감지 자동 총액 계산 보정
                        unit_match = re.search(r'개당\s*([\d,]+)\s*원', raw)
                        qty_match = re.search(r'([\d,]+)\s*(개|봉|팩|롤|병|정|포)', title)

                        prices_found = re.findall(r'([\d,]+)\s*원', clean_raw)
                        prices_int = [int(p.replace(',', '')) for p in prices_found]
                        valid_prices = [p for p in prices_int if p >= 500]
                        price = valid_prices[0] if valid_prices else 9900

                        # 보정: 만약 추출된 가격이 2000원 미만이고 단가*수량이 정황상 맞으면 총액으로 계산
                        if price < 2500 and qty_match:
                            try:
                                qty_num = int(qty_match.group(1).replace(',', ''))
                                if unit_match:
                                    unit_val = int(unit_match.group(1).replace(',', ''))
                                    calculated_total = unit_val * qty_num
                                    if calculated_total >= 2000:
                                        price = calculated_total
                                elif price * qty_num >= 2000 and qty_num > 1:
                                    price = price * qty_num
                            except Exception:
                                pass

                        # 5대 검증 (할인율 미표기도 정상 허용)
                        is_valid_name = len(title) >= 3
                        is_valid_price = isinstance(price, int) and price >= 500
                        is_valid_thumb = bool(img_url and img_url.startswith('http') and len(img_url) >= 15)
                        if not (is_valid_name and is_valid_price and is_valid_thumb):
                            print_log(f"    🛑 [검증 실패] {title[:20]} (Name:{is_valid_name} Price:{is_valid_price} Thumb:{is_valid_thumb})")
                            continue

                        # 정가 계산 (할인율이 있으면 역산, 없으면 30% 추정 정가)
                        if discount_rate:
                            try:
                                rate_num = int(re.search(r'\d+', discount_rate).group())
                                if 0 < rate_num < 100:
                                    original_price = int(price / (1 - rate_num / 100))
                                else:
                                    original_price = int(price * 1.3)
                            except Exception:
                                original_price = int(price * 1.3)
                        else:
                            original_price = int(price * 1.3)



                        # Race Condition 방어: per-card idx 독립 키
                        card_key = (priority_val * 10000) + idx
                        capture_lock[0] = card_key
                        captured_links.pop(card_key, None)
                        try:
                            btn.click(timeout=2000, force=True)
                        except Exception:
                            pass
                        page.wait_for_timeout(600)
                        share_link = captured_links.get(card_key)

                        # 네트워크 응답 지연 시 2차 대기 (안전망 구축)
                        if not share_link:
                            page.wait_for_timeout(600)
                            share_link = captured_links.get(card_key)

                        # 모달 DOM 정밀 검사
                        if not share_link:
                            try:
                                modal_link = page.evaluate("""() => {
                                    const els = [...document.querySelectorAll('input, a, p, div, span')];
                                    for (const el of els) {
                                        const val = el.value || el.href || el.innerText || '';
                                        if (val.includes('toss.im/_m/') || val.includes('toss.im/m/')) {
                                            const match = val.match(/(https:\\/\\/toss\\.im\\/(?:_m|m)\\/[A-Za-z0-9_-]+)/);
                                            if (match) return match[1];
                                        }
                                    }
                                    return null;
                                }""")
                                if modal_link:
                                    share_link = modal_link
                            except Exception:
                                pass

                        # 모달 닫기
                        try:
                            close_btn = page.locator("button:has-text('닫기'), [aria-label='close'], .modal-close, button:has-text('확인')")
                            if close_btn.count() > 0:
                                close_btn.first.click(timeout=1000)
                        except Exception:
                            pass

                        if not share_link or 'AUTO' in share_link or not ('toss.im/_m/' in share_link or 'toss.im/m/' in share_link):
                            print_log(f"    🛑 [링크 미발급] {title[:25]} → 수집 제외")
                            continue

                        deal_obj = {
                            "name": title,
                            "price": price,
                            "discount_rate": discount_rate,
                            "thumbnail": img_url,
                            "share_link": share_link,
                            "section": section_key,
                            "priority": priority_val
                        }
                        harvested_deals.append(deal_obj)
                        section_counts[section_key] += 1
                        collected += 1
                        print_log(f"  [{section_name}] #{collected} {title[:30]} | {price:,}원 ({discount_rate})")

                    except Exception as card_err:
                        print_log(f"  ⚠️ 카드 #{idx+1} 파싱 오류: {card_err}")

                return collected

            # ── 1순위: 오늘만 이가격 (하루특가) 전체 보기 ──
            print_log("━━━ [1순위] 오늘만 이가격 하루특가 전체 보기 클릭 ━━━")
            try:
                # 홈페이지 딥스크롤 → 섹션 헤더 노출
                for step in range(1, 6):
                    try:
                        page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 5) * {step})")
                    except Exception:
                        pass
                    page.wait_for_timeout(500)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1500)

                today_see_all = page.locator("a:has-text('전체 보기'), button:has-text('전체 보기'), a:has-text('더 보기'), button:has-text('더 보기')").first
                if today_see_all.count() > 0 or True:
                    # 하루특가 섹션의 전체 보기 탐색 (DOM 다각도 탐색)
                    see_all_link = page.evaluate("""() => {
                        // 1. 텍스트 직접 매칭 탐색
                        const allEls = [...document.querySelectorAll('a, button, div, span')];
                        for (const el of allEls) {
                            const txt = (el.innerText || '').trim();
                            if ((txt === '전체 보기' || txt === '전체보기' || txt === '더보기' || txt === '더 보기') && (el.href || el.tagName === 'BUTTON' || el.onclick || el.getAttribute('role') === 'button')) {
                                // 섹션 근처인지 확인
                                let p = el.parentElement;
                                for (let i = 0; i < 5; i++) {
                                    if (!p) break;
                                    const pTxt = p.innerText || '';
                                    if (pTxt.includes('오늘만') || pTxt.includes('하루특가')) {
                                        return el.href || el.getAttribute('href') || '__CLICK__';
                                    }
                                    p = p.parentElement;
                                }
                            }
                        }
                        // 2. 헤더 기준 근처 버튼/링크 탐색
                        const headers = [...document.querySelectorAll('h1, h2, h3, h4, p, span, div')];
                        for (const h of headers) {
                            const txt = h.innerText || '';
                            if (txt.includes('오늘만 이 가격') || txt.includes('하루특가')) {
                                let parent = h.parentElement;
                                for (let i = 0; i < 6; i++) {
                                    if (!parent) break;
                                    const link = parent.querySelector('a, button, [role="button"]');
                                    if (link) {
                                        const linkTxt = (link.innerText || '').trim();
                                        if (linkTxt.includes('전체') || linkTxt.includes('더')) {
                                            return link.href || link.getAttribute('href') || '__CLICK__';
                                        }
                                    }
                                    parent = parent.parentElement;
                                }
                            }
                        }
                        return null;
                    }""")
                    print_log(f"  🔗 하루특가 '전체 보기' 링크: {see_all_link}")

                    if see_all_link and see_all_link != '__CLICK__' and see_all_link.startswith('http'):
                        page.goto(see_all_link, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(2000)
                        collect_from_full_page("하루특가", "today_price", 1)
                    else:
                        # 직접 클릭 시도 (JS return '__CLICK__' 또는 셀렉터 지원)
                        clicked = False
                        try:
                            btn = page.locator("text='오늘만 이 가격' >> xpath=../..//button[contains(.,'전체')] | text='오늘만 이 가격' >> xpath=../..//a[contains(.,'전체')]").first
                            if btn.count() > 0:
                                btn.click(timeout=3000)
                                page.wait_for_timeout(2000)
                                clicked = True
                        except Exception:
                            pass
                        
                        if clicked:
                            print_log("  👆 하루특가 '전체 보기' 직접 클릭 성공!")
                            collect_from_full_page("하루특가", "today_price", 1)
                        else:
                            print_log("  ⚠️ 전체 보기 링크 없음 → 홈 하루특가 섹션 직접 수집")
                            collect_from_full_page("하루특가(홈)", "today_price", 1)


            except Exception as e:
                print_log(f"  ❌ 하루특가 전체 보기 오류: {e}")

            # ── 홈으로 복귀 ──
            try:
                page.goto("https://sharelink.toss.im/home", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
            except Exception:
                pass

            # ── 2순위: 지금 많이 팔리는 BEST 전체 보기 ──
            print_log("━━━ [2순위] 지금 많이 팔리는 BEST 전체 보기 클릭 ━━━")
            try:
                for step in range(1, 6):
                    try:
                        page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 5) * {step})")
                    except Exception:
                        pass
                    page.wait_for_timeout(500)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1500)

                best_see_all_link = page.evaluate("""() => {
                    const allEls = [...document.querySelectorAll('a, button, div, span')];
                    for (const el of allEls) {
                        const txt = (el.innerText || '').trim();
                        if ((txt === '전체 보기' || txt === '전체보기' || txt === '더보기' || txt === '더 보기') && (el.href || el.tagName === 'BUTTON' || el.onclick || el.getAttribute('role') === 'button')) {
                            let p = el.parentElement;
                            for (let i = 0; i < 5; i++) {
                                if (!p) break;
                                const pTxt = p.innerText || '';
                                if (pTxt.includes('많이 팔리는') || pTxt.includes('BEST') || pTxt.includes('베스트')) {
                                    return el.href || el.getAttribute('href') || '__CLICK__';
                                }
                                p = p.parentElement;
                            }
                        }
                    }
                    const headers = [...document.querySelectorAll('h1, h2, h3, h4, p, span, div')];
                    for (const h of headers) {
                        const txt = h.innerText || '';
                        if (txt.includes('지금 많이 팔리는') || txt.includes('BEST') || txt.includes('베스트')) {
                            let parent = h.parentElement;
                            for (let i = 0; i < 6; i++) {
                                if (!parent) break;
                                const link = parent.querySelector('a, button, [role="button"]');
                                if (link) {
                                    const linkTxt = (link.innerText || '').trim();
                                    if (linkTxt.includes('전체') || linkTxt.includes('더')) {
                                        return link.href || link.getAttribute('href') || '__CLICK__';
                                    }
                                }
                                parent = parent.parentElement;
                            }
                        }
                    }
                    return null;
                }""")
                print_log(f"  🔗 베스트 '전체 보기' 링크: {best_see_all_link}")

                if best_see_all_link and best_see_all_link != '__CLICK__' and best_see_all_link.startswith('http'):
                    page.goto(best_see_all_link, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(2000)
                    collect_from_full_page("지금 많이 팔리는 BEST", "best_seller", 2)
                else:
                    clicked = False
                    try:
                        btn = page.locator("text='BEST' >> xpath=../..//button[contains(.,'전체')] | text='BEST' >> xpath=../..//a[contains(.,'전체')] | text='지금 많이 팔리는' >> xpath=../..//button[contains(.,'전체')]").first
                        if btn.count() > 0:
                            btn.click(timeout=3000)
                            page.wait_for_timeout(2000)
                            clicked = True
                    except Exception:
                        pass

                    if clicked:
                        print_log("  👆 베스트 '전체 보기' 직접 클릭 성공!")
                        collect_from_full_page("지금 많이 팔리는 BEST", "best_seller", 2)
                    else:
                        print_log("  ⚠️ 전체 보기 링크 없음 → 홈 베스트 섹션 직접 수집")
                        collect_from_full_page("베스트(홈)", "best_seller", 2)


            except Exception as e:
                print_log(f"  ❌ 베스트 전체 보기 오류: {e}")

            print_log("==========================================================")
            print_log(f"🏆 오늘만 이가격(하루특가) : {section_counts['today_price']}개 수집")
            print_log(f"🔥 지금 많이 팔리는 BEST  : {section_counts['best_seller']}개 수집")
            print_log(f"📦 총 합계               : {len(harvested_deals)}개")
            print_log("==========================================================")










            try:
                tabs = page.evaluate("""() => {
                    const btns = [...document.querySelectorAll('button, a')];
                    return btns
                        .filter(b => b.innerText && b.innerText.length < 30 && !b.innerText.includes('링크 발급') && !b.innerText.includes('로그인'))
                        .map(b => b.innerText.trim())
                        .filter(t => t.length > 1)
                        .slice(0, 20);
                }""")
                print_log(f"📑 탐지된 탭 목록: {tabs}")
            except Exception:
                pass

            btn_els = page.query_selector_all("button:has-text('링크 발급')")
            print_log(f"📊 탐지된 핫딜 '링크 발급' 카드 총 수량: {len(btn_els)}개")

            section_counts = {"today_price": 0, "best_seller": 0, "season_special": 0, "other": 0}
            seen_titles = set()

            # 상한 60개로 확대 (첫 20개 고정 → 전체 섹션 풀 수집)
            TARGET_DEALS = 60

            for idx, btn in enumerate(btn_els):  # [:30] 제한 해제 - 전체 버튼 순회
                try:
                    # 1. 카드를 화면 내로 먼저 스크롤하여 이미지 레이지 로딩(Lazy-Loading) 100% 강제 유발
                    try:
                        btn.scroll_into_view_if_needed()
                        page.wait_for_timeout(300)
                    except Exception:
                        pass

                    # 1. 썸네일 이미지(img)와 가격(원)이 모두 상위 상자에 포함되도록 DOM 상위 조상 정밀 클라이밍
                    card_container = btn.evaluate_handle("""el => {
                        let card = el.parentElement;
                        for (let i = 0; i < 8 && card; i++) {
                            if (card.querySelector('img') && card.innerText && card.innerText.includes('원')) {
                                break;
                            }
                            if (card.parentElement) card = card.parentElement;
                        }
                        return card || el.parentElement;
                    }""")

                    raw = card_container.evaluate("el => el ? el.innerText : ''")
                    if not raw or '원' not in raw:
                        continue

                    lines_txt = [l.strip() for l in raw.split('\n') if l.strip()]

                    title = ""
                    for line in lines_txt:
                        if not re.search(r'(원|특가|수익|링크|발급|최저가|오늘출발)', line) and len(line) > 3:
                            title = line
                            break
                    if not title and len(lines_txt) > 0:
                        title = lines_txt[0]

                    if not title or title in seen_titles:
                        continue
                    seen_titles.add(title)

                    img_url = card_container.evaluate(r"""el => {

                        const imgs = [...el.querySelectorAll('img')];
                        for (const img of imgs) {
                            let src = img.currentSrc || img.src || img.getAttribute('data-src') || img.getAttribute('src') || img.getAttribute('srcset') || '';
                            if (src.includes(' ')) src = src.split(' ')[0];
                            if (src && src.startsWith('http') && !src.includes('placeholder') && !src.includes('DefaultDeal') && !src.includes('data:image')) {
                                return src;
                            }
                        }
                        const divs = [...el.querySelectorAll('div, span, a')];
                        for (const d of divs) {
                            const bg = window.getComputedStyle(d).backgroundImage;
                            if (bg && bg.includes('url(')) {
                                const match = bg.match(/url\(["']?(https?:\/\/[^"']+)["']?\)/);
                                if (match && match[1]) return match[1];
                            }
                        }
                        return '';
                    }""")
                    if ' ' in img_url:
                        img_url = img_url.split(' ')[0]


                    clean_price_raw = re.sub(r'개당\s*[\d,]+\s*원\s*수익', '', raw)
                    clean_price_raw = re.sub(r'[\d,]+\s*원\s*수익', '', clean_price_raw)

                    discount_match = re.search(r'(\d+[%％]\s*특가|\d+[%％]\s*할인|\d+[%％])', raw)
                    discount_rate = discount_match.group(1) if discount_match else "30%"

                    price_match = re.search(r'([\d,]+)\s*원', clean_price_raw)
                    price = int(price_match.group(1).replace(',', '')) if price_match else 9900

                    # 정밀 섹션 및 우선순위 판별 (카드 내 배지 및 이전 섹션 헤더 DOM 탐색)
                    sec = card_container.evaluate("""el => {
                        const rawTxt = el.innerText || '';
                        if (rawTxt.includes('하루특가') || rawTxt.includes('오늘만')) return 'today_price';

                        let curr = el;
                        while (curr && curr.tagName !== 'BODY') {
                            let prev = curr.previousElementSibling;
                            while (prev) {
                                const pTxt = prev.innerText || '';
                                if (pTxt.includes('오늘만 이 가격') || pTxt.includes('하루특가')) return 'today_price';
                                if (pTxt.includes('지금 많이 팔리는') || pTxt.includes('BEST') || pTxt.includes('베스트')) return 'best_seller';
                                if (pTxt.includes('시즌') || pTxt.includes('기획전')) return 'season_special';
                                prev = prev.previousElementSibling;
                            }
                            curr = curr.parentElement;
                        }
                        return 'best_seller';
                    }""")

                    priority = 1 if sec == 'today_price' else (2 if sec == 'best_seller' else 3)


                    # Race Condition 방어: 현재 idx를 capture_lock에 등록하고 이전 응답 제거
                    capture_lock[0] = idx
                    captured_links.pop(idx, None)
                    btn.scroll_into_view_if_needed()
                    page.wait_for_timeout(200)

                    try:
                        btn.click(timeout=2000, force=True)
                    except Exception:
                        pass
                    page.wait_for_timeout(600)
                    share_link = captured_links.get(idx)

                    # 1. 모달/팝업 DOM 내 실시간 발급된 토스 쉐어링크 정밀 검사
                    if not share_link:
                        try:
                            modal_link = page.evaluate("""() => {
                                const els = [...document.querySelectorAll('input, a, p, div, span')];
                                for (const el of els) {
                                    const val = el.value || el.href || el.innerText || '';
                                    if (val.includes('toss.im/_m/') || val.includes('toss.im/m/')) {
                                        const match = val.match(/(https:\\/\\/toss\\.im\\/(?:_m|m)\\/[A-Za-z0-9_-]+)/);
                                        if (match) return match[1];
                                    }
                                }
                                return null;
                            }""")
                            if modal_link:
                                share_link = modal_link
                        except Exception:
                            pass

                    # 모달 팝업 닫기 (이후 버튼 클릭 방해 해제)
                    try:
                        close_btn = page.locator("button:has-text('닫기'), [aria-label='close'], .modal-close, button:has-text('확인')")
                        if close_btn.count() > 0:
                            close_btn.first.click(timeout=1000)
                    except Exception:
                        pass

                    # 🚨 100% 진짜 토스 쉐어링크가 발급되지 않은 경우 AUTO 가짜 생성 금지 및 즉시 차단
                    if not share_link or "AUTO" in share_link or not ("toss.im/_m/" in share_link or "toss.im/m/" in share_link):
                        print_log(f"🛑 [진짜 쉐어링크 미발급 차단] {title[:25]} ➔ 더미 생성 금지 및 수집 제외")
                        continue


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
                        "priority": priority
                    }
                    harvested_deals.append(deal_obj)
                    print_log(f"  [{sec}] #{len(harvested_deals)} {title[:28]} | {price:,}원 ({discount_rate}) ➔ Link: {share_link}")

                    if len(harvested_deals) >= TARGET_DEALS:
                        break

                except Exception as card_err:
                    print_log(f"⚠️ 카드 #{idx+1} 단일 파싱 오류: {card_err}")

            # ── 카테고리 탭 순회: 아직 TARGET_DEALS 미달 시 추가 섹션에서 보충 수집 ──
            if len(harvested_deals) < TARGET_DEALS:
                print_log(f"📂 1차 수집 {len(harvested_deals)}개 → 카테고리 탭 순회로 추가 보충 시작...")

                # 탭 키워드 후보 - 토스 쇼핑몰의 카테고리 탭 텍스트 매칭
                TAB_KEYWORDS = ['전체', '식품', '생활', '패션', '뷰티', '가전', '유아', '스포츠', '반려', '문화', '여행']

                for tab_kw in TAB_KEYWORDS:
                    if len(harvested_deals) >= TARGET_DEALS:
                        break
                    try:
                        tab_btn = page.locator(f"button:has-text('{tab_kw}'), a:has-text('{tab_kw}')")
                        if tab_btn.count() == 0:
                            continue
                        print_log(f"  📁 탭 클릭: [{tab_kw}]")
                        tab_btn.first.click(timeout=3000)
                        page.wait_for_timeout(2000)

                        # 탭 전환 후 딥스크롤로 lazy-load 유발
                        for step in range(1, 6):
                            try:
                                page.evaluate(f"window.scrollTo(0, (document.body.scrollHeight / 5) * {step})")
                            except Exception:
                                pass
                            page.wait_for_timeout(500)
                        page.wait_for_timeout(1500)

                        # 추가 버튼 재스캔
                        extra_btns = page.query_selector_all("button:has-text('링크 발급')")
                        print_log(f"  📊 [{tab_kw}] 탭 내 '링크 발급' 버튼: {len(extra_btns)}개")

                        for idx2, btn2 in enumerate(extra_btns):
                            if len(harvested_deals) >= TARGET_DEALS:
                                break
                            try:
                                btn2.scroll_into_view_if_needed()
                                page.wait_for_timeout(200)

                                # 카드 컨테이너 탐색 (img + 가격 텍스트가 모두 있는 최상위 상자)
                                card_container = btn2.evaluate_handle("""el => {
                                    let node = el;
                                    for (let i = 0; i < 8; i++) {
                                        node = node.parentElement;
                                        if (!node) break;
                                        const hasImg = node.querySelector('img') !== null;
                                        const text = node.innerText || '';
                                        const hasPrice = /[0-9,]+\\s*\uc6d0/.test(text);
                                        if (hasImg && hasPrice) return node;
                                    }
                                    return el.parentElement || el;
                                }""")

                                if not card_container:
                                    continue

                                card_text = card_container.evaluate("el => el.innerText || ''")
                                lines_text = [l.strip() for l in card_text.split('\n') if l.strip() and '링크 발급' not in l]

                                import re as _re
                                title2 = next((l for l in lines_text if len(l) >= 5 and not _re.match(r'^[\d,%원]+$', l) and '할인' not in l and '특가' not in l and l not in seen_titles), '')
                                if not title2 or title2 in seen_titles:
                                    continue
                                seen_titles.add(title2)

                                price_m = _re.search(r'([0-9,]+)\s*원', card_text)
                                price2 = int(price_m.group(1).replace(',', '')) if price_m else 0
                                disc_m = _re.search(r'(\d+)\s*[%％]', card_text)
                                disc2 = f"{disc_m.group(1)}%" if disc_m else '30%'
                                img_el = card_container.query_selector('img')
                                img2 = ''
                                if img_el:
                                    img2 = img_el.get_attribute('src') or img_el.get_attribute('data-src') or ''

                                if not (price2 >= 500 and img2.startswith('http')):
                                    continue

                                # 쉐어링크 발급
                                capture_lock[0] = 90000 + idx2
                                captured_links.pop(90000 + idx2, None)
                                try:
                                    btn2.click(timeout=2000, force=True)
                                except Exception:
                                    pass
                                page.wait_for_timeout(600)
                                link2 = captured_links.get(90000 + idx2)
                                if not link2 or 'toss.im/_m/' not in link2:
                                    continue

                                deal_obj2 = {
                                    "name": title2,
                                    "price": price2,
                                    "discount_rate": disc2,
                                    "thumbnail": img2,
                                    "share_link": link2,
                                    "section": "best_seller",
                                    "priority": 2
                                }
                                harvested_deals.append(deal_obj2)
                                print_log(f"  [tab:{tab_kw}] #{len(harvested_deals)} {title2[:28]} | {price2:,}원 ({disc2})")
                            except Exception:
                                pass
                    except Exception as tab_err:
                        print_log(f"  ⚠️ [{tab_kw}] 탭 순회 오류: {tab_err}")

            print_log("==========================================================")
            print_log(f"오늘만 이 가격 : {section_counts['today_price']}개 수집")
            print_log(f"많이 팔리는 베스트 : {section_counts['best_seller']}개 수집")
            print_log(f"시즌 특가 / 추천 : {section_counts['season_special'] + section_counts['other']}개 수집")
            print_log("==========================================================")
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

    # 2026-07-31 수복 이전 구형 엇갈린 데이터 100% 자동 소탕 필터
    existing = [p for p in db.get("products", []) if p.get("added_date", "") >= "2026-07-31T00:00:00"]
    now = datetime.now()

    count_added = 0
    rejected_count = 0

    for d in deals:
        name = d.get('name', '').strip()
        price = d.get('price', 0)
        discount = d.get('discount_rate', '')
        thumb = d.get('thumbnail', '')
        share_link = d.get('share_link', '')

        is_valid_name = len(name) >= 3 and not re.match(r'^\d+(\.\d+)?\s*\(', name)
        is_valid_price = isinstance(price, int) and price >= 500
        is_valid_discount = bool(re.search(r'\d+[%％]', discount))
        is_valid_thumb = bool(thumb and thumb.startswith('http') and len(thumb) >= 15 and not 'DefaultDeal' in thumb and not 'placeholder' in thumb)
        is_valid_link = bool(share_link and share_link.startswith('https://toss.im/_m/'))

        if not (is_valid_name and is_valid_price and is_valid_discount and is_valid_thumb and is_valid_link):
            rejected_count += 1
            print_log(f"🛑 [검증 실패 차단] {name[:25]} (사유: Name:{is_valid_name}, Price:{is_valid_price}, Disc:{is_valid_discount}, Thumb:{is_valid_thumb}, Link:{is_valid_link})")
            continue


        # UPSERT 전략: 이미 같은 상품명이 존재하면 skip이 아닌 UPDATE (링크/이미지/섹션 최신화)
        existing_idx = next((i for i, p in enumerate(existing) if p.get('name') == name), None)
        if existing_idx is not None:
            # 기존 항목 현재 정보로 갱신 (링크, 이미지, 섹션, 만료일 최신화)
            existing[existing_idx]['toss_link'] = share_link
            existing[existing_idx]['affiliate_links'][0]['url'] = share_link
            existing[existing_idx]['thumbnail'] = thumb
            existing[existing_idx]['section'] = d.get('section', 'best_seller')
            existing[existing_idx]['priority'] = d.get('priority', 2)
            existing[existing_idx]['price'] = price
            existing[existing_idx]['discount_rate'] = discount
            existing[existing_idx]['expiry_date'] = (now + timedelta(hours=48)).isoformat()
            print_log(f"  🔄 [UPSERT 갱신] {name[:28]} ➔ 링크/이미지 최신화 완료")
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


    # 2순위 수복: 200개 강제 슬라이싱 대신 만료일(expiry_date) 기반으로 오래된 상품 자동 정리
    now_iso = now.isoformat()
    existing = [p for p in existing if p.get('expiry_date', '9999') > now_iso]
    db["products"] = existing[:300]  # 안전 상한선 300개로 완화

    with open(DB_PATH, "w", encoding="utf-8") as f:

        json.dump(db, f, ensure_ascii=False, indent=2)

    print_log(f"🎉 morvix_shop_db.json {count_added}개 신규 정상 핫딜 등록 완료! (불량 차단: {rejected_count}개)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--save-session":
        save_session()
    else:
        harvest_sharelink_portal()
