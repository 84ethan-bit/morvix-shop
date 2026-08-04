"""
=============================================================================
MORVIX SHOP OS - Integrated Scheduler (Path-Fixed v2)
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

# 현재 파일 위치 기준, 또는 상위 폴더를 기준으로 올바른 worker 경로 지정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(BASE_DIR) == "worker":
    # 스크립트가 worker 폴더 안에서 실행되는 경우
    WORKER_DIR = BASE_DIR
    BASE_DIR = os.path.dirname(BASE_DIR)
else:
    # 스크립트가 루트에서 실행되는 경우
    WORKER_DIR = os.path.join(BASE_DIR, "worker")

def print_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [SCHEDULER] {msg}", flush=True)

def run_pipeline():
    print_log(f"🚀 [오케스트레이터] 파이프라인 가동 시작 (BASE_DIR: {BASE_DIR})")
    print_log(f"📁 [디버그] WORKER_DIR 경로: {WORKER_DIR}")
    
    if os.path.exists(WORKER_DIR):
        print_log(f"📁 [디버그] worker 폴더 내 파일 목록: {os.listdir(WORKER_DIR)}")
    else:
        print_log(f"❌ [오류] worker 폴더를 찾을 수 없습니다: {WORKER_DIR}")
        return

    # 1번 수집기 실행 (오늘만 이가격)
    worker1_path = os.path.join(WORKER_DIR, "sharelink_toss_harvester.py")
    if os.path.exists(worker1_path):
        print_log(f"📦 [1번 수집기] 실행 시도: {worker1_path}")
        try:
            result = subprocess.run([sys.executable, worker1_path], check=True, cwd=BASE_DIR, capture_output=True, text=True)
            print(result.stdout)
            print_log("✅ [1번 수집기] 완료")
        except subprocess.CalledProcessError as e:
            print_log(f"❌ [1번 수집기] 실행 실패 (에러코드 {e.returncode}):\n{e.stderr}")
        except Exception as e:
            print_log(f"❌ [1번 수집기] 예외 발생: {e}")
    else:
        print_log(f"❌ [1번 수집기] 파일을 찾을 수 없음: {worker1_path}")
            
    time.sleep(5)

    # 2번 수집기 실행 (BEST 랭킹)
    worker2_path = os.path.join(WORKER_DIR, "harvest_best_ranking.py")
    if os.path.exists(worker2_path):
        print_log(f"🏆 [2번 수집기] 실행 시도: {worker2_path}")
        try:
            result = subprocess.run([sys.executable, worker2_path], check=True, cwd=BASE_DIR, capture_output=True, text=True)
            print(result.stdout)
            print_log("✅ [2번 수집기] 완료")
        except subprocess.CalledProcessError as e:
            print_log(f"❌ [2번 수집기] 실행 실패 (에러코드 {e.returncode}):\n{e.stderr}")
        except Exception as e:
            print_log(f"❌ [2번 수집기] 예외 발생: {e}")
    else:
        print_log(f"❌ [2번 수집기] 파일을 찾을 수 없음: {worker2_path}")

    print_log("🎉 [오케스트레이터] 전체 파이프라인 작업 종료.")

if __name__ == "__main__":
    print_log("🛡️ Morvix Shop OS 통합 스케줄러 백그라운드 구동 시작")
    
    print_log("🚀 서버 부팅 직후 최초 수집 파이프라인을 즉시 실행합니다.")
    try:
        run_pipeline()
    except Exception as err:
        print_log(f"⚠️ 최초 실행 예외 발생: {err}")
    
    while True:
        print_log("⏳ 다음 작업 주기(6시간) 대기 중...")
        time.sleep(21600)
        try:
            run_pipeline()
        except Exception as err:
            print_log(f"⚠️ 스케줄러 루프 예외 발생: {err}")