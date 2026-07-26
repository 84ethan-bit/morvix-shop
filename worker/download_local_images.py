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

IMAGE_SOURCES = {
    "fan001.jpg": "https://img.danawa.com/prod_img/500000/039/971/img/19971039_1.jpg?shrink=500:500",
    "blanket001.jpg": "https://img.danawa.com/prod_img/500000/624/187/img/20187624_1.jpg?shrink=500:500",
    "mosquito001.jpg": "https://img.danawa.com/prod_img/500000/841/552/img/14552841_1.jpg?shrink=500:500",
    "magsafe001.jpg": "https://img.danawa.com/prod_img/500000/129/734/img/17734129_1.jpg?shrink=500:500"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.danawa.com/"
}

def download_images():
    print("=======================================================")
    print("📥 Downloading Real Product Images to Local Assets (images/)...")
    print("=======================================================\n")

    for filename, url in IMAGE_SOURCES.items():
        save_path = os.path.join(IMAGES_DIR, filename)
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200 and len(res.content) > 1000:
                with open(save_path, "wb") as f:
                    f.write(res.content)
                print(f"✅ Saved Local Asset: images/{filename} ({len(res.content)} bytes)")
            else:
                print(f"⚠️ Failed to download {filename}: HTTP {res.status_code}")
        except Exception as e:
            print(f"❌ Exception downloading {filename}: {e}")

if __name__ == "__main__":
    download_images()
