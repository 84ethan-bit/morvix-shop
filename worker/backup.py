import json
import os
import shutil
import sys
from datetime import datetime

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

def create_db_snapshot():
    """Create timestamped automated backup snapshot of Master DB"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Backup Error: Source Master DB missing at {DB_PATH}")
        return False

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_filename = f"morvix_master_db_snapshot_{timestamp}.json"
    snapshot_path = os.path.join(BACKUP_DIR, snapshot_filename)

    shutil.copy2(DB_PATH, snapshot_path)
    print(f"📦 [BACKUP] Created Master DB Snapshot: backups/{snapshot_filename}")

    # Keep latest 30 snapshots
    snapshots = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("morvix_master_db_snapshot_")])
    if len(snapshots) > 30:
        for old in snapshots[:-30]:
            os.remove(os.path.join(BACKUP_DIR, old))
            print(f"🧹 [PRUNE] Rotated out old snapshot: {old}")

    return snapshot_path

def restore_latest_snapshot():
    """Restore Master DB from the most recent backup snapshot"""
    if not os.path.exists(BACKUP_DIR):
        print("❌ Restore Error: Backup directory missing.")
        return False

    snapshots = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("morvix_master_db_snapshot_")])
    if not snapshots:
        print("❌ Restore Error: No backup snapshots found.")
        return False

    latest = snapshots[-1]
    latest_path = os.path.join(BACKUP_DIR, latest)

    shutil.copy2(latest_path, DB_PATH)
    print(f"🔄 [RESTORE] Master DB successfully restored from backups/{latest}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_latest_snapshot()
    else:
        create_db_snapshot()
