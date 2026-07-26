import json
import os
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

LOCAL_IMAGE_MAP = {
    "fan001": "images/fan001.jpg",
    "blanket001": "images/blanket001.jpg",
    "mosquito001": "images/mosquito001.jpg",
    "magsafe001": "images/magsafe001.jpg"
}

def update_db_images():
    print("=======================================================")
    print("🔄 Updating Master DB with Local Static Asset Paths...")
    print("=======================================================\n")

    if not os.path.exists(DB_PATH):
        print("❌ Error: morvix_shop_db.json not found!")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    for p in db_data.get("products", []):
        slug = p.get("slug")
        if slug in LOCAL_IMAGE_MAP:
            local_path = LOCAL_IMAGE_MAP[slug]
            p["thumbnail"] = local_path
            p["images"] = [local_path]
            p["image_status"] = "Verified_Local"
            print(f"✅ Updated Master DB Image for [{p.get('name')}]: {local_path}")

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    print("\n🎉 Master DB updated with guaranteed local static assets!")

if __name__ == "__main__":
    update_db_images()
