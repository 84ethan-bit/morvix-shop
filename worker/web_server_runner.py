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
from datetime import datetime, timedelta, timezone

# 🇰🇷 한국 표준시 (KST: UTC+9) 명시적 타임존 정의
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """해외 렌더 서버(UTC) 환경에서도 100% 정확한 한국 표준시(KST) 구하기"""
    return datetime.now(timezone.utc).astimezone(KST)

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

def run_harvester_daemon():
    """
    스마트 자정(00:01) 스케줄러 데몬
    - 서버 켜지자마자 최초 1회 즉시 실행 (오늘만 이가격 수집 및 기존 베스트 통합 후 푸시)
    - 이후부터는 매일 밤 00시 01분에 정확히 깨어나 작동
    """
    # 1. 배포/서버 기동 직후 최초 1회 즉시 수집 실행
    print("\n=======================================================", flush=True)
    print("🚀 [배포 최초 수집] 서버 기동 직후 1회차 핫딜 수집 및 통합 시작...", flush=True)
    print("=======================================================\n", flush=True)
    try:
        run_pipeline_cycle()
    except Exception as e:
        print(f"❌ [스마트 데몬] 최초 실행 중 에러 발생: {e}", flush=True)

    while True:
        # 🇰🇷 해외 렌더 서버(UTC) 환경에서도 정확한 '한국 표준시(KST)' 기준 다음 00시 01분 계산
        now_kst = get_kst_now()
        target_time_kst = now_kst.replace(hour=0, minute=1, second=0, microsecond=0)
        if target_time_kst <= now_kst:
            target_time_kst += timedelta(days=1)
        
        sleep_seconds = max(1, (target_time_kst - now_kst).total_seconds())
        hours_left = sleep_seconds / 3600
        print(f"💤 [스마트 데몬] 다음 한국시간(KST) 00:01 수집 예정 시각: {target_time_kst.strftime('%Y-%m-%d %H:%M:%S')} KST (약 {hours_left:.2f}시간 후 대기 중)...", flush=True)
        
        time.sleep(sleep_seconds)

        # 자정 00시 01분이 되어 깨어남
        print(f"\n🚀 [스마트 데몬] 자정(00:01) 정기 수집 실행 (오늘만 이가격 갱신 & 통합)...", flush=True)
        try:
            run_pipeline_cycle()
        except Exception as e:
            print(f"❌ [스마트 데몬] 정기 실행 중 에러 발생: {e}", flush=True)

if __name__ == "__main__":
    # 0. 시작 직후 공인 IP 확인 함수 실행
    check_and_print_server_ip()

    # 1. 웹 서버를 백그라운드 스레드로 실행
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # 2. 렌더 슬립 방지 하트비트 셀프 핑 스레드 가동
    heartbeat_thread = threading.Thread(target=run_keepalive_heartbeat, daemon=True)
    heartbeat_thread.start()

    # 3. 메인 스레드에서는 최초 1회 수집 + 00:01 자정 스케줄러 데몬 실행
    run_harvester_daemon()