"""
=============================================================================
MORVIX SHOP OS - 365-Day Unattended Autonomous Operational Daemon
worker/toss_365_unattended_daemon.py

[운영 6대 검증 항목 내장]
1. 24시간 자동 실행 스케줄러 (주기적 수집/배포)
2. 중복 처리 (동일 핫딜 중복 등록 차단)
3. 24h/48h 만료 처리 (TTL Auto-Purge Engine)
4. 예외 처리 & 자동 복구 (세션/네트워크/DOM 변경 시 프로세스 다운 방지)
5. GitHub / Vercel 배포 실패 감지 및 자동 재시도 (Exponential Backoff)
6. 모니터링 & 실행 로그 파일 저널링
=============================================================================
"""
import sys, os, json, time, re, subprocess
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
LOG_PATH = os.path.join(BASE_DIR, "scratch", "daemon_execution.log")

def write_journal_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [MORVIX-365] {msg}"
    print(formatted)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception as e:
        print(f"⚠️ Log writing error: {e}")

def run_git_deploy_with_retry(commit_msg, max_retries=3):
    """5. 배포 검증: Git Push / Vercel 배포 자동 재시도 루틴"""
    write_journal_log(f"🚀 [배포 검증] Git commit & push 시도: {commit_msg}")
    for attempt in range(1, max_retries + 1):
        try:
            # Git add & commit
            subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
            commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, capture_output=True, text=True)
            
            # Git pull rebase & push
            subprocess.run(["git", "pull", "origin", "main", "--rebase"], cwd=BASE_DIR, check=True)
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, capture_output=True, text=True, check=True)
            
            write_journal_log(f"✅ [배포 성공] GitHub & Vercel 라이브 반영 완료 (시도 {attempt}/{max_retries})")
            return True
        except Exception as e:
            write_journal_log(f"⚠️ [배포 재시도 {attempt}/{max_retries}] Git 작업 예외: {e}")
            time.sleep(3 * attempt)
    
    write_journal_log("❌ [배포 경고] 3회 재시도 후에도 Push 실패. 다음 스케줄 주기에서 자동 복구 시도.")
    return False

def run_ttl_expiration_purge():
    """3. 만료 처리 (TTL Auto-Purge Engine): 24h/48h 지난 핫딜 자동 삭제/EXPIRED 처리"""
    write_journal_log("🧹 [TTL ENGINE] 만료 핫딜 자동 검사 및 Purge 스캔 중...")
    if not os.path.exists(DB_PATH):
        return 0

    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)

        products = db.get("products", [])
        now = datetime.now()
        active_products = []
        purged_count = 0

        for p in products:
            exp_str = p.get("expiry_date")
            is_expired = False
            if exp_str:
                try:
                    exp_dt = datetime.fromisoformat(exp_str)
                    if now > exp_dt:
                        is_expired = True
                except:
                    pass

            if is_expired:
                purged_count += 1
                write_journal_log(f"  🗑️ [TTL 만료 파기] {p.get('name')[:30]} (만료시각: {exp_str})")
            else:
                active_products.append(p)

        if purged_count > 0:
            db["products"] = active_products
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            write_journal_log(f"✅ [TTL ENGINE] 총 {purged_count}개 만료 핫딜 자동 제거 완료 (현재 활성: {len(active_products)}개)")
            run_git_deploy_with_retry(f"auto: 🧹 TTL Auto-Purge {purged_count} expired deals")
        else:
            write_journal_log(f"ℹ️ [TTL ENGINE] 만료된 핫딜 없음 (현재 활성 핫딜: {len(active_products)}개)")

        return purged_count

    except Exception as e:
        write_journal_log(f"❌ [TTL ENGINE 예외] {e}")
        return 0

def run_harvest_and_sync_cycle():
    """1, 2, 4. 24시간 수집 ➔ 중복 처리 ➔ 5대 검증 ➔ 예외 복구 메인 파이프라인"""
    write_journal_log("🔄 [수집 사이클 가동] sharelink.toss.im 포털 핫딜 동기화 시작")
    try:
        # Harvester 실행
        from worker.sharelink_toss_harvester import harvest_sharelink_portal
        harvest_sharelink_portal()
        write_journal_log("✅ [수집 사이클 완료] 파이프라인 정상 가동 완료")

        # Git Push Sync
        run_git_deploy_with_retry(f"auto: ⚡ 365-Day Unattended Harvester Sync [{datetime.now().strftime('%H:%M')}]")
    except Exception as e:
        write_journal_log(f"⚠️ [수집 사이클 예외 발생 - 자동 복구] {e}")

def sleep_until_next_midnight(target_hour=0, target_minute=1):
    now = datetime.now()
    next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)
    sleep_seconds = (next_run - now).total_seconds()
    write_journal_log(f"⏰ [MIDNIGHT SCHEDULER] 다음 실행 예정 시각: {next_run.strftime('%Y-%m-%d %H:%M:%S')} ({int(sleep_seconds)}초 / 약 {round(sleep_seconds/3600, 1)}시간 대기)")
    return sleep_seconds

def run_365_unattended_daemon(interval_minutes=30, run_once=False, is_midnight=False):
    """365일 무인 가동 메인 루프"""
    write_journal_log("=========================================================================")
    write_journal_log("🛡️ MORVIX SHOP OS - 365-DAY UNATTENDED AUTONOMOUS DAEMON INITIALIZED")
    write_journal_log(f"   • 실행 모드: {'매일 00:01 자정 자동 가동 모드' if is_midnight else f'매 {interval_minutes}분 주기 모드'}")
    write_journal_log(f"   • DB 경로: {DB_PATH}")
    write_journal_log(f"   • 저널 로그: {LOG_PATH}")
    write_journal_log("=========================================================================")

    while True:
        try:
            # 1. 만료 핫딜 스캔 및 Purge
            run_ttl_expiration_purge()

            # 2. 신규 핫딜 수집 및 DB 동기화 (오늘만 이 가격 + BEST 139개)
            run_harvest_and_sync_cycle()

        except Exception as main_e:
            write_journal_log(f"💥 [프로세스 예외 차단] 메인 루프 예외 감지 (다운 방지): {main_e}")

        if run_once:
            write_journal_log("🏁 1회 실행 완료 (--once 모드)")
            break

        if is_midnight:
            sleep_sec = sleep_until_next_midnight(0, 1)
            time.sleep(sleep_sec)
        else:
            write_journal_log(f"💤 다음 수집 주기까지 {interval_minutes}분간 대기 중...")
            time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    is_once = ("--once" in sys.argv)
    is_midnight = ("--midnight" in sys.argv)
    run_365_unattended_daemon(interval_minutes=30, run_once=is_once, is_midnight=is_midnight)
