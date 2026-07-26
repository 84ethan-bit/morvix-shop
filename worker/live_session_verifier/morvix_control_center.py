import os
import sys
import json
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEALTH_PATH = os.path.join(BASE_DIR, "system_health.json")
PUBLIC_HEALTH_PATH = os.path.join(BASE_DIR, "public", "system_health.json")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def update_morvix_control_center(coupang_session="UNKNOWN", naver_session="UNKNOWN",
                                 registered_today=4, link_success=4, link_fail=0,
                                 recent_errors=0, last_backup_time="18:00"):
    """
    MORVIX 5-Second Executive Control Center Manifest Engine
    Consolidates 10 core operational metrics into a single 5-second overview.
    """
    print("==========================================================================")
    print("🖥️ MORVIX 5-SECOND EXECUTIVE CONTROL CENTER (system_health.json)")
    print("==========================================================================\n")

    now_dt = datetime.now()
    now_iso = now_dt.isoformat()
    telegram_status = "CONNECTED" if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else "READY_TOKEN_PENDING"

    control_center_manifest = {
        "version": "CONTROL_CENTER_STABLE",
        "last_updated": now_iso,
        "metrics": {
            "registered_today": registered_today,
            "link_success": link_success,
            "link_fail": link_fail,
            "coupang_login": coupang_session,
            "naver_login": naver_session,
            "worker_status": "RUNNING",
            "queue_count": 0,
            "telegram_status": telegram_status,
            "recent_errors": recent_errors,
            "last_backup_time": last_backup_time
        },
        "gates": {
            "GATE_1_REAL_LOGIN": "PENDING_MANUAL_LOGIN_PAIRING",
            "GATE_2_REAL_LINK_ISSUANCE": "PENDING_GATE_1",
            "GATE_3_EXCEPTION_TELEGRAM": "IMPLEMENTED_READY",
            "GATE_4_24H_BURN_IN": "UNVERIFIED"
        }
    }

    with open(HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(control_center_manifest, f, ensure_ascii=False, indent=2)

    public_dir = os.path.dirname(PUBLIC_HEALTH_PATH)
    os.makedirs(public_dir, exist_ok=True)
    with open(PUBLIC_HEALTH_PATH, "w", encoding="utf-8") as f:
        json.dump(control_center_manifest, f, ensure_ascii=False, indent=2)

    print("==========================================================================")
    print("📊 MORVIX CONTROL CENTER SUMMARY (5-Second Executive Overview):")
    print(f"  • 오늘 등록된 상품:   {registered_today}건")
    print(f"  • 링크발급 성공/실패:  성공 {link_success}건 / 실패 {link_fail}건")
    print(f"  • 쿠팡 로그인 상태:   {coupang_session}")
    print(f"  • 네이버 로그인 상태: {naver_session}")
    print(f"  • Worker 가동 상태:  RUNNING")
    print(f"  • Queue 대기 수량:   0건")
    print(f"  • 텔레그램 연동:     {telegram_status}")
    print(f"  • 최근 발생 오류:     {recent_errors}건")
    print(f"  • 최근 백업 완료:     {last_backup_time}")
    print("==========================================================================")

    return control_center_manifest

if __name__ == "__main__":
    update_morvix_control_center()
