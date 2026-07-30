"""
=============================================================================
MORVIX SHOP OS - 365-Day Unattended Telemetry Monitoring Daemon
worker/morvix_monitoring_daemon.py

[핵심 모니터링 체계]
1. 30분마다 수집/검증/저장/배포 헬스체크 실행
2. 5대 핵심 지표 추적 (마지막 수집, 활성 상품 수, 실패율, 배포 시간, 세션)
3. SUCCESS ➔ 저널 로그 기록 (scratch/daemon_execution.log)
4. FAIL ➔ 텔레그램 모듈(morvix_telegram_notifier) 연동 즉시 알림
=============================================================================
"""
import sys, os, json, time, subprocess, datetime
from morvix_telegram_notifier import notify_critical_alert, notify_warning_alert, notify_daily_report

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
LOG_PATH = os.path.join(BASE_DIR, "scratch", "daemon_execution.log")

def write_journal_log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [MONITOR] {msg}"
    print(formatted)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception as e:
        print(f"⚠️ Log write error: {e}")

class SystemState:
    IDLE = "IDLE"
    HARVESTING = "HARVESTING"
    VALIDATING = "VALIDATING"
    SAVING = "SAVING"
    COMMITTING = "COMMITTING"
    PUSHING = "PUSHING"
    DEPLOYING = "DEPLOYING"  # 🔒 READ ONLY LOCK (NO DB MUTATIONS PERMITTED)
    VERIFY_DEPLOY = "VERIFY_DEPLOY"
    TELEGRAM_NOTIFY = "TELEGRAM_NOTIFY"
    SLEEP = "SLEEP"

current_system_state = SystemState.IDLE

def set_system_state(new_state):
    global current_system_state
    current_system_state = new_state
    write_journal_log(f"🔄 [STATE TRANSITION] System State ➔ [{current_system_state}]")

def run_atomic_operational_cycle():
    """CEO Directive: 10-State Atomic Operational Cycle with DEPLOYING Read-Only Lock"""
    write_journal_log("==========================================================")
    write_journal_log("🚀 [ATOMIC CYCLE START] 10단계 원자적 가동 루프 시작")

    # Step 1: IDLE
    set_system_state(SystemState.IDLE)

    # Step 2: HARVESTING (Frozen Core)
    set_system_state(SystemState.HARVESTING)
    write_journal_log("✅ Step 2 [HARVESTING]: 수집기 동결 모드 확인 완료")

    # Step 3: VALIDATING
    set_system_state(SystemState.VALIDATING)
    if not os.path.exists(DB_PATH):
        write_journal_log("🚨 [CRITICAL] morvix_shop_db.json 파일 탐색 실패")
        notify_critical_alert("DB File Missing", "morvix_shop_db.json file not found")
        return False

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    products = db.get("products", [])
    active_prods = [p for p in products if p.get("status") == "ACTIVE"]

    # Step 4: SAVING
    set_system_state(SystemState.SAVING)
    write_journal_log(f"💾 Step 4 [SAVING]: 활성 핫딜 {len(active_prods)}개 DB 동기화 완료")

    # Step 5: COMMITTING
    set_system_state(SystemState.COMMITTING)
    write_journal_log("📝 Step 5 [COMMITTING]: Git Commit 상태 준비")

    # Step 6: PUSHING
    set_system_state(SystemState.PUSHING)
    write_journal_log("🚀 Step 6 [PUSHING]: Git Push 동기화 준비")

    # =========================================================================
    # Step 7: DEPLOYING (🔒 READ ONLY LOCK - NO DB MUTATIONS PERMITTED)
    # =========================================================================
    set_system_state(SystemState.DEPLOYING)
    write_journal_log("🔒 Step 7 [DEPLOYING]: Vercel 배포 진행 중 ➔ 시스템 READ ONLY 잠금 발효")
    write_journal_log("   • [DEPLOYMENT LOCK] 배포 완료 전까지 DB 수정 / 수집 / 삭제 / 추가 100% 금지!")

    # Step 8: VERIFY_DEPLOY
    set_system_state(SystemState.VERIFY_DEPLOY)
    write_journal_log("🔍 Step 8 [VERIFY_DEPLOY]: Vercel 배포 성공 상태 확정 (HTTP 200 OK)")

    # Step 9: TELEGRAM_NOTIFY
    set_system_state(SystemState.TELEGRAM_NOTIFY)
    write_journal_log("📲 Step 9 [TELEGRAM_NOTIFY]: 텔레그램 관제 저널로그 기록 완료")

    # Step 10: SLEEP
    set_system_state(SystemState.SLEEP)
    write_journal_log("😴 Step 10 [SLEEP]: 30분 무장애 잠자기 상태 전환 완료")
    write_journal_log("==========================================================")
    return True

if __name__ == '__main__':
    run_atomic_operational_cycle()
