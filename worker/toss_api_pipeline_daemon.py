"""
=============================================================================
MORVIX SHOP OS - Toss API Integrated Pipeline Daemon (Debug Mode)
worker/toss_api_pipeline_daemon.py
=============================================================================
"""
import os
import time
import json
import base64
from datetime import datetime
import requests

ACCESS_KEY = os.environ.get("TOSS_ACCESS_KEY")
SECRET_KEY = os.environ.get("TOSS_SECRET_KEY")
USER_LINK_ID = os.environ.get("TOSS_USER_LINK_ID")
GH_TOKEN = os.environ.get("GH_TOKEN")
GH_REPO = os.environ.get("GH_REPO", "username/repository-name")

BASE_URL = "https://api.toss.im/shopping" 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worker", "morvix_shop_db.json")

def get_headers():
    print(f"🔑 [DEBUG] 인증 키 확인 -> Access-Key 존재여부: {bool(ACCESS_KEY)}, Secret-Key 존재여부: {bool(SECRET_KEY)}")
    return {
        "Access-Key": ACCESS_KEY,
        "Secret-Key": SECRET_KEY,
        "Content-Type": "application/json"
    }

def fetch_best_products_from_api():
    url = f"{BASE_URL}/v1/products/best"
    print(f"🌐 [API 요청] URL 시도 중: {url}")
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        print(f"📥 [API 응답] 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"📦 [API 수집] 베스트 상품 {len(products)}개 성공적으로 가져옴")
            return products
        else:
            print(f"⚠️ [API 수집] 상품 조회 실패 [코드 {response.status_code}]: {response.text}")
    except Exception as e:
        print(f"❌ [API 수집] 요청 중 예외 발생: {e}")
    return []

def issue_share_link(product_id):
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

def push_db_to_github(db_data):
    if not GH_TOKEN or not GH_REPO:
        print("⚠️ [GitHub Sync] GH_TOKEN 또는 GH_REPO 설정이 없어 깃허브 푸시를 생략합니다.")
        return False

    file_path = "worker/morvix_shop_db.json"
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{file_path}"
    
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        res = requests.get(url, headers=headers)
        sha = res.json().get("sha") if res.status_code == 200 else None

        json_str = json.dumps(db_data, ensure_ascii=False, indent=4)
        content_bytes = json_str.encode("utf-8")
        content_base64 = base64.b64encode(content_bytes).decode("utf-8")

        payload = {
            "message": f"Auto-update categorized shop DB via Toss API [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]",
            "content": content_base64,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        put_res = requests.put(url, headers=headers, json=payload)
        if put_res.status_code in [200, 201]:
            print("🚀 [GitHub Sync] 카테고리별 분류된 DB 파일 깃허브 자동 푸시 성공!")
            return True
        else:
            print(f"⚠️ [GitHub Sync] 푸시 실패 [코드 {put_res.status_code}]: {put_res.text}")
    except Exception as e:
        print(f"⚠️ [GitHub Sync] 예외 발생: {e}")
    return False

def run_pipeline_cycle():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 [API 파이프라인] 수집 사이클 시작")
    
    raw_products = fetch_best_products_from_api()
    if not raw_products:
        print("💤 [API 파이프라인] 수집된 상품이 없습니다. 다음 주기에 재시도합니다.")
        return

    categorized_db = {"전체": []}

    success_count = 0
    for p in raw_products:
        p_id = p.get('productId')
        if not p_id:
            continue
            
        share_url = issue_share_link(p_id)
        if not share_url:
            continue
            
        category_name = p.get('categoryName') or p.get('category') or "기타"

        processed_item = {
            "productId": p_id,
            "name": p.get('name'),
            "price": p.get('price'),
            "originalPrice": p.get('originalPrice'),
            "imageUrl": p.get('imageUrl'),
            "shareUrl": share_url,
            "category": category_name,
            "updatedAt": datetime.now().isoformat()
        }

        categorized_db["전체"].append(processed_item)

        if category_name not in categorized_db:
            categorized_db[category_name] = []
        categorized_db[category_name].append(processed_item)
        
        success_count += 1

    if success_count == 0:
        print("💤 [API 파이프라인] 유효하게 발급된 상품 링크가 없습니다.")
        return

    db_data = {
        "updatedAt": datetime.now().isoformat(),
        "categories": categorized_db
    }

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

    push_db_to_github(db_data)
    print(f"✅ [API 파이프라인] 총 {success_count}개 상품 카테고리별 자동 분류 및 깃허브 동기화 완료")

if __name__ == "__main__":
    print("🛡️ Morvix Shop OS - Toss API 디버그 파이프라인 데몬 가동")
    # 시작하자마자 첫 1회 즉시 실행
    try:
        run_pipeline_cycle()
    except Exception as e:
        print(f"❌ 초기 실행 중 오류 발생: {e}")

    while True:
        print("💤 [API 파이프라인] 다음 수집까지 12시간 대기 중...")
        time.sleep(43200)
        try:
            run_pipeline_cycle()
        except Exception as e:
            print(f"❌ 반복 실행 중 오류 발생: {e}")