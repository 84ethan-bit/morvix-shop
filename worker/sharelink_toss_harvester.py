import os
import sys
import time
import json
import subprocess
from datetime import datetime
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------
# 1. 경로 및 글로벌 설정
# ---------------------------------------------------------
# 실행 디렉토리 기준 절대 경로 확보 (Render 환경 경로 오류 방지)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "toss_products.json")

TARGET_URLS = {
    "TODAY_DEAL": "https://sharelink.toss.im/links/best-ranking/daily-deals?sectionCode=TODAY_DEAL",
    "BEST_SELLING": "https://sharelink.toss.im/links/best-ranking/promotion?sectionCode=BEST_SELLING"
}

MAX_SCROLL_COUNT = 40  # 대량 수집을 위한 깊은 스크롤

# ---------------------------------------------------------
# 2. 브라우저 스크롤 및 파싱 함수
# ---------------------------------------------------------
def scroll_to_bottom(page, max_scrolls=MAX_SCROLL_COUNT):
    """Render/클라우드 환경 대응 무한 스크롤"""
    print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] 전수 수집 무한 스크롤 시작 (최대 {max_scrolls}회)...")
    last_height = page.evaluate("document.body.scrollHeight")
    
    for i in range(max_scrolls):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        page.wait_for_timeout(1500)  # 동적 데이터 로딩 대기
        
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            # 리눅스 서버 지연 감안 2차 확인
            page.wait_for_timeout(2000)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                print(f"✅ 스크롤 완료 ({i+1}회 수행 후 바닥 도달)")
                break
        last_height = new_height
        if (i + 1) % 10 == 0:
            print(f"   - {i+1}번째 스크롤 다운 중...")

def parse_products(page, category_code):
    """할인율 미표기 특가(30일 최저가/역대급특가) 포함 전수 파싱"""
    extracted_data = page.evaluate("""
        (category) => {
            const results = [];
            // 토스 쉐어링크 카드 엘리먼트 타겟팅
            const cards = document.querySelectorAll('a[href*="/links/"], div[class*="Card"], li');
            
            cards.forEach((card, idx) => {
                const text = card.innerText || "";
                if (!text.includes('원') && !text.includes('%')) return;
                
                const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                
                let title = "";
                let price = "";
                let originalPrice = "";
                let discountRate = "";
                let badge = "";

                lines.forEach(line => {
                    if (line.includes('%')) {
                        discountRate = line;
                    } else if (line.includes('원')) {
                        if (!price) price = line;
                        else originalPrice = line;
                    } else if (line.includes('최저가') || line.includes('특가') || line.includes('오늘만')) {
                        badge = line;
                    } else if (line.length > 5 && !title) {
                        title = line;
                    }
                });

                const link = card.href || card.querySelector('a')?.href || "";

                if (title && price) {
                    results.push({
                        id: `${category}_${idx}_${Date.now()}`,
                        category: category,
                        title: title,
                        price: price,
                        originalPrice: originalPrice || price,
                        discountRate: discountRate || badge || "특가",
                        link: link,
                        crawledAt: new Date().toISOString()
                    });
                }
            });
            
            // 중복 상품 제거 (타이틀 기준)
            const uniqueResults = [];
            const seenTitles = new Set();
            for (const item of results) {
                if (!seenTitles.has(item.title)) {
                    seenTitles.add(item.title);
                    uniqueResults.push(item);
                }
            }
            return uniqueResults;
        }
    """, category_code)

    return extracted_data

# ---------------------------------------------------------
# 3. 메인 수집 엔진 (Render 스텔스 우회 적용)
# ---------------------------------------------------------
def run_harvester():
    print(f"\n🚀 [Morvix Engine] 수집 프로세스 가동: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    all_products = []

    with sync_playwright() as p:
        # Render/Linux 헤드리스 차단 방지 옵션 적용
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        # 봇 감지 스크립트 무력화
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for category, url in TARGET_URLS.items():
            print(f"\n🌐 [{category}] 직통 URL 접속: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)

            scroll_to_bottom(page, max_scrolls=MAX_SCROLL_COUNT)
            products = parse_products(page, category)
            
            print(f"✅ [{category}] 수집 완료: {len(products)}개 확보")
            all_products.extend(products)

        browser.close()

    # JSON 저장
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\n🏆 총 {len(all_products)}개 상품 파싱 완결 ➔ 저장 위치: {OUTPUT_FILE}")
    return len(all_products)

# ---------------------------------------------------------
# 4. GitHub Auto Push 엔진 (Render ➔ GitHub ➔ Vercel)
# ---------------------------------------------------------
def git_auto_push():
    """Render 환경에서 GH_TOKEN 기반 원격 인증 Push 처리"""
    gh_token = os.getenv("GH_TOKEN")
    if not gh_token:
        print("\nℹ️ [GH_TOKEN 미설정] 로컬 테스트 모드로 Git Push를 스킵합니다.")
        return

    print("\n🚀 [AUTO GIT PUSH ENGINE] Render ➔ GitHub 동기화 시도...")
    try:
        # Git 사용자 기본 정보 설정
        subprocess.run(["git", "config", "user.name", "Morvix Render Bot"], check=True)
        subprocess.run(["git", "config", "user.email", "bot@morvix.com"], check=True)
        
        # 데이터 파일 스테이징
        subprocess.run(["git", "add", OUTPUT_FILE], check=True)
        
        commit_msg = f"chore(data): auto update toss products [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        
        # 커밋할 변경사항이 있는지 확인
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            print("ℹ️ 변경된 상품 데이터가 없어 Push를 스킵합니다.")
            return

        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        # Remote 저장소 URL 가져오기 및 인증 토큰 주입
        remote_url_cmd = subprocess.run(["git", "config", "--get", "remote.origin.url"], capture_output=True, text=True, check=True)
        raw_url = remote_url_cmd.stdout.strip()
        
        # https://github.com/org/repo.git 형태를 https://x-access-token:TOKEN@github.com/org/repo.git 로 변환
        if "github.com" in raw_url:
            clean_repo = raw_url.split("github.com/")[-1]
            auth_repo_url = f"https://x-access-token:{gh_token}@github.com/{clean_repo}"
            
            # HEAD:main 또는 HEAD:master로 강제 푸시
            push_res = subprocess.run(["git", "push", auth_repo_url, "HEAD:main"], capture_output=True, text=True)
            if push_res.returncode != 0:
                # main 브랜치가 아닐 경우 master 시도
                push_res = subprocess.run(["git", "push", auth_repo_url, "HEAD:master"], capture_output=True, text=True)
                
            if push_res.returncode == 0:
                print("🎉 [Git Push 성공] GitHub 저장소에 업데이트 완료! Vercel 자동 재배포가 시작됩니다.")
            else:
                print(f"❌ [Git Push 실패] 원인: {push_res.stderr}")
        else:
            print("⚠️ 원격 저장소 URL 형식을 확인해 주세요.")

    except Exception as e:
        print(f"❌ [Git Automation Error] {e}")

# ---------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------
if __name__ == "__main__":
    count = run_harvester()
    if count > 0:
        git_auto_push()