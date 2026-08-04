"""
=============================================================================
MORVIX SHOP OS - Render Web Service Dummy Port & Harvester Runner
worker/web_server_runner.py
=============================================================================
"""
import http.server
import socketserver
import threading
import os
import time

PORT = int(os.environ.get("PORT", 10000))

def run_dummy_server():
    """렌더 포트 타임아웃 방지를 위한 가벼운 웹 서버"""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Morvix Shop OS Worker is running perfectly!")
        def log_message(self, format, *args):
            return # 로그가 너무 많이 찍히는 것 방지

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 렌더 포트 바인딩 성공: 포트 {PORT}에서 웹 서버 대기 중...", flush=True)
        httpd.serve_forever()

def run_harvester_daemon():
    """백그라운드에서 수집기 데몬 실행"""
    time.sleep(5) # 서버가 먼저 뜬 후 수집기 구동
    daemon_script = os.path.join(os.path.dirname(__file__), "toss_365_unattended_daemon.py")
    while True:
        print("🚀 [통합 데몬] 수집기 루프 실행 시작...", flush=True)
        os.system(f"python {daemon_script}")
        print("💤 [통합 데몬] 대기 중 (3시간 후 재실행)...", flush=True)
        time.sleep(10800) # 3시간 대기

if __name__ == "__main__":
    # 1. 웹 서버를 백그라운드 스레드로 실행 (포트 바인딩 해결)
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # 2. 메인 스레드에서는 수집기 데몬 실행
    run_harvester_daemon()