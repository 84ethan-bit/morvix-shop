import requests
import json
import urllib.parse
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_microlink_naver_shopping(query="신일 서큘레이터"):
    print("=======================================================")
    print("🧪 Testing Microlink Open Graph Extraction for Naver Shopping")
    print("=======================================================\n")

    naver_search_url = f"https://search.shopping.naver.com/search/all?query={urllib.parse.quote(query)}"
    microlink_url = f"https://api.microlink.io/?url={urllib.parse.quote(naver_search_url)}"

    res = requests.get(microlink_url, timeout=10)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        data = res.json().get("data", {})
        print("Data Keys:", list(data.keys()))
        print("Title:", data.get("title"))
        print("Image:", data.get("image"))
        print("Description:", data.get("description"))

if __name__ == "__main__":
    test_microlink_naver_shopping()
