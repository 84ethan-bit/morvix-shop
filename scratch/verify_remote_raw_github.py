import urllib.request
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REMOTE_RAW_URL = f"https://raw.githubusercontent.com/84ethan-bit/morvix-shop/main/morvix_shop_db.json?t={int(time.time())}"

def verify_github_remote():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🌐 [GitHub 원격 Server raw.githubusercontent.com 직접 조회 증명]")
    print(f"🔗 Target URL: {REMOTE_RAW_URL}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    req = urllib.request.Request(
        REMOTE_RAW_URL,
        headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            db = json.loads(content)

        tiedye = None
        alpha = None
        for p in db.get("products", []):
            if "타이다이" in p.get("name", ""):
                tiedye = p
            elif "알파시디" in p.get("name", ""):
                alpha = p

        print("📦 [1/2] GitHub Remote '타이다이 상하의 세트' Raw Dict:")
        print(json.dumps(tiedye, ensure_ascii=False, indent=2) if tiedye else "❌ 찾지 못함")

        print("\n📦 [2/2] GitHub Remote '순수스토리 알파시디' Raw Dict:")
        print(json.dumps(alpha, ensure_ascii=False, indent=2) if alpha else "❌ 찾지 못함")

        if tiedye and tiedye.get("price") == 18900:
            print("\n🎉 [최종 증명 성공] GitHub 원격 DB상 타이다이 price = 18900원 실측 확인 완료!")
        else:
            print(f"\n⚠️ 타이다이 가격: {tiedye.get('price') if tiedye else 'N/A'}")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    except Exception as e:
        print(f"❌ HTTP 요청 실패: {e}")

if __name__ == "__main__":
    verify_github_remote()
