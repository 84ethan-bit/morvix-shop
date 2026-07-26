import os
import sys
import subprocess
import json
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from logger import append_sync_log

def run_daily_health_check():
    print("=======================================================")
    print("🩺 Starting MORVIX OS Automated Daily Self-Health Check...")
    print("=======================================================\n")

    results = {}

    # Step 1: Automated Backup Snapshot & Integrity Verification
    print("📦 [STEP 1] Creating & Verifying Master DB Snapshot...")
    b_res = subprocess.run(["python", os.path.join(BASE_DIR, "worker", "backup.py"), "verify"], capture_output=True, encoding="utf-8", errors="ignore")
    results["backup_verify"] = b_res.returncode == 0 and "BACKUP VERIFY: PASS" in (b_res.stdout or "")
    print(f"   • Result: {'✅ PASS' if results['backup_verify'] else '❌ FAIL'}")

    # Step 2: Disaster Recovery Simulation Test
    print("\n🚨 [STEP 2] Running Instant Disaster Recovery (DR) Simulation...")
    dr_res = subprocess.run(["python", os.path.join(BASE_DIR, "worker", "backup.py"), "dr"], capture_output=True, encoding="utf-8", errors="ignore")
    results["disaster_recovery"] = dr_res.returncode == 0 and "100% PASSED" in (dr_res.stdout or "")
    print(f"   • Result: {'✅ PASS' if results['disaster_recovery'] else '❌ FAIL'}")

    # Step 3: Background Worker Ingestion Sync Execution
    print("\n⚡ [STEP 3] Running Worker Ingestion Sync...")
    w_res = subprocess.run(["python", os.path.join(BASE_DIR, "worker", "sync.py")], capture_output=True, encoding="utf-8", errors="ignore")
    results["worker_sync"] = w_res.returncode == 0 and "COMPLETED EMPIRICALLY" in (w_res.stdout or "")
    print(f"   • Result: {'✅ PASS' if results['worker_sync'] else '❌ FAIL'}")

    # Step 4: E2E Automated System Test Suite
    print("\n🧪 [STEP 4] Executing 14-Point E2E Automated Test Suite...")
    e2e_res = subprocess.run(["node", os.path.join(BASE_DIR, "test_e2e.js")], capture_output=True, encoding="utf-8", errors="ignore")
    results["e2e_tests"] = e2e_res.returncode == 0 and "ALL TESTS PASSED" in (e2e_res.stdout or "")
    print(f"   • Result: {'✅ PASS' if results['e2e_tests'] else '❌ FAIL'}")

    all_passed = all(results.values())

    print("\n=======================================================")
    print(f"🩺 DAILY SELF-HEALTH CHECK RESULT: {'🟢 100% HEALTHY' if all_passed else '🔴 HEALTH CHECK FAILURE DETECTED'}")
    print(f"• Backup & Integrity: {'✅ PASS' if results['backup_verify'] else '❌ FAIL'}")
    print(f"• Disaster Recovery:  {'✅ PASS' if results['disaster_recovery'] else '❌ FAIL'}")
    print(f"• Worker Sync:        {'✅ PASS' if results['worker_sync'] else '❌ FAIL'}")
    print(f"• E2E System Suite:   {'✅ PASS' if results['e2e_tests'] else '❌ FAIL'}")
    print("=======================================================")

    return all_passed

if __name__ == "__main__":
    run_daily_health_check()
