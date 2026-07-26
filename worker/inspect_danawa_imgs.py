import requests
from bs4 import BeautifulSoup
import urllib.parse
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

def inspect_danawa_imgs():
    url = "https://search.danawa.com/dsearch.php?query=" + urllib.parse.quote("신일 서큘레이터")
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-original') or ""
        if "danawa" in src or "pstatic" in src:
            print("IMG SRC:", src)

if __name__ == "__main__":
    inspect_danawa_imgs()
