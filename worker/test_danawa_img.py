import requests
import re
import urllib.parse
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

def test_danawa_img():
    url = "https://search.danawa.com/dsearch.php?query=" + urllib.parse.quote("신일 서큘레이터")
    res = requests.get(url, headers=HEADERS, timeout=10)
    matches = re.findall(r'//img\.danawa\.com/prod_img/[^"\'\s>]+', res.text)
    print("Found Danawa Product Images:")
    for img in matches[:5]:
        full_url = "https:" + img if img.startswith("//") else img
        print("  •", full_url)

if __name__ == "__main__":
    test_danawa_img()
