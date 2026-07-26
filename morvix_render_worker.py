import os
import json
import sys
import time
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────
# AUTO-INSTALL PLAYWRIGHT CHROMIUM IN BACKGROUND
# (Server starts immediately, Chromium installs async)
# ─────────────────────────────────────────────────
CHROMIUM_READY = False

def install_chromium_background():
    global CHROMIUM_READY
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, args=["--no-sandbox"])
            b.close()
        print("✅ Playwright Chromium: READY (already installed)")
        CHROMIUM_READY = True
    except Exception:
        print("⚠️ Chromium not found — installing in background...")
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=False
        )
        if result.returncode == 0:
            print("✅ Chromium background install: COMPLETE")
            CHROMIUM_READY = True
        else:
            print("❌ Chromium install failed")

threading.Thread(target=install_chromium_background, daemon=True).start()
# ─────────────────────────────────────────────────




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(BASE_DIR, "sessions")
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
            naver_cnt, naver_auth = inspect_session('naver')
            coupang_cnt, coupang_auth = inspect_session('coupang')
            self._respond(200, {
                "status": "MORVIX_RENDER_WORKER_ONLINE",
                "chromium_ready": CHROMIUM_READY,
                "timestamp": datetime.now().isoformat(),
                "sessions": {
                    "naver": {"cookie_count": naver_cnt, "authenticated": naver_auth},
                    "coupang": {"cookie_count": coupang_cnt, "authenticated": coupang_auth}
                },
                "endpoints": [
                    "POST /api/direct-login",
                    "POST /api/trigger-affiliate-login",
                    "GET /api/verify-session?platform=naver",
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

        else:
            self._respond(404, {"error": "Not found"})


def run():
    port = int(os.getenv("PORT", "5000"))
    print("=" * 60)
    print(f"🚀 MORVIX RENDER CLOUD WORKER ONLINE — PORT {port}")
    print(f"📡 https://morvix-shop.onrender.com")
    print(f"🔐 POST /api/direct-login     (Playwright auto login)")
    print(f"🍪 POST /api/inject-cookies   (manual cookie bridge)")
    print(f"✅ GET  /api/verify-session   (check auth cookies)")
    print("=" * 60)
    httpd = HTTPServer(('', port), MorvixBridgeHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
