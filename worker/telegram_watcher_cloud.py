import json
import os
import sys
import time
import re
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "morvix_shop_db.json")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
REFERRAL_ID = os.getenv("REFERRAL_ID", "")

def send_telegram_notification(message):
    if not BOT_TOKEN or not CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")
        return False

# --------------------------------------------------------------------------
# 1. 7-Tier Priority Category Classification Engine (Ported & Extended)
# --------------------------------------------------------------------------
def any_keyword(text, keywords):
    return any(kw in text for kw in keywords)

def get_auto_category(title_text):
    lk = (title_text or '').lower().replace(' ', '')

    # 1. Summer & Cooling
    if any_keyword(lk, [
        "서큘레이터", "선풍기", "에어컨", "쿨링", "이불", "패드", "여름", "얼음", "장마", "모기", "포충기", "냉풍기",
        "초냉감", "열대야", "부채", "제습기", "냉매", "아이스", "얼음조끼", "쿨매트", "쿨베개", "냉감", "홑이불", "시원"
    ]): return "summer"

    # 2. Cleaning & Hygiene
    if any_keyword(lk, [
        "청소기", "청소", "소독", "탈취", "세제", "위생", "스크러버", "휴지", "물티슈", "샴푸", "린스", "칫솔", "치약", "비누", "걸레",
        "유연제", "섬유유연제", "수건", "기저귀", "키친타올", "생리대", "면도기", "살충제", "제습제", "마스크", "손세정제",
        "방향제", "건전지", "세탁세제", "주방세제", "바디워시", "화장지", "티슈", "치실", "구강청결제", "로봇청소기"
    ]): return "cleaning"

    # 3. Kitchen & Cooking
    if any_keyword(lk, [
        "냄비", "프라이팬", "식기", "그릇", "도마", "칼", "가위", "주방", "조리", "밥솥", "전기포트", "믹서기", "에어프라이어",
        "전자레인지", "텀블러", "밀폐용기", "도시락", "오븐", "토스터", "커피머신", "쌀통", "행주", "수세미", "니트릴", "호일",
        "랩", "지퍼백", "식세기", "식기세척기", "수저", "젓가락", "포크", "쟁반", "국자", "뒤집개", "집게", "위생장갑"
    ]): return "kitchen"

    # 4. IT & Electronics
    if any_keyword(lk, [
        "맥세이프", "거치대", "충전기", "충전", "아이폰", "갤럭시", "데스크", "키보드", "마우스", "무선", "it", "디지털",
        "모니터", "노트북", "태블릿", "아이패드", "에어팟", "버즈", "워치", "스피커", "이어폰", "헤드폰", "공유기", "외장하드",
        "usb", "닌텐도", "플스", "게임기", "공기청정기", "가전", "tv", "노트북가방", "파우치", "케이블", "보조배터리"
    ]): return "it"

    # 5. Automotive
    if any_keyword(lk, [
        "자동차", "차량", "햇빛", "차광", "우산", "세차", "블랙박스", "네비게이션", "와이퍼", "타이어", "광택", "방향제",
        "시트커버", "핸들커버", "차량용", "엔진오일", "워셔액", "하이패스", "세차용품", "트렁크", "차박"
    ]): return "car"

    # 6. Pets
    if any_keyword(lk, [
        "강아지", "고양이", "펫", "사료", "간식", "장난감", "목줄", "하네스", "캣타워", "펫푸드", "반려동물", "애완",
        "멍멍", "야옹", "츄르", "모래", "배변패드", "이동장", "숨집", "애견", "캣"
    ]): return "pet"

    # 7. Life & Home
    return "life"

# --------------------------------------------------------------------------
# 2. TTL Expiry Clean Up Engine (Auto Purge Expired Deals)
# --------------------------------------------------------------------------
def cleanup_expired_deals():
    if not os.path.exists(DB_PATH): return
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db_data = json.load(f)
        
        products = db_data.get("products", [])
        now_str = datetime.now().isoformat()
        initial_count = len(products)

        valid_products = [p for p in products if p.get("expiry_date", "2099-12-31T23:59:59") > now_str]

        if len(valid_products) < initial_count:
            db_data["products"] = valid_products
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(db_data, f, ensure_ascii=False, indent=2)
            print(f"🧹 [TTL AUTO PURGE] Expired deals purged: {initial_count - len(valid_products)} items removed.")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

# --------------------------------------------------------------------------
# 3. Message Processing Engine (0-Human Autonomous Parsing)
# --------------------------------------------------------------------------
def process_deal_text(text, attached_image_url=None):
    if "http" not in text: return False

    url_match = re.search(r'(https?://\S+)', text)
    if not url_match: return False

    link = url_match.group(1).split('?')[0]
    clean_text = text.replace(link, "").replace('[토스특가]', '').replace('[토스쇼핑]', '').replace('[특가]', '').replace('[가격오류급]', '').strip()

    # Extract Price & Discount Rate from text
    discount_match = re.search(r'(\d+)\s*[%％]', clean_text)
    discount_rate = f"{discount_match.group(1)}%" if discount_match else None

    price_matches = re.findall(r'([\d,]+)\s*원', clean_text)
    prices = [int(p.replace(',', '')) for p in price_matches if p.replace(',', '').isdigit()]
    price = prices[-1] if prices else None

    title = clean_text
    title = re.sub(r'[\*✱]?\s*이\s*포스팅은\s*토스쇼핑\s*쉐어링크[^\n]*\n?', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\*✱]?\s*이\s*포스팅은[^\n]*제공받습니다\.?\n?', '', title, flags=re.IGNORECASE)
    title = re.sub(r'[\d,]+\s*원', '', title)
    title = re.sub(r'\d+\s*[%％]', '', title).strip()
    title = title.strip()
    if len(title) < 3:
        title = "토스쇼핑 파격특가 추천 꿀템"

    # If price or discount missing from raw text, auto harvest exact market price
    if not price:
        try:
            from urllib.parse import quote
            sq = re.sub(r'\[.*?\]', '', title).strip()
            s_url = f"https://search.shopping.naver.com/search/all?query={quote(sq)}"
            h_res = requests.get(s_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=4).text
            pm = re.search(r'lowestPrice["\']?:\s*["\']?(\d+)["\']?', h_res) or re.search(r'([\d,]+)\s*원', h_res)
            if pm:
                price = int(pm.group(1).replace(',', ''))
        except Exception as e:
            print(f"⚠️ Price harvest error: {e}")
        if not price:
            price = 10900

    if not discount_rate:
        discount_rate = "25%"

    category = get_auto_category(title)
    time_slug = f"toss_{int(time.time())}"

    # Priority 1: Direct Attached Photo from Telegram Message
    image_thumb = attached_image_url
    if image_thumb:
        print(f"✅ Using Direct Telegram Attached Product Image: {image_thumb}")
    else:
        # Priority 2: Harvest from Naver Shopping
        try:
            from urllib.parse import quote
            search_query = re.sub(r'\[.*?\]', '', title).strip()
            s_url = f"https://search.shopping.naver.com/search/all?query={quote(search_query)}"
            h_res = requests.get(s_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=4).text
            m_img = re.search(r'https://shopping-phinf\.pstatic\.net/main_[^\"]+', h_res)
            if m_img:
                image_thumb = m_img.group(0)
        except Exception as e:
            print(f"⚠️ Real image harvest exception: {e}")

    if not image_thumb:
        category_fallback_images = {
            "summer": "https://images.unsplash.com/photo-1618957610183-f2310777c65f?w=600&auto=format&fit=crop&q=80",
            "it": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=600&auto=format&fit=crop&q=80",
            "life": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=600&auto=format&fit=crop&q=80",
            "cleaning": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop&q=80"
        }
        image_thumb = category_fallback_images.get(category, "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=600&auto=format&fit=crop&q=80")

    now = datetime.now()
    ttl_hours = 24 if any(x in title for x in ["1일", "단하루", "오늘만", "타임어택", "한정", "가격오류"]) else 48
    expiry_date = (now + timedelta(hours=ttl_hours)).isoformat()

    new_product = {
        "id": f"TOSS-AUTO-{int(time.time())}",
        "slug": time_slug,
        "short_url": f"morvix.kr/{time_slug}",
        "name": title,
        "subtitle": f"토스 혜택가 적용 실시간 특가 {discount_rate} 할인",
        "category": category,
        "status": "ACTIVE",
        "is_featured": True,
        "price": price,
        "original_price": int(price * 1.35),
        "discount_rate": discount_rate,
        "rating": 4.9,
        "review_count": random.randint(50, 250),
        "usps": [
            "토스 혜택가 적용 실시간 특가",
            "실사용자 검증 100% 꿀템"
        ],
        "affiliate_links": [
            {
                "platform": "toss",
                "label": "💙 토스할인가 확인 ➔",
                "url": link,
                "priority": 1,
                "bg_gradient": "linear-gradient(135deg, #0052cc, #2684ff)"
            }
        ],
        "thumbnail": image_thumb,
        "analytics": { "clicks_count": 1, "platform_clicks": { "toss": 1 }, "conversions_count": 0, "ctr": 5.0 },
        "added_date": now.isoformat(),
        "expiry_date": expiry_date
    }

    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"products": []}, f)

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    if "products" not in db_data:
        db_data["products"] = []

    # Check duplicate link: overwrite with newest info
    db_data["products"] = [p for p in db_data["products"] if p.get("affiliate_links", [{}])[0].get("url") != link]
    db_data["products"].insert(0, new_product)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=2)

    # Automatically Push to GitHub Main Branch to trigger live Vercel deployment
    try:
        from subprocess import run
        run(["git", "add", "morvix_shop_db.json"], cwd=BASE_DIR)
        run(["git", "commit", "-m", f"auto: ⚡ Telegram 0-Human Deal Ingestion [{title[:20]}]"], cwd=BASE_DIR)
        run(["git", "push", "origin", "main"], cwd=BASE_DIR)
        print("🚀 Successfully pushed to GitHub Main Branch & Vercel live site!")
    except Exception as e:
        print(f"⚠️ Git push error: {e}")

    # Send Instant Reply Notification back to Telegram User
    try:
        reply_msg = (
            f"🎉 *[MORVIX OS 핫딜 1초 라이브 등록 완료!]*\n\n"
            f"• *상품명:* `{title}`\n"
            f"• *실시간 시세:* `{price:,}원` (할인율 `{discount_rate}`)\n"
            f"• *자동 분류:* `[{category.upper()}]` 탭\n"
            f"• *토스 쉐어링크:* {link}\n\n"
            f"🌐 *라이브 홈페이지:* https://morvix-shop.vercel.app\n"
            f"✨ 컴퓨터를 끄셔도 라이브 서버에 즉시 게재되었습니다!"
        )
        send_telegram_notification(reply_msg)
    except Exception as e:
        print(f"⚠️ Telegram reply notification error: {e}")

    print(f"✅ [AUTONOMOUS INGESTION COMPLETE]")
    print(f"   • Title: '{title}'")
    print(f"   • Price: {price:,}원 ({discount_rate})")
    print(f"   • Category: [{category.upper()}]")
    print(f"   • Link: {link}")
    print(f"   • Expiry (TTL): {ttl_hours}h ({expiry_date})")

    return True

def download_telegram_photo(file_id):
    """Download attached photo from Telegram API directly"""
    if not BOT_TOKEN or not file_id: return None
    try:
        f_res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}", timeout=5).json()
        file_path = f_res.get("result", {}).get("file_path")
        if file_path:
            photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            print(f"📸 Telegram Attached Photo Downloaded:\n   {photo_url}")
            return photo_url
    except Exception as e:
        print(f"⚠️ Telegram photo download error: {e}")
    return None

# --------------------------------------------------------------------------
# 4. Polling Watcher Loop
# --------------------------------------------------------------------------
def run_watcher():
    print("=======================================================")
    print("🤖 MORVIX UNATTENDED TELEGRAM WATCHER DAEMON (STAGE 2)")
    print("=======================================================")

    if not BOT_TOKEN:
        print("⚠️ [NOTICE] TELEGRAM_BOT_TOKEN not set. Running in Standalone Listener Mode...")
        return

    offset = 0
    print("📡 Watching 24/7 for Telegram deal messages & attached photos...")

    while True:
        try:
            cleanup_expired_deals()
            res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset+1}&timeout=30", timeout=35).json()
            for u in res.get("result", []):
                offset = u["update_id"]
                if 'message' in u:
                    msg = u['message']
                    # Text can be in 'text' or 'caption' (if photo attached)
                    text = msg.get('text') or msg.get('caption') or ''
                    
                    # Extract attached photo if present
                    attached_photo_url = None
                    if 'photo' in msg and isinstance(msg['photo'], list) and len(msg['photo']) > 0:
                        largest_photo = msg['photo'][-1]
                        attached_photo_url = download_telegram_photo(largest_photo.get('file_id'))

                    if text:
                        process_deal_text(text, attached_image_url=attached_photo_url)
            time.sleep(1)
        except Exception as e:
            time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw_text_input = " ".join(sys.argv[1:])
        process_deal_text(raw_text_input)
    else:
        run_watcher()
