"""
=============================================================================
MORVIX SHOP OS - Render Web Service Dummy Port & Harvester Runner with IP Checker
worker/web_server_runner.py
=============================================================================
"""
import http.server
import socketserver
import threading
import os
import time
import sys
import requests

PORT = int(os.environ.get("PORT", 10000))

def check_and_print_server_ip():
    """렌더 아웃바운드 공인 IP 확인 및 강제 로그 출력"""
    print("🌐 [RENDER IP CHECK] 외부 IP 조회 시도 중...", flush=True)
    try:
        # ipify 또는 다른 공인 IP 확인 서비스 활용
        res = requests.get('https://api.ipify.org?format=json', timeout=10)
        if res.status_code == 200:
            current_ip = res.json().get('ip')
            print(f"\n=======================================================", flush=True)
            print(f"🌐 [RENDER OUTBOUND IP]: {current_ip}", flush=True)
            print(f"💡 위 IP 주소를 토스 쉐어링크 Open API 설정 페이지에 등록하세요.", flush=True)
            print(f"=======================================================\n", flush=True)
        else:
            print(f"⚠️ IP 조회 응답 코드 이상: {res.status_code}", flush=True)
    except Exception as e:
        print(f"⚠️ 서버 IP 확인 중 예외 발생: {e}", flush=True)

def run_dummy_server():
    """렌더 포트 타임아웃 방지를 위한 가벼운 웹 서버"""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Morvix Shop OS Worker is running perfectly!")
        def log_message(self, format, *args):
            return

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 렌더 포트 바인딩 성공: 포트 {PORT}에서 웹 서버 대기 중...", flush=True)
        httpd.serve_forever()

def run_harvester_daemon():
    """백그라운드에서 API 수집기 데몬 실행"""
    time.sleep(5)
    # 기존 크롤링 데몬에서 새로운 토스 API 파이프라인 데몬으로 변경됨
    daemon_script = os.path.join(os.path.dirname(__file__), "toss_api_pipeline_daemon.py")
    while True:
        print("🚀 [통합 데몬] API 수집기 루프 실행 시작...", flush=True)
        os.system(f"python {daemon_script}")
        print("💤 [통합 데몬] 대기 중 (3시간 후 재실행)...", flush=True)
        time.sleep(10800)

if __name__ == "__main__":
    # 0. 시작 직후 공인 IP 확인 함수 실행
    check_and_print_server_ip()

    # 1. 웹 서버를 백그라운드 스레드로 실행
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # 2. 메인 스레드에서는 수집기 데몬 실행
    run_harvester_daemon()