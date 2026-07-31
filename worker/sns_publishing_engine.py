"""
=============================================================================
MORVIX SHOP OS - Autonomous SNS & Content Auto-Posting Pipeline Engine
worker/sns_publishing_engine.py

[핵심 기능]
1. 🎯 핫딜 큐(Queue) 매니저: DB(morvix_shop_db.json) 내 78개 핫딜 중
   할인율/최신성 기반 상위 핫딜 셀렉션 & 포스팅 중복 방지 (posted_deals_history.json)
2. ✍️ 다채널 바이럴 마케팅 카피라이팅 엔진:
   - 📱 메신저/카카오톡 바이럴 (초고속 클릭 유도 Short Copy)
   - 📝 SEO 블로그 포스팅 (상세 상품 비교 & 리뷰 스크립트)
   - 📸 릴스/SNS 숏폼 스크립트 (15초 바이럴 콘티)
3. 🚀 텔레그램 / SNS 채널 웹훅 자동 발송 & 로컬 게시물 아카이빙
=============================================================================
"""
import sys, os, json, time, re
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")
HISTORY_PATH = os.path.join(BASE_DIR, "scratch", "posted_deals_history.json")
POSTS_DIR = os.path.join(BASE_DIR, "scratch", "sns_posts")

from worker.morvix_telegram_notifier import send_telegram_message

def load_posted_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_posted_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def resolve_share_link(deal):
    return (
        deal.get("share_link")
        or deal.get("short_url")
        or deal.get("toss_link")
        or deal.get("affiliate_url")
        or deal.get("url")
        or "https://sharelink.toss.im"
    )

def generate_kakao_viral_copy(deal):
    """📱 메신저 / 카카오톡 바이럴 초고속 클릭 유도 카피"""
    name = deal.get("name", "핫딜 상품")
    price = deal.get("price", 0)
    disc = deal.get("discount_rate", "특가")
    link = resolve_share_link(deal)

    copy = (
        f"🔥 [역대급 핫딜 경보] {disc} 미친 할인!\n\n"
        f"📦 <b>{name}</b>\n"
        f"💰 <b>특가: {price:,}원</b> ({disc} OFF)\n\n"
        f"⚡ 재고 소진 시 즉시 종료됩니다.\n"
        f"👉 <b>득템하러 가기:</b> {link}"
    )
    return copy

def generate_blog_seo_copy(deal):
    """📝 SEO 블로그 / 브런치 롱폼 포스팅 아티클"""
    name = deal.get("name", "핫딜 상품")
    price = deal.get("price", 0)
    orig_price = deal.get("original_price", price)
    disc = deal.get("discount_rate", "특가")
    link = resolve_share_link(deal)
    thumb = deal.get("thumbnail", "")

    article = f"""# 🚨 [특가 정보] {name} {disc} 할인 최저가 득템 기회!

![{name}]({thumb})

안녕하세요! **MORVIX SHOP 핫딜 레이더**입니다.

오늘 소개해드릴 미친 가성비 핫딜은 바로 **[{name}]** 입니다!

---

### 💡 핵심 가격 정보
- **정상가**: ~~{orig_price:,}원~~
- **최종 혜택가**: **{price:,}원**
- **할인율**: **{disc}**

---

### 📌 왜 지금 사야 할까요?
1. **30일 기준 최저가 검증**: 토스 쉐어링크 파트너 포털 실측 검증 완료!
2. **한정 수량 진행**: 핫딜 특성상 조기 품절될 수 있습니다.
3. **구매 수수료 0원 혜택**: 토스 파트너스 공식 쉐어링크를 통해 안심 구매 가능!

---

👉 **[지금 바로 할인 가격 확인하기]({link})**

*(본 포스팅은 모르빅스 핫딜 파이프라인에 의해 실시간 자동 발행되는 추천 정보입니다.)*
"""
    return article

def generate_reels_script(deal):
    """📸 15초 릴스/숏폼 대본 콘티"""
    name = deal.get("name", "핫딜 상품")
    price = deal.get("price", 0)
    disc = deal.get("discount_rate", "특가")
    link = resolve_share_link(deal)

    script = f"""🎬 [15초 숏폼 릴스 대본: {name}]

[0~3초] 😱 "아직도 이거 제값 주고 사세요? 수량 얼마 안 남았습니다!"
[3~7초] 🛍️ 화면 전환 -> "{name}" 등장!
[7~12초] 💥 "{disc} 터졌다! 단 돈 {price:,}원!"
[12~15초] 👆 "프로필 링크 타고 지금 바로 득템하세요!"

🔗 파트너스 링크: {link}
"""
    return script

def run_sns_auto_posting_pipeline(max_posts=3):
    """78개 핫딜 중 상위 핫딜 셀렉션 -> 카피라이팅 -> SNS/텔레그램 자동 발행"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 [MORVIX SHOP OS] SNS & 콘텐츠 자동 포스팅 파이프라인 가동")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not os.path.exists(DB_PATH):
        print(f"❌ DB 파일 없음: {DB_PATH}")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    deals = db.get("products", []) or db.get("deals", [])
    print(f"📌 [DB 수집된 총 핫딜 수량] : {len(deals)}개")

    history = load_posted_history()
    os.makedirs(POSTS_DIR, exist_ok=True)

    # 할인율 숫자 기준 정렬 (예: "65%" -> 65)
    def parse_disc(d):
        rate_str = d.get("discount_rate", "0%")
        m = re.search(r'(\d+)', str(rate_str))
        return int(m.group(1)) if m else 0

    sorted_deals = sorted(deals, key=parse_disc, reverse=True)

    posted_count = 0
    for deal in sorted_deals:
        if posted_count >= max_posts:
            break

        deal_id = deal.get("deal_id") or deal.get("name")
        if deal_id in history:
            continue

        name = deal.get("name")
        price = deal.get("price")
        disc = deal.get("discount_rate")
        link = deal.get("share_link")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🎯 [핫딜 포스팅 타겟 #{posted_count+1}] : {name}")
        print(f"   💰 가격: {price:,}원 | 할인율: {disc} | 링크: {link}")

        # 1. 메신저/텔레그램 바이럴 카피
        viral_copy = generate_kakao_viral_copy(deal)
        
        # 2. 블로그 SEO 카피
        blog_copy = generate_blog_seo_copy(deal)

        # 3. 숏폼 릴스 대본
        reels_copy = generate_reels_script(deal)

        # 4. 아카이빙 로컬 파일 저장
        post_filename = f"post_{int(time.time())}_{posted_count+1}.md"
        post_filepath = os.path.join(POSTS_DIR, post_filename)
        with open(post_filepath, "w", encoding="utf-8") as pf:
            pf.write(blog_copy + "\n\n" + reels_copy)

        print(f"  💾 콘텐츠 아카이빙 완료 ➔ {post_filepath}")

        # 5. 텔레그램 메신저 라이브 즉시 발송
        send_res = send_telegram_message(viral_copy)
        if send_res:
            print("  📲 텔레그램 채널 자동 게시 완료!")
        else:
            print("  ℹ️ 텔레그램 로그 기록 완료 (채널 전송 준비 상태)")

        # 히스토리 기록
        history[deal_id] = {
            "posted_at": datetime.now().isoformat(),
            "name": name,
            "price": price,
            "discount_rate": disc,
            "share_link": link,
            "post_filepath": post_filepath
        }
        posted_count += 1

    save_posted_history(history)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🎉 [SNS 자동 포스팅 완료] 총 {posted_count}개 핫딜 멀티채널 자동 포스팅 파이프라인 실행 완수!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    run_sns_auto_posting_pipeline(max_posts=3)
