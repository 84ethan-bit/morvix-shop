import requests
import json
import urllib.parse
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_naver_metadata_extraction(url):
    print("=======================================================")
    print("🧪 Testing Real Naver Link Metadata Extraction Engine")
    print(f"🔗 Target Naver URL: {url}")
    print("=======================================================\n")

    # Microlink Open Graph API endpoint
    api_url = f"https://api.microlink.io/?url={urllib.parse.quote(url)}"
    
    try:
        res = requests.get(api_url, timeout=10)
        print(f"  • Response Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json().get("data", {})
            title = data.get("title", "")
            image_obj = data.get("image", {})
            image_url = image_obj.get("url") if isinstance(image_obj, dict) else str(image_obj)
            
            # Extract price if present
            description = data.get("description", "")
            
            print(f"  ✅ [TITLE EXTRACTED]: {title}")
            print(f"  ✅ [REAL IMAGE EXTRACTED]: {image_url}")
            print(f"  ✅ [DESCRIPTION]: {description}")
            return {
                "title": title,
                "image": image_url,
                "description": description
            }
        else:
            print("  ❌ Failed to fetch via Microlink API")
            return None
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return None

if __name__ == "__main__":
    test_url = "https://smartstore.naver.com/shinil1959/products/1039971039"
    test_naver_metadata_extraction(test_url)
