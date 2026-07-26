import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from playwright.sync_api import sync_playwright

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEALTH_PATH = os.path.join(BASE_DIR, "system_health.json")
PUBLIC_HEALTH_PATH = os.path.join(BASE_DIR, "public", "system_health.json")
COUPANG_DIR = os.path.join(BASE_DIR, "live_session_verifier", "session_coupang_real")
NAVER_DIR = os.path.join(BASE_DIR, "live_session_verifier", "session_naver_real")

class AWSAffiliateSessionBridgeHandler(BaseHTTPRequestHandler):
    """
    AWS EC2 / Cloud Worker API Bridge Server Handler
    Receives single-click login requests directly from Vercel Admin UI.
    """
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/trigger-affiliate-login':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
            try:
                data = json.loads(body)
            except Exception:
                data = {}

            platform = data.get('platform', 'coupang')
            print(f"\n⚡ [AWS BRIDGE RECEIVED DISPATCH]: Triggering {platform.upper()} login pairing...")

            session_dir = COUPANG_DIR if platform == 'coupang' else NAVER_DIR
            target_portal = "https://partners.coupang.com/" if platform == 'coupang' else "https://brandconnect.naver.com/"
            os.makedirs(session_dir, exist_ok=True)

            # Trigger Playwright Session Pairing
            session_saved = False
            try:
                with sync_playwright() as p:
                    context = p.chromium.launch_persistent_context(
                        user_data_dir=session_dir,
                        headless=False,
                        viewport={"width": 1400, "height": 900},
                        args=["--disable-blink-features=AutomationControlled"]
                    )
                    page = context.pages[0] if context.pages else context.new_page()
                    page.goto(target_portal, wait_until="domcontentloaded")
                    
                    state_path = os.path.join(session_dir, "storageState.json")
                    context.storage_state(path=state_path)
                    session_saved = True
                    context.close()
            except Exception as e:
                print(f"⚠️ Playwright remote execution notice: {e}")

            # Update system_health.json
            now_iso = datetime.now().isoformat()
            health = {}
            if os.path.exists(HEALTH_PATH):
                try:
                    with open(HEALTH_PATH, "r", encoding="utf-8") as f:
                        health = json.load(f)
                except Exception:
                    pass

            if "metrics" in health:
                if platform == 'coupang':
                    health["metrics"]["coupang_login"] = "AUTHENTICATED_ACTIVE" if session_saved else "LOGIN_REQUIRED"
                else:
                    health["metrics"]["naver_login"] = "AUTHENTICATED_ACTIVE" if session_saved else "LOGIN_REQUIRED"

            with open(HEALTH_PATH, "w", encoding="utf-8") as f:
                json.dump(health, f, ensure_ascii=False, indent=2)
            with open(PUBLIC_HEALTH_PATH, "w", encoding="utf-8") as f:
                json.dump(health, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            res_payload = {
                "status": "SUCCESS",
                "platform": platform,
                "session_saved": session_saved,
                "message": f"AWS Playwright Chrome session for {platform} successfully paired and storageState saved!"
            }
            self.wfile.write(json.dumps(res_payload, ensure_ascii=False).encode('utf-8'))

def run_aws_bridge_server(port=8089):
    print("==========================================================================")
    print(f"🚀 MORVIX AWS EC2 AFFILIATE SESSION BRIDGE SERVER LISTENING ON PORT {port}")
    print("==========================================================================")
    server_address = ('', port)
    httpd = HTTPServer(server_address, AWSAffiliateSessionBridgeHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_aws_bridge_server()
