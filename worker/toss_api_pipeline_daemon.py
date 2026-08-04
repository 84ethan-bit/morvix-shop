"""
=============================================================================
MORVIX SHOP OS - Toss API Integrated Pipeline Daemon
worker/toss_api_pipeline_daemon.py
=============================================================================
"""
import os
import time
import json
from datetime import datetime
import requests

# 1. 렌더 환경 변수에서 키 불러오기
ACCESS_KEY = os.environ.get("TOSS_ACCESS_KEY")
SECRET_KEY = os.environ.get("TOSS_SECRET_KEY")
USER_LINK_ID = os.environ.get("TOSS_USER_LINK_ID")

# ※ 토스 측 공식 가이드에 명시된 정확한 API 엔드포인트 URL로 수정해 주세요.
BASE_URL = "https://api.toss.im/shopping" 

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worker", "morvix_shop_db.json")

def get_headers():
    """API 인증 헤더 생성"""
    return {
        "Access-Key": ACCESS_KEY,
        "Secret-Key": SECRET_KEY,
        "Content-Type": "application/json"
    }

def fetch_best_products_from_api():
    """토스 Open API를 통해 베스트 상품 및 하루특가 목록 수집"""
    url = f"{BASE_URL}/v1/products/best"
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"📦 [API 수집] 베스트 상품 {len(products)}개 성공적으로 가져옴")
            return products
        else:
            print(f"⚠️ [API 수집] 상품 조회 실패 [코드 {response.status_code}]: {response.text}")
    except Exception as e:
        print(f"⚠️ [API 수집] 요청 중 예외 발생: {e}")
    return []

def issue_share_link(product_id):
    """상품별 쉐어링크(수익 추적 링크) 발급"""
    url = f"{BASE_URL}/v1/share-link"
    payload = {
        "productId": product_id,
        "userLinkId": USER_LINK_ID
    }
    try:
        response = requests.post(url, headers=get_headers(), json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get('shareUrl')
        else:
            print(f"⚠️ [링크 발급] 실패 [코드 {response.status_code}]: {response.text}")
    except Exception as e:
        print(f"⚠️ [링크 발급] 예외 발생: {e}")
    return None

def load_local_db():
    """기존 로컬 DB 불러오기"""
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"products": []}

def save_local_db(data):
    """로컬 DB 저장하기"""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def run_pipeline_cycle():
    """1회 수집 및 링크 발급 파이프라인 실행"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 [API 파이프라인] 수집 시작")
    
    raw_products = fetch_best_products_from_api()
    if not raw_products:
        print("💤 [API 파이프라인] 수집된 상품이 없습니다. 다음 주기에 재시도합니다.")
        return

    db = load_local_db()
    
    new_count = 0
    for p in raw_products:
        p_id = p.get('productId')
        if not p_id:
            continue
            
        # 쉐어링크 발급 (수익 연동의 핵심)
        share_url = issue_share_link(p_id)
        if not share_url:
            continue
            
        processed_item = {
            "productId": p_id,
            "name": p.get('name'),
            "price": p.get('price'),
            "originalPrice": p.get('originalPrice'),
            "imageUrl": p.get('imageUrl'),
            "shareUrl": share_url, # 발급된 쉐어링크
            "updatedAt": datetime.now().isoformat()
        }
        
        # DB에 업데이트 또는 신규 추가
        db['products'] = [item for item in db.get('products', []) if item.get('productId') != p_id]
        db['products'].insert(0, processed_item)
        new_count += 1

    save_local_db(db)
    print(f"✅ [API 파이프라인] 총 {new_count}개의 상품 및 쉐어링크 갱신 완료")

if __name__ == "__main__":
    print("🛡️ Morvix Shop OS - Toss API 통합 파이프라인 데몬 가동")
    while True:
        try:
            run_pipeline_cycle()
        except Exception as e:
            print(f"❌ 파이프라인 실행 중 오류 발생: {e}")
        
        # 3시간 마다 반복 실행
        print("💤 [API 파이프라인] 다음 수집까지 3시간 대기 중...")
        time.sleep(10800)