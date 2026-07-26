import json
import os
import sys
import time
import requests
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from logger import append_sync_log
from affiliate_worker import process_product_affiliates
from publishing_worker import generate_publishing_assets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9"
}

def send_telegram_notification(message):
    """Operator Notification Channel (Decoupled Alert Bot)"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[TELEGRAM] Notification skipped (Token/ChatID not set in ENV).")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM] Notification send error: {e}")
        return False

def run_worker_sync():
    start_time = time.time()
    print("[LOG] [MORVIX Phase 2 Worker] Starting Master DB Synchronization...")

    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Master DB path not found: {DB_PATH}")
        append_sync_log("FAIL", 0, "0.0%", "Master DB File Not Found", "0.0s", ["DB File Missing"])
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    products = db_data.get("products", [])
    total_count = len(products)
    success_count = 0
    fail_count = 0
    error_logs = []

    print(f"[LOG] Total Master Products to Sync: {total_count}")

    for idx, p in enumerate(products, 1):
        slug = p.get("slug", "unknown")
        name = p.get("name", "Unnamed")
        print(f"\n[LOG] [{idx}/{total_count}] Checking Product: {name} (morvix.kr/{slug})")

        # 1. Status & Price History Audit
        if not p.get("status"):
            p["status"] = "ACTIVE"

        current_price = p.get("price")
        history = p.get("price_history", [])
        if not history and current_price:
            history = [{"price": current_price, "date": datetime.now().isoformat()}]
            p["price_history"] = history

        # 2. Affiliate Link Health Verification
        links = p.get("affiliate_links", [])
        prod_success = True

        for link_item in links:
            url = link_item.get("url", "")
            platform = link_item.get("platform", "naver")
            
            try:
                res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
                status_code = res.status_code
                print(f"  • Link Check [{platform}]: Status {status_code} ({url[:40]}...)")
                
                if status_code in [200, 301, 302]:
                    pass
                elif status_code in [403, 418]:
                    error_logs.append(f"{slug} [{platform}]: Status {status_code} (Anti-bot Shield)")
                    print(f"  [WARN] {platform} returned Status {status_code} Anti-bot Shield")
                elif status_code == 404:
                    prod_success = False
                    p["status"] = "OUT_OF_STOCK"
                    error_logs.append(f"{slug} [{platform}]: 404 Not Found (Auto set OUT_OF_STOCK)")
                    print(f"  [ERROR] 404 Error: Marked product OUT_OF_STOCK")
            except Exception as e:
                print(f"  [WARN] Exception checking [{platform}]: {e}")
                error_logs.append(f"{slug} [{platform}]: {str(e)[:60]}")

        # 3. Sub-Worker Processing: Affiliate & Publishing Assets
        p = process_product_affiliates(p)
        p = generate_publishing_assets(p)

        # 4. Master Version Increment & Image Status Audit
        if prod_success:
            success_count += 1
        else:
            fail_count += 1

        p["version"] = p.get("version", 1) + 1
        p["last_synced_at"] = datetime.now().isoformat()
        if not p.get("image_status"):
            p["image_status"] = "Verified" if p.get("thumbnail") else "Missing"

    # Save Updated Master DB
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    duration = f"{time.time() - start_time:.1f}초"
    success_rate_pct = f"{((success_count / total_count) * 100):.1f}%" if total_count > 0 else "100.0%"
    
    process_status = "PROCESS_SUCCESS"
    harvest_status = "SCRAPE_BLOCKED (403/418 Shield)" if len(error_logs) > 0 else "HARVEST_SUCCESS"

    log_summary = f"[Process: {process_status} | Harvest: {harvest_status}] Master DB {total_count}개 상품 동기화 스캔 완료"
    
    entry = append_sync_log(
        status="SUCCESS" if len(error_logs) == 0 else "PARTIAL_SHIELD",
        processed_count=total_count,
        success_rate=success_rate_pct,
        log_msg=log_summary,
        duration_str=duration,
        error_details=error_logs
    )

    # 3. Send Decoupled Telegram Operator Notification
    tele_msg = f"🤖 *[MORVIX OS Worker Sync Alert]*\n\n• *Process:* `{process_status}`\n• *Harvest:* `{harvest_status}`\n• *Products Synced:* `{total_count}개`\n• *Success Rate:* `{success_rate_pct}`\n• *Duration:* `{duration}`\n• *Timestamp:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
    send_telegram_notification(tele_msg)

    print("\n=======================================================")
    print("WORKER EXECUTION COMPLETED EMPIRICALLY:")
    print(f"• Process Status: {process_status}")
    print(f"• Harvest Status: {harvest_status}")
    print(f"• Processed Products: {total_count}")
    print(f"• Success Rate: {success_rate_pct}")
    print(f"• Duration: {duration}")
    print(f"• Error Logs Captured: {len(error_logs)}")
    print("=======================================================")

if __name__ == "__main__":
    run_worker_sync()
