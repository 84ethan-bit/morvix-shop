"""
=============================================================================
MORVIX SHOP OS - Toss Official Smart Cycle Pipeline Daemon
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

TOKEN_URL = "https://oauth2.cert.toss.im/token"
API_BASE_URL = "https://sharelink.toss.im/openapi"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worker", "morvix_shop_db.json")

def get_access_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": ACCESS_KEY,
        "client_secret": SECRET_KEY,
        "scope": "sharelink:read sharelink:write"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception as e:
        print(f"❌ [토큰 발급 예외]: {e}", flush=True)
    return None

def fetch_limited_products(access_token, endpoint_path, max_count, category_label):
    """지정한 개수(max_count)까지만 페이징하며 상품 수집"""
    all_items = []
    cursor = None
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print(f"🔄 [{category_label}] 최대 {max_count}개 수집 시작...", flush=True)
    while len(all_items) < max_count:
        fetch_size = min(50, max_count - len(all_items))
        url = f"{API_BASE_URL}{endpoint_path}?size={fetch_size}"
        if cursor:
            url += f"&cursor={cursor}"
            
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get("resultType") == "SUCCESS":
                    success_data = res_data.get("success", {})
                    items = success_data.get("items", [])
                    if not items:
                        break
                    all_items.extend(items)
                    
                    has_next = success_data.get("hasNext", False)
                    cursor = success_data.get("nextCursor")
                    
                    if not has_next or not cursor:
                        break
                else:
                    break
            else:
                break
        except Exception as e:
            print(f"⚠️ [{category_label}] 수집 중 예외: {e}", flush=True)
            break
            
    print(f"📦 [{category_label}] 총 {len(all_items)}개 상품 수집 완료", flush=True)
    return all_items[:max_count]

def issue_share_link(access_token, taca_item_id):
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
    except Exception:
        pass
    return None

def load_existing_db():
    """기존 DB 로드 및 기존 쉐어링크 딕셔너리 복원"""
    existing_links = {}
    existing_categories = {"베스트": [], "오늘만 이가격": [], "전체": []}
    
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_categories = data.get("categories", existing_categories)
                for cat_name, items in existing_categories.items():
                    for item in items:
                        p_id = item.get("productId")
                        s_url = item.get("shareUrl")
                        if p_id and s_url:
                            existing_links[p_id] = s_url
        except Exception:
            pass
    return existing_links, existing_categories

def push_db_to_github(db_data):
    if not GH_TOKEN or not GH_REPO:
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
            "message": f"Auto-update smart cycle Toss shop DB [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]",
            "content": content_base64,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha

        put_res = requests.put(url, headers=headers, json=payload)
        return put_res.status_code in [200, 201]
    except Exception:
        pass
    return False

def run_pipeline_cycle(refresh_best=True):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 [스마트 파이프라인] 실행 (베스트 수집 여부: {refresh_best})", flush=True)
    
    access_token = get_access_token()
    if not access_token:
        print("💤 [파이프라인] 토큰 발급 실패", flush=True)
        return

    # 기존 링크와 카테고리 데이터 로드
    existing_links, existing_categories = load_existing_db()

    # 1. 베스트 상품 (3일에 1번만 재수집, 아니면 기존 데이터 유지)
    if refresh_best:
        best_items = fetch_limited_products(access_token, "/products/best-selling", 200, "베스트 상품")
        best_processed = []
        for item in best_items:
            taca_id = item.get('tacaItemId')
            if not taca_id:
                continue
            short_url = existing_links.get(taca_id) or issue_share_link(access_token, taca_id)
            if not short_url:
                continue
            existing_links[taca_id] = short_url
            best_processed.append({
                "productId": taca_id,
                "name": item.get('displayName'),
                "price": item.get('displayPrice'),
                "originalPrice": item.get('originalPrice'),
                "imageUrl": item.get('thumbnailUrl'),
                "shareUrl": short_url,
                "category": "베스트",
                "updatedAt": datetime.now().isoformat()
            })
        categorized_db_best = best_processed
    else:
        print("📦 [베스트 상품] 3일 주기가 아니므로 기존 데이터를 유지합니다.", flush=True)
        categorized_db_best = existing_categories.get("베스트", [])

    # 2. 오늘만 이가격 상품 (매일 24시간마다 100개 수집)
    today_items = fetch_limited_products(access_token, "/products/today-special", 100, "오늘만 이가격")
    today_processed = []
    for item in today_items:
        taca_id = item.get('tacaItemId')
        if not taca_id:
            continue
        short_url = existing_links.get(taca_id) or issue_share_link(access_token, taca_id)
        if not short_url:
            continue
        existing_links[taca_id] = short_url
        today_processed.append({
            "productId": taca_id,
            "name": item.get('displayName'),
            "price": item.get('displayPrice'),
            "originalPrice": item.get('originalPrice'),
            "imageUrl": item.get('thumbnailUrl'),
            "shareUrl": short_url,
            "category": "오늘만 이가격",
            "updatedAt": datetime.now().isoformat()
        })
    categorized_db_today = today_processed

    # 전체 통합 리스트 생성 (중복 제거)
    all_combined = []
    seen_ids = set()
    for item in categorized_db_best + categorized_db_today:
        if item["productId"] not in seen_ids:
            all_combined.append(item)
            seen_ids.add(item["productId"])

    db_data = {
        "updatedAt": datetime.now().isoformat(),
        "categories": {
            "전체": all_combined,
            "베스트": categorized_db_best,
            "오늘만 이가격": categorized_db_today
        }
    }

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, ensure_ascii=False, indent=4)

    push_db_to_github(db_data)
    print(f"✅ [파이프라인] 동기화 완료 (베스트: {len(categorized_db_best)}개, 오늘만 이가격: {len(categorized_db_today)}개)", flush=True)

if __name__ == "__main__":
    print("🛡️ Morvix Shop OS - Smart Cycle Daemon 가동", flush=True)
    
    # 최초 실행 시 베스트 상품 포함 전체 수집
    try:
        run_pipeline_cycle(refresh_best=True)
    except Exception as e:
        print(f"❌ 초기 실행 오류: {e}", flush=True)

    cycle_count = 0
    while True:
        # 24시간(86400초)마다 루프가 돔
        print("💤 [파이프라인] 24시간 대기 중...", flush=True)
        time.sleep(86400) 
        cycle_count += 1
        
        # 3일에 한 번(3번째 24시간 주기마다) 베스트 상품 재수집 (3 * 24시간 = 3일)
        if cycle_count % 3 == 0:
            try:
                run_pipeline_cycle(refresh_best=True)
            except Exception as e:
                print(f"❌ 베스트 재수집 오류: {e}", flush=True)
        else:
            try:
                run_pipeline_cycle(refresh_best=False)
            except Exception as e:
                print(f"❌ 오늘만 이가격 수집 오류: {e}", flush=True)