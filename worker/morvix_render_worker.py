import os
import json
import sys
import time
import subprocess
import threading
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "morvix_shop_db.json")
HARVEST_INTERVAL = 1 * 60  # 1분 (검증용 - 확인 후 30분으로 변경)


if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CHROMIUM_READY = True
print(f"📦 PLAYWRIGHT_BROWSERS_PATH = {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'default')}")






WORKER_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(WORKER_DIR, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)



NAVER_SESSION_PATH = os.path.join(SESSION_DIR, "naver_storageState.json")
COUPANG_SESSION_PATH = os.path.join(SESSION_DIR, "coupang_storageState.json")

NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login"
COUPANG_LOGIN_URL = "https://login.coupang.com/login/login.pang"

def get_session_path(platform):
    return NAVER_SESSION_PATH if platform == 'naver' else COUPANG_SESSION_PATH

def inspect_session(platform):
    path = get_session_path(platform)
    if not os.path.exists(path):
        return 0, False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            cookies = data.get("cookies", [])
            auth_keywords = ["AUTH", "NID_AUT", "NID_SES", "CAUTH", "SESS", "LOGIN"]
            has_auth = any(
                any(k in c.get("name", "").upper() for k in auth_keywords)
                for c in cookies
            )
            return len(cookies), has_auth
    except Exception:
        return 0, False

def try_playwright_login(platform, username, password):
    """
    Real Playwright headless login attempt with stealth.
    Returns: (success: bool, cookie_count: int, message: str)
    """
    import random

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, 0, "Playwright not installed on this server"

    session_path = get_session_path(platform)
    login_url = NAVER_LOGIN_URL if platform == 'naver' else COUPANG_LOGIN_URL

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ]
            )
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                locale="ko-KR",
                timezone_id="Asia/Seoul",
            )

            # Stealth: Remove webdriver flag
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR','ko','en-US','en'] });
                window.chrome = { runtime: {} };
            """)

            page = context.new_page()

            print(f"[LOGIN] Navigating to {login_url}")
            page.goto(login_url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(random.randint(1500, 2500))

            if platform == 'naver':
                # Click ID field and type like a human
                id_sel = "#id"
                pw_sel = "#pw"

                page.click(id_sel)
                page.wait_for_timeout(random.randint(300, 600))
                # Type character by character with random delay
                for ch in username:
                    page.keyboard.type(ch)
                    page.wait_for_timeout(random.randint(60, 160))

                page.wait_for_timeout(random.randint(300, 700))

                page.click(pw_sel)
                page.wait_for_timeout(random.randint(300, 600))
                for ch in password:
                    page.keyboard.type(ch)
                    page.wait_for_timeout(random.randint(60, 160))

                page.wait_for_timeout(random.randint(400, 800))

                # Click login button
                try:
                    page.click("#log\\.login")
                except Exception:
                    try:
                        page.click("button[type='submit']")
                    except Exception:
                        page.keyboard.press("Enter")

                page.wait_for_timeout(5000)

                # Check for CAPTCHA or 2FA
                current_url = page.url
                page_text = page.inner_text("body") if page.query_selector("body") else ""
                print(f"[LOGIN] After login URL: {current_url}")

                if "captcha" in current_url.lower() or "captcha" in page_text.lower():
                    context.storage_state(path=session_path)
                    browser.close()
                    return False, 0, "CAPTCHA detected — manual login required"

                if "otp" in current_url.lower() or "인증" in page_text:
                    context.storage_state(path=session_path)
                    browser.close()
                    return False, 0, "2FA/OTP required — check your phone for verification"

            elif platform == 'coupang':
                id_field = page.query_selector("#username") or page.query_selector("input[name='email']") or page.query_selector("input[type='email']")
                pw_field = page.query_selector("#password") or page.query_selector("input[name='password']") or page.query_selector("input[type='password']")

                if id_field and pw_field:
                    id_field.fill(username)
                    page.wait_for_timeout(500)
                    pw_field.fill(password)
                    page.wait_for_timeout(500)
                    pw_field.press("Enter")
                    page.wait_for_timeout(4000)
                else:
                    browser.close()
                    return False, 0, "Coupang login form fields not found"

            # Save session regardless - check cookies after
            context.storage_state(path=session_path)
            
            cookies = context.cookies()
            auth_keywords = ["AUTH", "NID_AUT", "NID_SES", "CAUTH", "SESS", "LOGIN"]
            has_auth = any(
                any(k in c.get("name", "").upper() for k in auth_keywords)
                for c in cookies
            )

            browser.close()

            if has_auth:
                return True, len(cookies), f"Login SUCCESS: {len(cookies)} cookies saved including auth cookies"
            else:
                return False, len(cookies), f"Login FAILED: {len(cookies)} cookies found but NO auth cookies (wrong credentials or bot detection)"

    except Exception as e:
        return False, 0, f"Playwright error: {str(e)}"


class MorvixBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_HEAD(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self._cors()
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):

        self.send_response(200)
        self._cors()
        self.end_headers()

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        try:
            return json.loads(body)
        except Exception:
            return {}

    def _respond(self, code, payload):
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self._respond(200, {
                "status": "MORVIX_RENDER_WORKER_ONLINE",
                "mode": "TOSS_SHOPPING_SINGLE_PIPELINE",
                "security": "SAFE_STATIC_PARSER_ACTIVE (Zero Account Lock Risk)",
                "timestamp": datetime.now().isoformat(),
                "endpoints": [
                    "POST /api/test-link",
                    "GET /health"
                ]
            })
        elif self.path.startswith('/api/verify-session'):
            platform = 'naver' if 'naver' in self.path else 'coupang'
            cnt, auth = inspect_session(platform)
            self._respond(200, {
                "platform": platform,
                "cookie_count": cnt,
                "authenticated": auth,
                "status": "AUTHENTICATED" if auth else "NOT_AUTHENTICATED",
                "session_file_exists": os.path.exists(get_session_path(platform))
            })
        elif self.path.startswith('/api/diagnostic-screenshot'):
            platform = 'naver' if 'naver' in self.path else 'coupang'
            diag_png_path = os.path.join(SESSION_DIR, f"diagnostic_{platform}.png")
            if os.path.exists(diag_png_path):
                self.send_response(200)
                self._cors()
                self.send_header('Content-Type', 'image/png')
                self.end_headers()
                with open(diag_png_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self._respond(404, {"error": "No screenshot evidence found yet."})
        elif self.path.startswith('/api/diagnostic-html'):
            platform = 'naver' if 'naver' in self.path else 'coupang'
            diag_html_path = os.path.join(SESSION_DIR, f"diagnostic_{platform}.html")
            if os.path.exists(diag_html_path):
                self.send_response(200)
                self._cors()
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(diag_html_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self._respond(404, {"error": "No HTML evidence found yet."})
        else:
            self._respond(404, {"error": "Not found"})


    def do_POST(self):
        data = self._read_body()

        if self.path == '/api/direct-login':
            platform = data.get('platform', 'naver')
            username = data.get('username', '')
            password = data.get('password', '')

            if not username or not password:
                self._respond(400, {"success": False, "error": "username and password required"})
                return

            print(f"\n🔐 [DIRECT LOGIN] Platform={platform} User={username[:3]}***")
            success, cookie_count, message = try_playwright_login(platform, username, password)

            self._respond(200, {
                "success": success,
                "platform": platform,
                "cookie_count": cookie_count,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

        elif self.path == '/api/trigger-affiliate-login':
            platform = data.get('platform', 'coupang')
            print(f"\n⚡ [TRIGGER LOGIN] Platform={platform}")
            self._respond(200, {
                "status": "QUEUED",
                "platform": platform,
                "message": f"Login request received for {platform}.",
                "timestamp": datetime.now().isoformat()
            })

        elif self.path == '/api/inject-cookies':
            # ✅ Manual cookie injection from browser DevTools
            platform = data.get('platform', 'naver')
            cookies_raw = data.get('cookies', [])

            if not cookies_raw:
                self._respond(400, {"success": False, "error": "cookies array is required"})
                return

            session_path = get_session_path(platform)
            storage_state = {"cookies": cookies_raw, "origins": []}
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(storage_state, f, ensure_ascii=False, indent=2)

            cnt, has_auth = inspect_session(platform)
            print(f"[COOKIE INJECT] {platform}: {cnt} cookies saved, auth={has_auth}")

            self._respond(200, {
                "success": has_auth,
                "platform": platform,
                "cookie_count": cnt,
                "authenticated": has_auth,
                "message": f"{'✅ 인증 쿠키 저장 완료!' if has_auth else '⚠️ 쿠키 저장됨 - 인증 쿠키 없음 (NID_AUT/NID_SES 확인 필요)'}",
                "timestamp": datetime.now().isoformat()
            })

        elif self.path == '/api/test-link':
            url = data.get('url', '')
            platform = data.get('platform', 'naver')
            step_logs = []

            def log_step(step_name, detail):
                msg = f"[{step_name}] {detail}"
                print(msg, flush=True)
                step_logs.append(msg)

            if not url:
                self._respond(400, {"success": False, "error": "url required", "logs": step_logs})
                return

            log_step("STEP 1", f"Target Platform: {platform.upper()} | Input URL: {url}")
            
            # Verify session file
            session_path = get_session_path(platform)
            cnt, has_auth = inspect_session(platform)
            log_step("STEP 2", f"StorageState check: File Exists={os.path.exists(session_path)}, Cookies Count={cnt}, Auth Valid={has_auth}")

            if not os.path.exists(session_path) or cnt == 0:
                log_step("STEP 2 FAIL", "No session file found on Render ephemeral disk. Please re-inject cookies in Admin UI.")
                self._respond(200, {
                    "success": False,
                    "error": "세션 파일이 없습니다 (Render 서버가 재시작되었을 수 있습니다). 쿠키를 어드민에서 다시 저장해 주세요.",
                    "session_state": "NOT_AUTHENTICATED",
                    "logs": step_logs
                })
                return

            try:
                from playwright.sync_api import sync_playwright
                log_step("STEP 3", "Launching Playwright Chromium (Stealth mode)...")
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-blink-features=AutomationControlled",
                            "--disable-dev-shm-usage"
                        ]
                    )
                    context = browser.new_context(
                        storage_state=session_path,
                        viewport={"width": 1366, "height": 768},
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                        locale="ko-KR",
                        timezone_id="Asia/Seoul"
                    )

                    # Remove webdriver flag for anti-bot
                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                        window.chrome = { runtime: {} };
                    """)

                    page = context.new_page()

                    log_step("STEP 4", f"Navigating to URL: {url}")
                    response = None
                    try:
                        response = page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    except Exception as goto_err:
                        log_step("STEP 4 WARN", f"Goto warning: {goto_err}")

                    status_code = response.status if response else "UNKNOWN"
                    log_step("STEP 5", f"HTTP Response Status Code: {status_code}")

                    page.wait_for_timeout(2500)

                    # ──────────────────────────────────────────────────────────
                    # STEP 5.5: EVIDENCE-FIRST PAGE INSPECTION & ARTIFACT DUMP
                    # ──────────────────────────────────────────────────────────
                    applied_cookies = context.cookies()
                    cookies_count = len(applied_cookies)
                    page_title = page.title()
                    html_content = page.content()
                    html_size = len(html_content.encode('utf-8'))
                    
                    has_login_form = bool(page.query_selector('input[type="password"], #id, #pw, #username, input[name="id"]'))
                    has_captcha = "captcha" in html_content.lower() or "recaptcha" in html_content.lower() or "bot" in html_content.lower()

                    log_step("STEP 5.5a", f"Applied Cookies Count in Browser Context: {cookies_count}")
                    log_step("STEP 5.5b", f"Landed Final URL: {page.url}")
                    log_step("STEP 5.5c", f"Document Title: '{page.title()}'")
                    log_step("STEP 5.5d", f"Contains Login Form: {'YES (Redirected/Not Logged In)' if has_login_form else 'NO'}")
                    log_step("STEP 5.5e", f"Contains CAPTCHA/Anti-Bot: {'YES (Bot Blocked)' if has_captcha else 'NO'}")
                    log_step("STEP 5.5f", f"HTML Content Size: {html_size:,} bytes")

                    # Save Evidence Artifacts
                    diag_png_path = os.path.join(SESSION_DIR, f"diagnostic_{platform}.png")
                    diag_html_path = os.path.join(SESSION_DIR, f"diagnostic_{platform}.html")
                    
                    try:
                        page.screenshot(path=diag_png_path, full_page=False)
                        log_step("STEP 5.5g", f"Screenshot Evidence Saved: {diag_png_path}")
                    except Exception as ss_err:
                        log_step("STEP 5.5g WARN", f"Screenshot save error: {ss_err}")

                    try:
                        with open(diag_html_path, "w", encoding="utf-8") as hf:
                            hf.write(html_content)
                        log_step("STEP 5.5h", f"HTML Evidence Saved: {diag_html_path}")
                    except Exception as html_err:
                        log_step("STEP 5.5h WARN", f"HTML save error: {html_err}")
                    # ──────────────────────────────────────────────────────────

                    # Check for bot detection or login redirect
                    landed_url = page.url.lower()
                    if has_login_form or "login" in landed_url or "nidlogin" in landed_url:
                        log_step("STEP 5 WARN", "🚨 로그인 폼 감지됨: 쿠키 세션이 유효하지 않거나 적용되지 않았습니다.")

                    if status_code in [403, 418] or has_captcha:
                        log_step("STEP 5 ERROR", f"🚨 봇 차단/캡차 감지됨! HTTP {status_code}")

                    # STEP 6: Metadata & Link extraction
                    log_step("STEP 6", "Extracting OpenGraph metadata and Product details...")

                    try:
                        title = page.evaluate("() => document.querySelector('meta[property=\"og:title\"]')?.content || document.title || ''")
                    except Exception:
                        title = "[제목 수급 실패]"

                    try:
                        image = page.evaluate("() => document.querySelector('meta[property=\"og:image\"]')?.content || ''")
                    except Exception:
                        image = ""

                    final_url = page.url
                    log_step("STEP 7", f"SUCCESS | Title: '{title[:30]}...' | Final Link: {final_url}")
                    browser.close()

                self._respond(200, {
                    "success": True,
                    "platform": platform,
                    "title": title,
                    "image": image,
                    "price": "[실가 수급 완료 - Playwright]",
                    "affiliate_link": final_url,
                    "session_state": "AUTHENTICATED",
                    "logs": step_logs
                })
            except Exception as e:
                log_step("STEP 7 ERROR", f"Execution Exception: {str(e)}")
                self._respond(200, {
                    "success": False,
                    "error": str(e),
                    "session_state": "AUTHENTICATED_BUT_FETCH_FAILED",
                    "logs": step_logs
                })



        else:
            self._respond(404, {"error": "Not found"})


# ─────────────────────────────────────────────────
# 자율 수집 루프 (30분마다 토스 수집 → DB 갱신 → Git Push)
# ─────────────────────────────────────────────────
def git_push_db():
    try:
        subprocess.run(["git", "config", "user.name",  "MORVIX Render Server"], cwd=BASE_DIR)
        subprocess.run(["git", "config", "user.email", "render@morvix.io"],      cwd=BASE_DIR)
        subprocess.run(["git", "add", "morvix_shop_db.json"],                    cwd=BASE_DIR)
        diff = subprocess.run(["git", "diff", "--staged", "--quiet"],            cwd=BASE_DIR)
        if diff.returncode != 0:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            subprocess.run(["git", "commit", "-m", f"chore(render): Auto-ingest Toss deals @ {now_str}"], cwd=BASE_DIR)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR)
            print(f"[{now_str}] ✅ Git Push 완료 → Vercel 자동 배포 시작", flush=True)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️ 변경사항 없음 - Push 생략", flush=True)
    except Exception as e:
        print(f"❌ Git Push 오류: {e}", flush=True)

def autonomous_harvest_loop():
    """HARVEST_INTERVAL마다 토스 수집 → DB 갱신 → Git Push 자동 루프"""
    print(f"🤖 [AUTO LOOP] 자율 수집 루프 시작 ({HARVEST_INTERVAL//60}분 간격)", flush=True)
    while True:
        try:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🕐 토스 파트너 수집 시작...", flush=True)
            result = subprocess.run(
                [sys.executable, os.path.join(BASE_DIR, "worker", "sharelink_toss_harvester.py")],
                capture_output=True, text=True, cwd=BASE_DIR, timeout=600
            )
            # 수집기 전체 출력을 로그에 표시
            if result.stdout:
                print(f"[HARVESTER STDOUT]\n{result.stdout[-1000:]}", flush=True)
            if result.stderr:
                print(f"[HARVESTER STDERR]\n{result.stderr[-500:]}", flush=True)

            if result.returncode == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 수집 완료", flush=True)
                git_push_db()
            else:
                print(f"❌ 수집기 returncode={result.returncode}", flush=True)
        except Exception as e:
            print(f"❌ 자율 루프 예외: {e}", flush=True)
        print(f"😴 {HARVEST_INTERVAL//60}분 후 재가동...", flush=True)
        time.sleep(HARVEST_INTERVAL)

def ensure_playwright_browsers():
    """런타임 시작 시 Playwright Chromium 브라우저 자동 설치"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, args=["--no-sandbox"])
            b.close()
        print("✅ Playwright Chromium: READY", flush=True)
    except Exception:
        print("⚠️ Chromium not found - installing now...", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=False
        )
        if result.returncode == 0:
            print("✅ Chromium install: COMPLETE", flush=True)
        else:
            print("❌ Chromium install FAILED", flush=True)

def restore_toss_session():
    """세션 파일 확인 및 Render 환경변수 TOSS_SESSION_B64 백업 복원"""
    session_dir = os.path.join(BASE_DIR, "scratch")
    os.makedirs(session_dir, exist_ok=True)
    session_path = os.path.join(session_dir, "toss_sharelink_session.json")

    # 1. 이미 최신 세션 파일이 존재하면 그대로 사용
    if os.path.exists(session_path) and os.path.getsize(session_path) > 100:
        print(f"✅ 레포지토리 저장 세션 파일 사용: {session_path}", flush=True)
        return

    # 2. 파일이 없거나 유효하지 않은 경우 환경변수에서 복원
    b64 = os.environ.get("TOSS_SESSION_B64", "")
    if not b64:
        print("⚠️ 세션 파일 및 TOSS_SESSION_B64 환경변수 없음 - 세션 없이 수집 시도", flush=True)
        return
    try:
        import base64
        decoded = base64.b64decode(b64.encode("utf-8")).decode("utf-8")
        with open(session_path, "w", encoding="utf-8") as f:
            f.write(decoded)
        print(f"✅ 환경변수에서 토스 세션 복원 완료: {session_path}", flush=True)
    except Exception as e:
        print(f"❌ 세션 복원 오류: {e}", flush=True)


def run():
    # 1. 토스 세션 복원 (Render 환경변수 → 파일)
    restore_toss_session()

    # 2. Playwright 브라우저 설치 확인
    ensure_playwright_browsers()

    # 3. 자율 수집 루프 백그라운드 스레드로 즉시 시작
    harvest_thread = threading.Thread(target=autonomous_harvest_loop, daemon=True)
    harvest_thread.start()

    port = int(os.getenv("PORT", "10000"))
    print("=" * 60)
    print(f"🚀 MORVIX RENDER CLOUD WORKER ONLINE — PORT {port}")
    print(f"📡 https://morvix-shop.onrender.com")
    print(f"🤖 AUTO HARVEST LOOP: 1분마다 자동 수집 → Git Push")
    print("=" * 60)
    httpd = HTTPServer(('0.0.0.0', port), MorvixBridgeHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
