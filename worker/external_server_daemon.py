"""
=============================================================================
MORVIX SHOP OS - 365-Day External Server Autonomous Daemon
worker/external_server_daemon.py

[역할]
 - 외부 서버가 부팅 후 이 파일 1개만 실행하면 365일 무인 자동 운영
 - 30분마다: 토스 수집 → DB 생성 → Git Push → Sleep
 - 장애 시: Telegram 즉시 알림
 - GitHub/Vercel: 절대 토스 접속 안 함 (Push 수신/배포만)

[실행법 - OS 무관]
 python worker/external_server_daemon.py
=============================================================================
"""
import subprocess, sys, os, time, json, datetime, traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "morvix_shop_db.json")
LOG_PATH = os.path.join(BASE_DIR, "scratch", "daemon_execution.log")
SLEEP_SECONDS = 30 * 60  # 30분 (테스트 시 60으로 변경)

# ─────────────────────────────────────────
# Telegram 알림 (장애 시에만)
# ─────────────────────────────────────────
def telegram_alert(msg):
    try:
        from morvix_telegram_notifier import notify_critical_alert
        notify_critical_alert(msg)
    except Exception as e:
        log(f"⚠️ Telegram 발송 실패: {e}")

# ─────────────────────────────────────────
# 로그
# ─────────────────────────────────────────
def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

# ─────────────────────────────────────────
# Step 1: 토스 수집
# ─────────────────────────────────────────
def run_harvest():
    log("🕐 [STEP 1] 토스 파트너 포털 수집 시작...")
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "worker", "sharelink_toss_harvester.py")],
        capture_output=True, text=True, cwd=BASE_DIR
    )
    if result.returncode != 0:
        raise Exception(f"수집기 오류:\n{result.stderr[-500:]}")
    log("✅ [STEP 1] 수집 완료")

# ─────────────────────────────────────────
# Step 2: DB 검증 (0개면 Push 안 함)
# ─────────────────────────────────────────
def verify_db():
    log("🔍 [STEP 2] DB 무결성 검증...")
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    count = len(db.get("products", []))
    if count == 0:
        raise Exception("수집 결과 0개 - Git Push 중단 (라이브 DB 보호)")
    log(f"✅ [STEP 2] DB 검증 완료 ({count}개 상품)")
    return count

# ─────────────────────────────────────────
# Step 3: Git Push
# ─────────────────────────────────────────
def git_push():
    log("📤 [STEP 3] GitHub Git Push 시작...")
    cmds = [
        ["git", "config", "user.name", "MORVIX External Server"],
        ["git", "config", "user.email", "server@morvix.io"],
        ["git", "add", "morvix_shop_db.json"],
    ]
    for cmd in cmds:
        subprocess.run(cmd, cwd=BASE_DIR, check=True)

    diff = subprocess.run(
        ["git", "diff", "--staged", "--quiet"],
        cwd=BASE_DIR
    )
    if diff.returncode == 0:
        log("ℹ️ [STEP 3] 변경사항 없음 - Push 생략")
        return

    subprocess.run(
        ["git", "commit", "-m", f"chore(external): Auto-ingest Toss deals @ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"],
        cwd=BASE_DIR, check=True
    )
    subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
    log("✅ [STEP 3] GitHub Push 완료 → Vercel 10초 자동 배포 시작")

# ─────────────────────────────────────────
# 메인 루프
# ─────────────────────────────────────────
def main_loop():
    log("=" * 60)
    log("🚀 MORVIX External Server Daemon 가동 (365일 무인 운영)")
    log("=" * 60)

    while True:
        try:
            log("─" * 40)
            run_harvest()
            count = verify_db()
            git_push()
            log(f"🎉 사이클 완료! ({count}개 상품 → Vercel 라이브 반영) | {SLEEP_SECONDS//60}분 후 재가동")
        except Exception as e:
            err_msg = f"🚨 [CRITICAL] 외부 서버 오류: {e}\n{traceback.format_exc()[-300:]}"
            log(err_msg)
            telegram_alert(err_msg)

        log(f"😴 Sleep {SLEEP_SECONDS//60}분...")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main_loop()
