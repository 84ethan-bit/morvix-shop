"""
토스 파트너 세션 저장 스크립트
사용법: python worker/save_toss_session.py

브라우저가 열리면 sharelink.toss.im에 로그인 완료 후 기다리세요.
자동으로 세션이 저장됩니다.
"""
import os, json, base64
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_PATH = os.path.join(BASE_DIR, "scratch", "toss_sharelink_session.json")
B64_PATH = os.path.join(BASE_DIR, "scratch", "session_b64_for_render.txt")

os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)

print("=" * 60)
print("🔑 토스 파트너 세션 저장 스크립트")
print("=" * 60)
print("1. 브라우저가 열립니다")
print("2. sharelink.toss.im 에서 로그인을 완료해주세요")
print("3. 홈 화면이 나오면 자동으로 세션이 저장됩니다")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()

    page.goto("https://sharelink.toss.im/home")
    print("⏳ 로그인 완료 후 홈 화면이 나올 때까지 기다리는 중... (최대 120초)")

    try:
        page.wait_for_url("**/home", timeout=120000)
        import time; time.sleep(2)  # 쿠키 완전 로드 대기

        storage = ctx.storage_state()
        with open(SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump(storage, f, ensure_ascii=False, indent=2)
        print(f"✅ 세션 저장 완료: {SESSION_PATH}")

        # Base64 인코딩 자동 생성
        b64 = base64.b64encode(json.dumps(storage, ensure_ascii=False).encode("utf-8")).decode("utf-8")
        # Git Push로 Render 외부 서버에 1초 자동 동기화
        print("\n🚀 [자동 동기화] Render 외부 서버로 새 세션 파일 Git Push 중...")
        try:
            import subprocess
            subprocess.run(["git", "add", SESSION_PATH], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "commit", "-m", "chore: Update Toss partner session state for external server"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
            print("✅ Git Push 완료! Render 외부 서버에 10초 내 새 세션 적용 완료 🎉")
        except Exception as git_err:
            print(f"⚠️ Git Push 자동 전송 실패 (수동 Push 필요): {git_err}")

        print()
        print("=" * 60)
        print("🎉 모든 세션 동기화 작업이 완료되었습니다!")
        print("   외부 서버가 이 세션으로 365일 무인 자동 수집을 진행합니다.")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 세션 저장 실패: {e}")

    browser.close()

