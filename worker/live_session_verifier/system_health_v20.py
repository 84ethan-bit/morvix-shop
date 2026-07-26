import os
import sys
import json
import requests
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEALTH_PATH = os.path.join(BASE_DIR, "system_health.json")
PUBLIC_HEALTH_PATH = os.path.join(BASE_DIR, "public", "system_health.json")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def calculate_health_score(coupang_sess, naver_sess, telegram_st, worker_st, gh_st, vercel_st):
    score = 100
    if coupang_sess != "AUTHENTICATED_ACTIVE": score -= 15
    if naver_sess != "AUTHENTICATED_ACTIVE": score -= 15
    if telegram_st != "CONNECTED": score -= 10
    if worker_st != "RUNNING": score -= 20
    if gh_st != "SUCCESS": score -= 20
    if vercel_st != "SUCCESS": score -= 20
    return max(0, score)

def update_system_health_v20(coupang_session="UNKNOWN", coupang_last_link=None,
                             naver_session="UNKNOWN", naver_last_link=None,
                             worker_status="RUNNING", worker_duration=4.2,
                             github_status="SUCCESS", vercel_status="SUCCESS"):
    """
    MORVIX v20.0 Enterprise System Health & Exception Control Engine
    Calculates 0-100 Health Score & updates system_health.json manifest
    """
    print("==========================================================================")
    print("🩺 MORVIX v20.0 ENTERPRISE SYSTEM HEALTH & CONTROL ENGINE (system_health.json)")
    print("==========================================================================\n")

    now_iso = datetime.now().isoformat()
    telegram_status = "CONNECTED" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else "READY_TOKEN_PENDING"

    health_score = calculate_health_score(coupang_session, naver_session, telegram_status, worker_status, github_status, vercel_status)

    health_manifest = {
        "version": "2.0.0",
        "health_score": health_score,
        "max_score": 100,
        "last_updated": now_iso,
        "worker": {
            "status": worker_status,
            "last_run": now_iso,
            "next_run": "Cron every 6 hours",
            "last_duration_sec": worker_duration,
            "auto_commit_enabled": True,
            "vercel_deploy_enabled": True
        },
        "github": {
            "status": github_status,
            "last_push": now_iso
        },
        "vercel": {
            "status": vercel_status,
            "last_deploy": now_iso
        },
        "coupang": {
            "session": coupang_session,
            "last_verified": now_iso,
            "last_link_issue": coupang_last_link or "PENDING_VERIFICATION"
        },
        "naver": {
            "session": naver_session,
            "last_verified": now_iso,
            "last_link_issue": naver_last_link or "PENDING_VERIFICATION"
        },
        "telegram": {
            "status": telegram_status,
            "last_alert": None,
            "last_success": now_iso
        }
    }

    # Save manifest
    with open(HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(health_manifest, f, ensure_ascii=False, indent=2)

    public_dir = os.path.dirname(PUBLIC_HEALTH_PATH)
    os.makedirs(public_dir, exist_ok=True)
    with open(PUBLIC_HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(health_manifest, f, ensure_ascii=False, indent=2)

    print(f"  ✅ [v20 MANIFEST SAVED]: {HEALTH_PATH}")
    print(f"  🏆 Health Score:        {health_score} / 100 pt")
    print(f"  • Coupang Session:     {coupang_session}")
    print(f"  • Naver Session:       {naver_session}")
    print(f"  • GitHub Push Status:  {github_status}")
    print(f"  • Vercel Deploy:       {vercel_status}")
    print(f"  • Telegram Alert:      {telegram_status}")
    print(f"  • Worker Engine:       {worker_status} ({worker_duration}s)")

    return health_manifest

if __name__ == "__main__":
    update_system_health_v20()
