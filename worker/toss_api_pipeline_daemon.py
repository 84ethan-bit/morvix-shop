"""
=============================================================================
MORVIX SHOP OS - Toss API Official Pipeline Daemon (Based on Docs)
worker/toss_api_pipeline_daemon.py
=============================================================================
"""
import os
import time
import json
import base64
from datetime import datetime
import requests

# 환경 변수 불러오기
ACCESS_KEY = os.environ.get("TOSS_ACCESS_KEY")
SECRET_KEY = os.environ.get("TOSS_SECRET_KEY")
USER_LINK_ID = os.environ.get("TOSS_USER_LINK_ID") # 문서상의 publisherId 역할
GH_TOKEN = os.environ.get("GH_TOKEN")
GH_REPO = os.environ.get("GH_REPO", "username/repository-name")

# 문서에 명시된 공식 오픈 아키텍처 주소
TOKEN_URL = "https://oauth2.cert.toss.im/token" # 알파/테스트 기준 (운영시 변경)
API_BASE_URL = "https://sharelink.toss.im/openapi"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worker", "morvix_shop_db.json")

def get_access_token():
    """1단계: 액세스 토큰 발급"""
    payload = {
        "grant_type": "client_credentials",
        "client_id": ACCESS_KEY,
        "client_secret": SECRET_KEY,
        "scope": "sharelink:read sharelink:write"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("🔑 [토큰 발급] 액세스 토큰 성공적으로 획득", flush=True)
            return token
        else:
            print(f"⚠️ [토큰 발급] 실패 [코드 {response.status_code}]: {response.text}", flush=True)
    except Exception as e:
        print(f"❌ [토큰 발급] 예외 발생: {e}", flush=True)
    return None

def check_health(access_token):
    """2단계: 연결 확인 (Health Check)"""
    url = f"{API_BASE_URL}/health"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("🟢 [Health Check] 연결 상태 정상 (ok)", flush=True)
            return True
        else:
            print(f"⚠️ [Health Check] 실패: {response.text}", flush=True)
    except Exception as e:
        print(f"❌ [Health Check] 예외 발생: {e}", flush=True)
    return False

def fetch_best_products(access_token):
    """3단계: 상품 목록 가져오기 (베스트 셀링)"""
    url = f"{API_BASE_URL}/products/best-selling?size=20"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("resultType") == "SUCCESS":
                items = res_data.get("success", {}).get("items", [])
                print(f"📦 [상품 수집] 베스트 상품 {len(items)}개 성공적으로 가져옴", flush=True)
                return items
            else:
                print(f"⚠️ [상품 수집] API 응답 FAIL: {res_data}", flush=True)
        else:
            print(f"⚠️ [상품 수집] 조회 실패 [코드 {response.status_code}]: {response.text}", flush=True)
    except Exception as e:
        print(f"❌ [상품 수집] 요청 중 예외 발생: {e}", flush=True)
    return []

def issue_share_link(access_token, taca_item_id):
    """4단계: 쉐어링크 발급"""
    url = f"{API_BASE_URL}/links"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "tacaItemId": taca_item_id,
        "publisherId": USER_LINK_ID
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("resultType") == "SUCCESS":
                return res_data.get("success", {}).get("shortUrl")
        print(f"⚠️ [링크 발급] 실패: {response.text}", flush=True)
    except Exception as e:
        print(f"⚠️ [링크 발급] 예외 발생: {e}", flush=True)
    return None

def push_db_to_github(db_data):
    """GitHub API를 통한 자동 커밋 및 푸시"""
    if not GH_TOKEN or not GH_REPO:
        print("⚠️ [GitHub Sync] 설정 누락으로 푸시 생략", flush=True)
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
        content_base64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

        payload = {
            "message": f"Auto-update official Toss shop DB [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]",
            "content": content_base64,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        put_res = requests.put(url, headers=headers, json=payload)
        if put_res.status_code in [200, 201]:
            print("🚀 [GitHub Sync] 깃허브 DB 자동 푸시 성공!", flush=True)
            return True
    except Exception as e:
        print(f"⚠️ [GitHub Sync] 예외 발생: {e}", flush=True)
    return False

def run_pipeline_cycle():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 [API 파이프라인] 수집 사이클 시작", flush=True)
    
    # 1단계: 토큰 발급
    access_token = get_access_token()
    if not access_token:
        print("💤 [API 파이프라인] 토큰 발급 실패로 이번 주기를 종료합니다.", flush=True)
        return

    # 2단계: 연결 확인
    if not check_health(access_token):
        print("💤 [API 파이프라인] Health check 실패로 이번 주기를 종료합니다.", flush=True)
        return

    # 3단계: 상품 목록 가져오기
    raw_items = fetch_best_products(access_token)
    if not raw_items:
        print("💤 [API 파이프라인] 수집된 상품이 없습니다.", flush=True)
        return

    categorized_db = {"전체": []}
    success_count = 0

    for item in raw_items:
        taca_item_id = item.get('tacaItemId')
        if not taca_item_id:
            continue
            
        # 4단계: 쉐어링크 발급 (shortUrl 확보)
        short_url = issue_share_link(access_token, taca_item_id)
        if not short_url:
            continue
            
        # 가이드에 따라 productUrl이 아닌 발급받은 shortUrl을 사용
        processed_item = {
            "productId": taca_item_id,
            "name": item.get('displayName'),
            "price": item.get('displayPrice'),
            "originalPrice": item.get('originalPrice'),
            "imageUrl": item.get('thumbnailUrl'),
            "shareUrl": short_url, # 수익 집계가 되는 쉐어링크
            "category": "베스트",
            "updatedAt": datetime.now().isoformat()
        }

        categorized_db["전체"].append(processed_item)
        success_count += 1

    if success_count == 0:
        print("💤 [API 파이프라인] 유효하게 발급된 상품 링크가 없습니다.", flush=True)
        return

    db_data = {
        "updatedAt": datetime.now().isoformat(),
        "categories": categorized_db
    }

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

    push_db_to_github(db_data)
    print(f"✅ [API 파이프라인] 총 {success_count}개 상품 쉐어링크 연동 및 깃허브 동기화 완료", flush=True)

if __name__ == "__main__":
    print("🛡️ Morvix Shop OS - Toss Official API 데몬 가동", flush=True)
    try:
        run_pipeline_cycle()
    except Exception as e:
        print(f"❌ 초기 실행 오류: {e}", flush=True)

    while True:
        print("💤 [API 파이프라인] 다음 수집까지 12시간 대기 중...", flush=True)
        time.sleep(43200)
        try:
            run_pipeline_cycle()
        except Exception as e:
            print(f"❌ 반복 실행 오류: {e}", flush=True)