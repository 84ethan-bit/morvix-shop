"""
=============================================================================
MORVIX SHOP OS - Render Background Worker Daemon
morvix_render_worker.py

[정시 스케줄링 관리자]
1. KST(한국 표준시) 기준 00:01 및 12:01 매일 정시 수집 자동 가동
2. 서버 최초 구동 시 즉시 1회 수집을 실행하여 테스트 및 초기 적재 수행
3. 이후부터는 다음 정시(00:01 또는 12:01)까지 안전 대기
4. 자정 00:00 KST DB 전수 리셋 및 신규 수집 준비
=============================================================================
"""
import os
import json
import sys
import time
import subprocess
import threading
from datetime import datetime, timezone, timedelta as td
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "morvix_shop_db.json")

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CHROMIUM_READY = True
print(f"📦 PLAYWRIGHT_BROWSERS_PATH = {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'default')}")

WORKER_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(WORKER_DIR, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)


class MorvixBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_HEAD(self):
        if self.path in ['/health', '/']:
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

    def _respond(self, code, payload):
        self.send_response(code)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        if self.path in ['/health', '/']:
            self._respond(200, {
                "status": "MORVIX_RENDER_WORKER_ONLINE",
                "mode": "TOSS_SHOPPING_HYBRID_PIPELINE",
                "schedule": "KST 00:01 & 12:01 DAILY (IMMEDIATE TEST MODE)",
                "timestamp": datetime.now().isoformat()
            })
        else:
            self._respond(404, {"error": "Not found"})

    def do_POST(self):
        self._respond(404, {"error": "Not found"})


def check_midnight_today_price_reset():
    """매일 00:00 KST 전체 상품 DB 100% 리셋"""
    try:
        KST = timezone(td(hours=9))
        now_kst = datetime.now(KST)
        if now_kst.hour == 0 and now_kst.minute <= 15:
            db_path = os.path.join(BASE_DIR, "morvix_shop_db.json")
            if os.path.exists(db_path):
                with open(db_path, "r", encoding="utf-8") as f:
                    db = json.load(f)

                before_count = len(db.get("products", []))
                db["products"] = []
                print(f"🌙 [00:00 KST 자정 전수 리셋] 기존 상품 {before_count}개 삭제 ➔ 신규 수집 준비 완료", flush=True)
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
                return True
    except Exception as e:
        print(f"⚠️ 자정 전수 리셋 오류: {e}", flush=True)
    return False


def get_seconds_until_next_target_time():
    """다음 목표 시각(00:01 또는 12:01)까지 남은 초(second) 계산"""
    KST = timezone(td(hours=9))
    now_kst = datetime.now(KST)
    
    target_0001_today = now_kst.replace(hour=0, minute=1, second=0, microsecond=0)
    target_1201_today = now_kst.replace(hour=12, minute=1, second=0, microsecond=0)
    target_0001_tomorrow = (now_kst + td(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
    
    if now_kst < target_0001_today:
        next_target = target_0001_today
    elif now_kst < target_1201_today:
        next_target = target_1201_today
    else:
        next_target = target_0001_tomorrow
        
    wait_seconds = (next_target - now_kst).total_seconds()
    print(f"⏰ [KST 정시 스케줄러] 현재 KST: {now_kst.strftime('%Y-%m-%d %H:%M:%S')} | 다음 수집 예정 시각: {next_target.strftime('%Y-%m-%d %H:%M:%S')} (남은 대기시간: {int(wait_seconds//3600)}시간 {int((wait_seconds%3600)//60)}분)", flush=True)
    return wait_seconds


def run_pipeline():
    """1번 및 2번 통합 수집 파이프라인 순차 실행 함수"""
    try:
        check_midnight_today_price_reset()

        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🕐 토스 파트너 정시 수집 시작...", flush=True)
        
        # 1. 1번 수집기('오늘만 이가격') 실행
        script_candidate1 = os.path.join(BASE_DIR, "worker", "sharelink_toss_harvester.py")
        script_candidate2 = os.path.join(BASE_DIR, "sharelink_toss_harvester.py")
        harvester_script = script_candidate1 if os.path.exists(script_candidate1) else script_candidate2

        print(f"📍 1번 수집기 실행 파일 경로: {harvester_script}", flush=True)

        cmd = [sys.executable, "-u", harvester_script]
        env = dict(os.environ)
        env["PYTHONUNBUFFERED"] = "1"
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=BASE_DIR, env=env, bufsize=1)

        for line in proc.stdout:
            print(line, end="", flush=True)

        proc.wait()
        if proc.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 1번 수집 완료", flush=True)
        else:
            print(f"❌ 1번 수집기 returncode={proc.returncode}", flush=True)

        # 2. 1번 완료 직후 2번 BEST 수집기 연쇄 실행
        best_script1 = os.path.join(BASE_DIR, "worker", "harvest_best_ranking.py")
        best_script2 = os.path.join(BASE_DIR, "harvest_best_ranking.py")
        best_script = best_script1 if os.path.exists(best_script1) else best_script2

        if os.path.exists(best_script):
            print(f"🚀 [연동 실행] 1번 완료 후 2번 BEST 수집기({os.path.basename(best_script)})를 가동합니다...", flush=True)
            best_cmd = [sys.executable, "-u", best_script]
            best_proc = subprocess.Popen(best_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=BASE_DIR, env=env, bufsize=1)
            
            for line in best_proc.stdout:
                print(line, end="", flush=True)
            best_proc.wait()
            
            if best_proc.returncode == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 2번 BEST 수집 및 통합 DB 적재 완료", flush=True)
            else:
                print(f"❌ 2번 수집기 returncode={best_proc.returncode}", flush=True)
        else:
            print(f"❌ 연동할 2번 BEST 수집기 파일을 찾을 수 없습니다: {best_script}", flush=True)

    except Exception as e:
        print(f"❌ 정시 수집 루프 예외: {e}", flush=True)


def autonomous_harvest_loop():
    """서버 구동 즉시 1회 실행 후, 다음 정시부터 스케줄링 루프 가동[cite: 2]"""
    print("🤖 [AUTO LOOP] 기동 즉시 수집 테스트 모드 가동", flush=True)

    print("🚀 [즉시 실행] 서버 최초 구동 테스트를 위해 수집 파이프라인을 즉시 실행합니다...")
    run_pipeline()

    while True:
        sleep_sec = get_seconds_until_next_target_time()
        print(f"⏳ 지정된 KST 정시까지 대기 모드로 진입합니다. (대기 시간: {int(sleep_sec//3600)}시간 {int((sleep_sec%3600)//60)}분)")
        time.sleep(sleep_sec)
        run_pipeline()


def ensure_playwright_browsers():
    """Playwright Chromium 브라우저 설치 검증"""
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


def restore_toss_session():
    """토스 2FA 세션 복원"""
    session_dir = os.path.join(BASE_DIR, "scratch")
    os.makedirs(session_dir, exist_ok=True)
    session_path = os.path.join(session_dir, "toss_sharelink_session.json")

    if os.path.exists(session_path) and os.path.getsize(session_path) > 100:
        print(f"✅ 승인된 최신 세션 파일 사용: {session_path}", flush=True)
        return

    b64 = os.environ.get("TOSS_SESSION_B64", "").strip()
    if b64:
        try:
            import base64
            decoded = base64.b64decode(b64.encode("utf-8")).decode("utf-8")
            parsed = json.loads(decoded)
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            print(f"🔑 [Render Env] 세션 적용 완료: {session_path}", flush=True)
        except Exception as e:
            print(f"❌ 세션 디코딩 실패: {e}", flush=True)


def run():
    restore_toss_session()
    ensure_playwright_browsers()

    harvest_thread = threading.Thread(target=autonomous_harvest_loop, daemon=True)
    harvest_thread.start()

    port = int(os.getenv("PORT", "10000"))
    print("=" * 60)
    print(f"🚀 MORVIX RENDER CLOUD WORKER ONLINE — PORT {port}")
    print(f"⏰ IMMEDIATE TEST MODE + KST SCHEDULED HARVEST")
    print("=" * 60)
    httpd = HTTPServer(('0.0.0.0', port), MorvixBridgeHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run()