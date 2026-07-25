import json
import os
from datetime import datetime

LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sync_history.json")

def append_sync_log(status, processed_count, success_rate, log_msg, duration_str, error_details=None):
    logs = []
    if os.path.exists(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
            
    entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "count": processed_count,
        "success_rate": success_rate,
        "log": log_msg,
        "duration": duration_str,
        "error_details": error_details or []
    }
    
    logs.insert(0, entry)
    logs = logs[:100]  # Keep last 100 entries
    
    with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
        
    print(f"[LOGGER] Saved sync audit log entry. Total history entries: {len(logs)}")
    return entry

if __name__ == "__main__":
    append_sync_log("SUCCESS", 5, "100.0%", "Test Logger Initialized", "0.5s")
