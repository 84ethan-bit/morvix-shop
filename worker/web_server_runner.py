"""
=============================================================================
MORVIX SHOP OS - Render Web Service Dummy Port & Smart Midnight Scheduler
worker/web_server_runner.py
=============================================================================
"""
import os
import sys
import http.server
import socketserver
import threading
import time
from datetime import datetime, timedelta
import requests

# 동일 폴더(worker) 내의 파이프라인 데몬 모듈을 안전하게 임포트하기 위한 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from toss_api_pipeline_daemon import run_pipeline_cycle

PORT = int(os.environ.get("PORT", 10000))

def check_and_print_server_ip():
    """렌더 아웃바운드 공인 IP 확인 및 강제 로그 출력"""
    print("🌐 [RENDER IP CHECK] 외부 IP 조회 시도 중...", flush=True)
    try:
        res = requests.get('https://api.ipify.org?format=json', timeout=10)
        if res.status_code == 200:
            current_ip = res.json().get('ip')
            print(f"\n=======================================================", flush=True)
            print(f"🌐 [RENDER OUTBOUND IP]: {current_ip}", flush=True)
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
    """
    스마트 자정(00:01) 스케줄러 데몬
    - 서버 켜지자마자 최초 1회 즉시 실행 (베스트 + 오늘만 이가격 모두 수집)
    - 이후부터는 매일 밤 00시 01분에 작동
    - 오늘만 이가격: 매일 00시 01분 수집
    - 베스트 상품: 3일에 한 번 00시 01분 수집
    """
    # 1. 서버 시작 직후 최초 1회 실행 (베스트 포함 전체 수집)
    print("🚀 [스마트 데몬] 서버 기동 직후 최초 수집 실행 시작...", flush=True)
    try:
        run_pipeline_cycle(refresh_best=True)
    except Exception as e:
        print(f"❌ [스마트 데몬] 최초 실행 중 에러 발생: {e}", flush=True)

    day_counter = 0  # 3일 주기를 카운트하기 위한 변수

    while True:
        # 현재 시간 기준으로 다음 날 00시 01분까지 남은 초(seconds)를 계산
        now = datetime.now()
        target_time = (now + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
        sleep_seconds = (target_time - now).total_seconds()
        
        hours_left = sleep_seconds / 3600
        print(f"💤 [스마트 데몬] 다음 수집 예정 시간: {target_time.strftime('%Y-%m-%d %H:%M:%S')} (약 {hours_left:.1f}시간 후 대기 중)...", flush=True)
        
        time.sleep(sleep_seconds)

        # 자정 00시 01분이 되어 깨어남
        day_counter += 1
        # 3일에 한 번은 베스트 상품도 함께 재수집 (1, 4, 7일째...)
        refresh_best = (day_counter % 3 == 1)

        print(f"🚀 [스마트 데몬] 정기 수집 실행 (베스트 재수집 여부: {refresh_best})...", flush=True)
        try:
            run_pipeline_cycle(refresh_best=refresh_best)
        except Exception as e:
            print(f"❌ [스마트 데몬] 정기 실행 중 에러 발생: {e}", flush=True)

if __name__ == "__main__":
    # 0. 시작 직후 공인 IP 확인 함수 실행
    check_and_print_server_ip()

    # 1. 웹 서버를 백그라운드 스레드로 실행
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # 2. 메인 스레드에서는 스마트 자정 스케줄러 데몬 실행
    run_harvester_daemon()