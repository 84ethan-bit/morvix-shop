"""
=============================================================================
MORVIX SHOP OS - Toss ShareLink Open API Harvester
worker/toss_api_harvester.py
=============================================================================
"""
import os
import requests

# 1. 렌더 환경 변수에서 키 불러오기
ACCESS_KEY = os.environ.get("TOSS_ACCESS_KEY")
SECRET_KEY = os.environ.get("TOSS_SECRET_KEY")
USER_LINK_ID = os.environ.get("TOSS_USER_LINK_ID")

# 2. 토스 Open API 기본 설정 (공식 가이드 기준 엔드포인트 적용)
# ※ 테스트(알파) 환경과 운영(프로덕션) 환경 URL에 맞춰 조정하세요.
BASE_URL = "https://api.toss.im/shopping" # 예시 엔드포인트 (가이드 참고)

def get_headers():
    """API 인증 헤더 생성"""
    return {
        "Access-Key": ACCESS_KEY,
        "Secret-Key": SECRET_KEY,
        "Content-Type": "application/json"
    }

def fetch_best_products():
    """카테고리 베스트 / 베스트 상품 조회"""
    url = f"{BASE_URL}/v1/products/best"
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"📦 베스트 상품 조회 성공: {len(data.get('products', []))}개 확보")
            return data.get('products', [])
        else:
            print(f"⚠️ 베스트 상품 조회 실패 [코드 {response.status_code}]: {response.text}")
    except Exception as e:
        print(f"⚠️ API 요청 예외 발생: {e}")
    return []

def issue_share_link(product_id):
    """상품별 쉐어링크(추적 링크) 발급"""
    url = f"{BASE_URL}/v1/share-link"
    payload = {
        "productId": product_id,
        "userLinkId": USER_LINK_ID
    }
    try:
        response = requests.post(url, headers=get_headers(), json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 반환된 추적 링크 반환
            return data.get('shareUrl')
        else:
            print(f"⚠️ 쉐어링크 발급 실패 [코드 {response.status_code}]: {response.text}")
    except Exception as e:
        print(f"⚠️ 쉐어링크 요청 예외 발생: {e}")
    return None

if __name__ == "__main__":
    print("🚀 토스 Open API 수집 테스트 시작...")
    products = fetch_best_products()
    
    for p in products[:3]: # 테스트로 상위 3개만 링크 발급 테스트
        p_id = p.get('productId')
        p_name = p.get('name')
        
        # 반드시 쉐어링크 발급 API를 거쳐야 수익 집계가 됩니다!
        share_url = issue_share_link(p_id)
        print(nels := f"상품명: {p_name} -> 발급된 쉐어링크: {share_url}")