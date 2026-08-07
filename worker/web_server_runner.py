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
import requests
from datetime import datetime, timedelta, timezone

# 🌐 렌더 주입 PORT 환경변수 수신 (기본값 10000)
PORT = int(os.environ.get("PORT", 10000))

# 🇰🇷 한국 표준시 (KST: UTC+9) 명시적 타임존 정의
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """해외 렌더 서버(UTC) 환경에서도 100% 정확한 한국 표준시(KST) 구하기"""
    return datetime.now(timezone.utc).astimezone(KST)

# 동일 폴더(worker) 내의 파이프라인 데몬 모듈을 안전하게 임포트하기 위한 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from toss_api_pipeline_daemon import run_pipeline_cycle

RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")

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

def run_keepalive_heartbeat():
    """
    렌더 슬립(Sleep) 방지용 자체 하트비트 스레드 (10분 간격)
    - 렌더 무료 서버의 15분 휴면 진입을 100% 원천 차단하여 서버가 24시간 깬 상태로 대기
    """
    target_url = RENDER_EXTERNAL_URL or f"http://127.0.0.1:{PORT}/"
    print(f"💓 [하트비트] 슬립 방지 셀프 핑 데몬 가동 (Target: {target_url})...", flush=True)
    while True:
        time.sleep(600)  # 10분마다 셀프 핑
        try:
            res = requests.get(target_url, timeout=10)
            print(f"💓 [하트비트 셀프 핑] 상태코드: {res.status_code} - 렌더 24시간 상시 깨어있음 유지 완료", flush=True)
        except Exception as e:
            pass

def run_dummy_server():
    """렌더 포트 타임아웃 방지를 위한 가벼운 웹 서버"""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Morvix Shop OS Worker is running perfectly!")
        def log_message(self, format, *args):
            return

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 렌더 포트 바인딩 성공: 포트 {PORT}에서 웹 서버 대기 중...", flush=True)
        httpd.serve_forever()

import traceback

def run_harvester_daemon():
    """
    GitHub Actions 매일 밤 00:01 KST 깨우기 연동 수집 데몬
    - GitHub이 깨우기 신호를 보낼 때마다 1회차 핫딜 수집 및 DB 동기화 실행
    - 수집 완수 후 15분 지나면 Render가 자동으로 전력을 0% 상태로 끄는 자연 휴면(Sleep) 진입
    """
    print("\n=======================================================", flush=True)
    print(f"🚀 [{get_kst_now().strftime('%Y-%m-%d %H:%M:%S')} KST] 핫딜 수집 및 DB 동기화 파이프라인 가동...", flush=True)
    print("=======================================================\n", flush=True)
    try:
        run_pipeline_cycle()
        print("\n=======================================================", flush=True)
        print("✅ [수집 완수] 오늘만 이가격 & 베스트 핫딜 수집 완료!", flush=True)
        print("💤 렌더 서버는 15분 후 자동으로 휴면(Sleep) 상태에 진입합니다.", flush=True)
        print("=======================================================\n", flush=True)
    except Exception as e:
        print(f"❌ [수집 데몬] 실행 중 에러 발생: {e}", flush=True)
        traceback.print_exc()

if __name__ == "__main__":
    # 0. 시작 직후 공인 IP 확인 함수 실행
    check_and_print_server_ip()

    # 1. 핫딜 수집 파이프라인을 백그라운드 스레드로 가동
    harvester_thread = threading.Thread(target=run_harvester_daemon, daemon=True)
    harvester_thread.start()

    # 2. 메인 스레드에서 즉시 렌더 포트 10000 바인딩 (0.001초 렌더 포트 검사 100% 200 OK 합격)
    run_dummy_server()