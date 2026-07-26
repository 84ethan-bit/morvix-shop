import os
import sys
import json
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from poc_naver_connect import run_naver_connect_poc
from poc_coupang_partners import run_coupang_partners_poc

def main():
    print("==========================================================================")
    print("🚀 MORVIX MASTER PROOF OF CONCEPT (PoC) PLAYWRIGHT LINK ISSUANCE SUITE")
    print(f"⏰ Execution Timestamp: {datetime.now().isoformat()}")
    print("==========================================================================\n")

    res_naver = run_naver_connect_poc("신일 서큘레이터 BLDC")
    print("\n--------------------------------------------------------------------------\n")
    res_coupang = run_coupang_partners_poc("신일 서큘레이터")

    suite_report = {
        "timestamp": datetime.now().isoformat(),
        "total_poc_tests": 2,
        "naver_connect_poc": res_naver,
        "coupang_partners_poc": res_coupang,
        "overall_poc_status": "SUCCESS" if (res_naver["status"] == "SUCCESS" and res_coupang["status"] == "SUCCESS") else "PARTIAL_SUCCESS"
    }

    report_path = os.path.join(os.path.dirname(__file__), "poc_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(suite_report, f, ensure_ascii=False, indent=2)

    print("\n==========================================================================")
    print("🏆 FINAL PoC VERIFICATION SUMMARY:")
    print(f"  • Naver Shopping Connect Link Issued: {res_naver['issued_affiliate_link']}")
    print(f"  • Coupang Partners Link Generated:   {res_coupang['issued_affiliate_link']}")
    print(f"  • Overall PoC Suite Status:           {suite_report['overall_poc_status']}")
    print(f"  • Result Log Saved To:               {report_path}")
    print("==========================================================================")

if __name__ == "__main__":
    main()
