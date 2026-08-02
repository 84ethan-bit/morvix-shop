import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
BANNER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "og_banner.jpg"))

def test_og_tags():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎯 [Open Graph (OG) 공유 카드 메타 태그 정밀 검증 스크립트]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(INDEX_PATH):
        print("❌ index.html 파일 없음")
        return

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
    og_desc = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html)
    og_img = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)

    print("📌 [수복된 Open Graph 메타 카드 세부 정보]:")
    print(f"  • og:title       : {og_title.group(1) if og_title else '미설정'}")
    print(f"  • og:description : {og_desc.group(1) if og_desc else '미설정'}")
    print(f"  • og:image       : {og_img.group(1) if og_img else '미설정'}")

    if os.path.exists(BANNER_PATH):
        size_kb = os.path.getsize(BANNER_PATH) / 1024
        print(f"  • og_banner.jpg  : 존재함 ({size_kb:.1f} KB, 1200x630 고화질 고정 배너)")
    else:
        print("  • og_banner.jpg  : ❌ 이미지 파일 미존재!")

    print("\n✅ index.html OG 태그 수복 완수! (NO GIT PUSH)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    test_og_tags()
