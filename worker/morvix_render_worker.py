"""
=============================================================================
MORVIX SHOP OS - Integrated Scheduler (V56 Pipeline)
scheduler.py
=============================================================================
"""
import sys
import os
import time
import subprocess
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKER_DIR = os.path.join(BASE_DIR, "worker")

def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [SCHEDULER] {msg}", flush=True)

def run_pipeline():
    print_log("🚀 [오케스트레이터] 파이프라인 주기적 가동 시작...")
    
    # 1번 수집기 실행 (오늘만 이가격)
    worker1_path = os.path.join(WORKER_DIR, "sharelink_toss_harvester.py")
    if os.path.exists(worker1_path):
        print_log("📦 [1번 수집기] 오늘만 이가격 수집 가동...")
        try:
            subprocess.run([sys.executable, worker1_path], check=True, cwd=BASE_DIR)
            print_log("✅ [1번 수집기] 완료")
        except Exception as e:
            print_log(f"❌ [1번 수집기] 오류 발생: {e}")
            
    time.sleep(5)

    # 2번 수집기 실행 (BEST 랭킹)
    worker2_path = os.path.join(WORKER_DIR, "harvest_best_ranking.py")
    if os.path.exists(worker2_path):
        print_log("🏆 [2번 수집기] BEST 랭킹 수집 가동...")
        try:
            subprocess.run([sys.executable, worker2_path], check=True, cwd=BASE_DIR)
            print_log("✅ [2번 수집기] 완료")
        except Exception as e:
            print_log(f"❌ [2번 수집기] 오류 발생: {e}")

    print_log("🎉 [오케스트레이터] 전체 파이프라인 주기 작업 종료. 다음 주기를 대기합니다.")

if __name__ == "__main__":
    print_log("🛡️ Morvix Shop OS 통합 스케줄러 백그라운드 구동 시작")
    run_pipeline()
    
    while True:
        time.sleep(21600)  # 6시간 주기
        try:
            run_pipeline()
        except Exception as err:
            print_log(f"⚠️ 스케줄러 루프 예외 발생: {err}")