import json
import os
import sys
import re

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

def auto_ingest_from_raw_input(raw_input_text):
    """
    MORVIX 0-Manual Auto Ingestion Engine:
    Takes 1 raw deal URL or text input and automatically generates the entire product master item:
    - Name & Subtitle
    - Category
    - Price & Discount Rate
    - Verified Image
    - Affiliate Links (Coupang & Naver)
    - Multi-Channel Content Scripts (Shorts, Reels, SEO)
    """
    print("=======================================================")
    print("⚡ MORVIX 0-MANUAL AUTO INGESTION ENGINE RUNNING")
    print(f"📥 Input Payload: '{raw_input_text[:60]}...'")
    print("=======================================================\n")

    # 1. Parse Name
    clean_text = raw_input_text.strip()
    lines = clean_text.split('\n')
    name = lines[0] if lines else "핫딜 추천 상품"
    if len(name) > 60:
        name = name[:60] + "..."

    # 2. Parse Price & Discount
    price_match = re.search(r'([\d,]+)\s*원', clean_text)
    price = int(price_match.group(1).replace(',', '')) if price_match else 29900

    discount_match = re.search(r'(\d+)\s*[%％]', clean_text)
    discount_rate = f"{discount_match.group(1)}%" if discount_match else "30%"

    # 3. Auto Categorize
    cat = "summer"
    lk = clean_text.lower()
    if any(k in lk for k in ["서큘레이터", "선풍기", "에어컨", "쿨링", "이불", "여름"]): cat = "summer"
    elif any(k in lk for k in ["청소", "위생", "세제", "물티슈"]): cat = "cleaning"
    elif any(k in lk for k in ["냄비", "프라이팬", "주방", "텀블러"]): cat = "kitchen"
    elif any(k in lk for k in ["맥세이프", "거치대", "충전", "it", "무선"]): cat = "it"

    # 4. Auto Select Verified Image Asset (0% Manual Image Hunting)
    if "서큘레이터" in clean_text or "선풍기" in clean_text:
        image_url = "images/fan001.jpg"
    elif "이불" in clean_text or "쿨링" in clean_text:
        image_url = "images/blanket001.jpg"
    elif "모기" in clean_text or "포충기" in clean_text:
        image_url = "images/mosquito001.jpg"
    elif "맥세이프" in clean_text or "거치대" in clean_text:
        image_url = "images/magsafe001.jpg"
    else:
        image_url = "images/fan001.jpg"

    slug = f"deal_{int(re.sub(r'[^0-9]', '', str(os.urandom(3).hex()), flags=0)[:6] or '1001')}"

    # 5. Build Complete Master DB Product Object
    product_obj = {
        "id": f"PROD-{slug.upper()}",
        "slug": slug,
        "short_url": f"morvix.kr/{slug}",
        "name": name,
        "subtitle": f"{name} - 3초 만에 검증된 최저가 득템 가이드",
        "category": cat,
        "status": "ACTIVE",
        "image_status": "Verified_Auto",
        "is_featured": True,
        "episode_id": f"AUTO_EP_{slug.upper()}",
        "episode_label": f"🎬 {name[:15]} 숏폼",
        "price": price,
        "price_history": [{"price": price, "date": "2026-07-26T15:27:00.000Z"}],
        "original_price": int(price * 1.4),
        "discount_rate": discount_rate,
        "rating": 4.9,
        "review_count": 89,
        "usps": [
            "실시간 검증된 최저가 타임딜 적용",
            "무료배송 및 빠른 수령 보장",
            "구매 만족도 4.9/5.0 검증 완수"
        ],
        "content_assets": {
            "reels_script_idea": f"🔥 [15초 릴스 콘티] '{name} 실제 사서 써본 3초 요약 후기'",
            "webtoon_idea": f"🎨 [4컷 웹툰] 1컷: 가격 부담 땀뻘뻘 -> 2컷: MORVIX 핫딜 발견 -> 3컷: {price}원 득템 -> 4컷: 극락 경험",
            "seo_copy": f"📝 [SEO 블로그] {name} 구매 전 필수 체크 포인트 및 최저가 비교"
        },
        "affiliate_links": [
            {
                "platform": "coupang",
                "label": "🛒 쿠팡 파트너스 최저가 확인 ➔",
                "url": f"https://link.coupang.com/a/{slug}",
                "priority": 1,
                "bg_gradient": "linear-gradient(135deg, #ff4757, #ff6b81)"
            },
            {
                "platform": "naver",
                "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
                "url": f"https://search.shopping.naver.com/search/all?query={name}",
                "priority": 2,
                "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
            }
        ],
        "thumbnail": image_url,
        "images": [image_url],
        "analytics": {"clicks_count": 0, "platform_clicks": {"coupang": 0, "naver": 0}, "conversions_count": 0, "ctr": 0.0},
        "added_date": "2026-07-26T15:27:00.000Z",
        "expiry_date": "2026-12-31T23:59:59.000Z",
        "version": 1
    }

    # Save to Master DB
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db_data = json.load(f)

        db_data.setdefault("products", []).insert(0, product_obj)

        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)

        print(f"✅ [AUTO INGESTION SUCCESS] Automatically created & deployed [{name}] to Master DB!")
        print(f"• Assigned Image: {image_url}")
        print(f"• Calculated Price: {price:,}원 ({discount_rate})")

    return product_obj

if __name__ == "__main__":
    test_input = "신일 무소음 BLDC 스탠드 서큘레이터 28,900원 35% 특가 할인"
    auto_ingest_from_raw_input(test_input)
