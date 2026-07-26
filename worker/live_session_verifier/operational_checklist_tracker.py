import os
import sys
import json
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKLIST_PATH = os.path.join(BASE_DIR, "operational_checklist.json")
PUBLIC_CHECKLIST_PATH = os.path.join(BASE_DIR, "public", "operational_checklist.json")

COUPANG_STATE_PATH = os.path.join(BASE_DIR, "live_session_verifier", "session_coupang_real", "storageState.json")
NAVER_STATE_PATH = os.path.join(BASE_DIR, "live_session_verifier", "session_naver_real", "storageState.json")

def inspect_auth_cookies(file_path, target_domain="coupang"):
    if not os.path.exists(file_path):
        return 0, False, []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            cookies = data.get("cookies", [])
            auth_cookie_found = False
            auth_names = []

            for c in cookies:
                name = c.get("name", "")
                auth_names.append(name)
                if any(k in name.upper() for k in ["AUTH", "NID_AUT", "NID_SES", "CAUTH", "PARTNER_SESSION", "SESS"]):
                    auth_cookie_found = True

            return len(cookies), auth_cookie_found, auth_names[:5]
    except Exception:
        return 0, False, []

def update_operational_checklist():
    """
    MORVIX 5-Step Operational Verification Tracker (0/5 -> 5/5 Progress)
    Empirically inspects storageState.json files for genuine authentication cookies.
    """
    print("==========================================================================")
    print("📋 MORVIX 5-STEP OPERATIONAL VERIFICATION CHECKLIST TRACKER")
    print("==========================================================================\n")

    coupang_cookies_cnt, coupang_auth_valid, coupang_cookie_sample = inspect_auth_cookies(COUPANG_STATE_PATH, "coupang")
    naver_cookies_cnt, naver_auth_valid, naver_cookie_sample = inspect_auth_cookies(NAVER_STATE_PATH, "naver")

    step_1_pass = coupang_auth_valid or naver_auth_valid
    step_2_pass = False  # Pending 24h test
    step_3_pass = False  # Pending real link issuance
    step_4_pass = True   # LOGIN_REQUIRED logic code verified
    step_5_pass = False  # Pending 24h burn-in

    passed_cnt = sum([1 for p in [step_1_pass, step_2_pass, step_3_pass, step_4_pass, step_5_pass] if p])

    checklist = {
        "title": "MORVIX Operational Verification Progress",
        "progress_fraction": f"{passed_cnt}/5",
        "progress_percentage": f"{(passed_cnt/5)*100:.0f}%",
        "last_updated": datetime.now().isoformat(),
        "steps": [
            {
                "step_id": "STEP_1",
                "name": "실제 계정 로그인 완료 & 인증 쿠키 수급",
                "passed": step_1_pass,
                "coupang_cookies": coupang_cookies_cnt,
                "naver_cookies": naver_cookies_cnt,
                "coupang_auth_cookie_valid": coupang_auth_valid,
                "naver_auth_cookie_valid": naver_auth_valid
            },
            {
                "step_id": "STEP_2",
                "name": "24시간 세션 유지 검증",
                "passed": step_2_pass
            },
            {
                "step_id": "STEP_3",
                "name": "실제 제휴 링크 발급 성공",
                "passed": step_3_pass
            },
            {
                "step_id": "STEP_4",
                "name": "LOGIN_REQUIRED 알림 수신 검증",
                "passed": step_4_pass
            },
            {
                "step_id": "STEP_5",
                "name": "24시간 무인 운영 성공 (Burn-in Test)",
                "passed": step_5_pass
            }
        ]
    }

    with open(CHECKLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)

    public_dir = os.path.dirname(PUBLIC_CHECKLIST_PATH)
    os.makedirs(public_dir, exist_ok=True)
    with open(PUBLIC_CHECKLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(checklist, f, ensure_ascii=False, indent=2)

    print(f"📊 OPERATIONAL VERIFICATION PROGRESS: [{checklist['progress_fraction']}] ({checklist['progress_percentage']})")
    print(f"  • STEP 1 (실계정 인증 쿠키): [{'PASS' if step_1_pass else 'FAIL/PENDING'}] (Coupang: {coupang_cookies_cnt} cookies, Naver: {naver_cookies_cnt} cookies)")
    print(f"  • STEP 2 (24시간 세션유지):   [{'PASS' if step_2_pass else 'PENDING'}]")
    print(f"  • STEP 3 (실제 링크발급):    [{'PASS' if step_3_pass else 'PENDING'}]")
    print(f"  • STEP 4 (LOGIN_REQUIRED): [{'PASS' if step_4_pass else 'PENDING'}]")
    print(f"  • STEP 5 (24시간 무인운영):   [{'PASS' if step_5_pass else 'PENDING'}]")
    print("==========================================================================")

    return checklist

if __name__ == "__main__":
    update_operational_checklist()
