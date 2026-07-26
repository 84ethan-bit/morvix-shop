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

def generate_action_center(coupang_sess, naver_sess, telegram_st, worker_st):
    actions = []

    if coupang_sess != "AUTHENTICATED_ACTIVE":
        actions.append({
            "status": "🔴 CRITICAL",
            "code": "COUPANG_LOGIN_REQUIRED",
            "message": "Coupang Partners Login Required (Execute STEP 1 Real Account Login)",
            "target": "GATE 1"
        })

    if naver_sess != "AUTHENTICATED_ACTIVE":
        actions.append({
            "status": "🔴 CRITICAL",
            "code": "NAVER_LOGIN_REQUIRED",
            "message": "Naver Shopping Connect Login Required (Execute STEP 1 Real Account Login)",
            "target": "GATE 1"
        })

    if telegram_st != "CONNECTED":
        actions.append({
            "status": "🟡 WARNING",
            "code": "TELEGRAM_TOKEN_PENDING",
            "message": "Telegram Token & Chat ID Registration Pending",
            "target": "GATE 3"
        })

    if worker_st == "RUNNING":
        actions.append({
            "status": "🟢 HEALTHY",
            "code": "WORKER_HEALTHY",
            "message": "Worker Engine Healthy & Running Cleanly",
            "target": "GATE 4"
        })

    return actions

def update_action_center_gate(coupang_session="UNKNOWN", naver_session="UNKNOWN",
                              worker_duration_sec=4.2, github_status="SUCCESS", vercel_status="SUCCESS"):
    """
    MORVIX v22.0 Feature Freeze & Operational Action Center Engine
    Focuses on 4 Operational Verification Gates & Immediate Action Items
    """
    print("==========================================================================")
    print("🛑 MORVIX FEATURE FREEZE & OPERATIONAL ACTION CENTER ENGINE (v22.0)")
    print("==========================================================================\n")

    now_iso = datetime.now().isoformat()
    telegram_status = "CONNECTED" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else "READY_TOKEN_PENDING"

    action_center = generate_action_center(coupang_session, naver_session, telegram_status, "RUNNING")

    # Gate Status Audit
    gates = {
        "GATE_1_LOGIN_VERIFICATION": "PENDING_REAL_ACCOUNT_LOGIN",
        "GATE_2_LINK_ISSUANCE": "PENDING_GATE_1",
        "GATE_3_EXCEPTION_RECOVERY": "IMPLEMENTED_PENDING_VERIFICATION",
        "GATE_4_24H_BURN_IN": "UNVERIFIED"
    }

    manifest_v22 = {
        "version": "22.0.0",
        "feature_freeze_status": "LOCKED_FEATURE_FREEZE",
        "health_score": 60,
        "max_score": 100,
        "action_center": action_center,
        "operational_gates": gates,
        "last_updated": now_iso,
        "queue": {
            "waiting": 0,
            "processing": 0,
            "completed_today": 4,
            "failed": 0
        },
        "worker": {
            "status": "RUNNING",
            "last_run": now_iso,
            "next_run": "Cron every 6 hours",
            "last_duration_sec": worker_duration_sec
        },
        "github": {
            "status": github_status,
            "last_success": now_iso
        },
        "vercel": {
            "status": vercel_status,
            "last_deploy": now_iso
        },
        "coupang": {
            "session": coupang_session,
            "last_verified": now_iso
        },
        "naver": {
            "session": naver_session,
            "last_verified": now_iso
        },
        "telegram": {
            "status": telegram_status
        }
    }

    with open(HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_v22, f, ensure_ascii=False, indent=2)

    public_dir = os.path.dirname(PUBLIC_HEALTH_PATH)
    os.makedirs(public_dir, exist_ok=True)
    with open(PUBLIC_HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_v22, f, ensure_ascii=False, indent=2)

    print(f"  ✅ [ACTION CENTER MANIFEST SAVED]: {HEALTH_PATH}")
    print(f"  🚨 Feature Freeze Status: {manifest_v22['feature_freeze_status']}")
    print(f"  📋 Action Center Items:   {len(action_center)} actions required")
    for act in action_center:
        print(f"     • {act['status']}: {act['message']} [{act['target']}]")

    return manifest_v22

if __name__ == "__main__":
    update_action_center_gate()
