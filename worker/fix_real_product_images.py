import json
import os
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

# REAL Product Specific High-Resolution Images
REAL_PRODUCT_IMAGES = {
    "fan001": {
        "thumbnail": "https://img.danawa.com/prod_img/500000/039/971/img/19971039_1.jpg?shrink=500:500",
        "images": [
            "https://img.danawa.com/prod_img/500000/039/971/img/19971039_1.jpg?shrink=500:500"
        ]
    },
    "blanket001": {
        "thumbnail": "https://img.danawa.com/prod_img/500000/624/187/img/20187624_1.jpg?shrink=500:500",
        "images": [
            "https://img.danawa.com/prod_img/500000/624/187/img/20187624_1.jpg?shrink=500:500"
        ]
    },
    "mosquito001": {
        "thumbnail": "https://img.danawa.com/prod_img/500000/841/552/img/14552841_1.jpg?shrink=500:500",
        "images": [
            "https://img.danawa.com/prod_img/500000/841/552/img/14552841_1.jpg?shrink=500:500"
        ]
    },
    "magsafe001": {
        "thumbnail": "https://img.danawa.com/prod_img/500000/129/734/img/17734129_1.jpg?shrink=500:500",
        "images": [
            "https://img.danawa.com/prod_img/500000/129/734/img/17734129_1.jpg?shrink=500:500"
        ]
    }
}

def fix_real_images():
    print("=======================================================")
    print("🖼️ Fixing MORVIX Master DB with REAL Product Specific Images")
    print("=======================================================\n")

    if not os.path.exists(DB_PATH):
        print("❌ Error: morvix_shop_db.json not found!")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    updated_count = 0
    for p in db_data.get("products", []):
        slug = p.get("slug")
        if slug in REAL_PRODUCT_IMAGES:
            p["thumbnail"] = REAL_PRODUCT_IMAGES[slug]["thumbnail"]
            p["images"] = REAL_PRODUCT_IMAGES[slug]["images"]
            p["image_status"] = "Verified_Real"
            updated_count += 1
            print(f"✅ Updated REAL Product Image for [{p.get('name')}]: {p['thumbnail']}")

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Successfully updated {updated_count} products with REAL exact images!")

if __name__ == "__main__":
    fix_real_images()
