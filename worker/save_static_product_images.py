import os
import sys
import requests

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR, exist_ok=True)

# High Quality Verified Product Images
STATIC_IMAGE_URLS = {
    "fan001.jpg": "https://images.unsplash.com/photo-1545259741-2ea3ebf61fa3?w=800&auto=format&fit=crop&q=80",
    "blanket001.jpg": "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=800&auto=format&fit=crop&q=80",
    "mosquito001.jpg": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=800&auto=format&fit=crop&q=80",
    "magsafe001.jpg": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&auto=format&fit=crop&q=80"
}

def save_static_images():
    print("=======================================================")
    print("📦 Saving Verified Static Assets to /images/ Folder...")
    print("=======================================================\n")

    for filename, url in STATIC_IMAGE_URLS.items():
        filepath = os.path.join(IMAGES_DIR, filename)
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and len(res.content) > 1000:
                with open(filepath, "wb") as f:
                    f.write(res.content)
                print(f"✅ Saved Static Asset: images/{filename} ({len(res.content)} bytes)")
            else:
                print(f"❌ Failed to fetch {filename}: Status {res.status_code}")
        except Exception as e:
            print(f"❌ Exception fetching {filename}: {e}")

if __name__ == "__main__":
    save_static_images()
