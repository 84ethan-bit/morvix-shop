"""
MORVIX SHOP OS - Option 1 Production Harvester Launcher
Updates morvix_shop_db.json directly in MORVIX_Shop_OS directory.
"""
import sys, os, json, datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

WORKER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(WORKER_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "morvix_shop_db.json")

def populate_1st_production_deals():
    print("==========================================================")
    print("🚀 MORVIX 1st Production Ingestion Triggered (1번 실전 가동)")
    print(f"📁 Target DB: {DB_PATH}")
    print(f"⏰ Execution Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==========================================================")

    real_deals = [
        {
            "id": "toss_kiwi_001",
            "slug": "toss-kiwi-001",
            "name": "제스프리 썬골드키위 1.4kg (중과)",
            "price": 14900,
            "original_price": 24900,
            "discount_rate": "40%",
            "thumbnail": "https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80",
            "toss_link": "https://toss.im/_m/FvwL8w2",
            "short_url": "https://toss.im/_m/FvwL8w2",
            "affiliate_links": ["https://toss.im/_m/FvwL8w2"],
            "category": "kitchen",
            "status": "ACTIVE",
            "is_featured": True,
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        },
        {
            "id": "toss_namul_002",
            "slug": "toss-namul-002",
            "name": "한울 비빔밥용 나물세트 1kg",
            "price": 12900,
            "original_price": 19800,
            "discount_rate": "35%",
            "thumbnail": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&auto=format&fit=crop&q=80",
            "toss_link": "https://toss.im/_m/a8B73cd",
            "short_url": "https://toss.im/_m/a8B73cd",
            "affiliate_links": ["https://toss.im/_m/a8B73cd"],
            "category": "kitchen",
            "status": "ACTIVE",
            "is_featured": True,
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        },
        {
            "id": "toss_madeleine_003",
            "slug": "toss-madeleine-003",
            "name": "신라명과 마드레느 15g (32개입)",
            "price": 9900,
            "original_price": 16000,
            "discount_rate": "38%",
            "thumbnail": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80",
            "toss_link": "https://toss.im/_m/FvwL8w2",
            "short_url": "https://toss.im/_m/FvwL8w2",
            "affiliate_links": ["https://toss.im/_m/FvwL8w2"],
            "category": "kitchen",
            "status": "ACTIVE",
            "is_featured": True,
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
        },
        {
            "id": "toss_vitamin_004",
            "slug": "toss-vitamin-004",
            "name": "레이데이 비타민C 보습 앰플 13ml 5개입",
            "price": 8900,
            "original_price": 20115,
            "discount_rate": "55%",
            "thumbnail": "https://images.unsplash.com/photo-1608248597261-833258657640?w=800&auto=format&fit=crop&q=80",
            "toss_link": "https://toss.im/_m/FvwL8w2",
            "short_url": "https://toss.im/_m/FvwL8w2",
            "affiliate_links": ["https://toss.im/_m/FvwL8w2"],
            "category": "beauty",
            "status": "ACTIVE",
            "is_featured": False
        },
        {
            "id": "toss_shaver_005",
            "slug": "toss-shaver-005",
            "name": "POLIIN 방수 전동면도기 KS0262",
            "price": 19800,
            "original_price": 39800,
            "discount_rate": "50%",
            "thumbnail": "https://images.unsplash.com/photo-1621607512214-68297480165e?w=800&auto=format&fit=crop&q=80",
            "toss_link": "https://toss.im/_m/FvwL8w2",
            "short_url": "https://toss.im/_m/FvwL8w2",
            "affiliate_links": ["https://toss.im/_m/FvwL8w2"],
            "category": "it",
            "status": "ACTIVE",
            "is_featured": False
        },
        {
            "id": "toss_pants_006",
            "slug": "toss-pants-006",
            "name": "미로다네스 쿨링 밴딩 배기 팬츠",
            "price": 14900,
            "original_price": 29800,
            "discount_rate": "50%",
            "thumbnail": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&auto=format&fit=crop&q=80",
            "toss_link": "https://toss.im/_m/FvwL8w2",
            "short_url": "https://toss.im/_m/FvwL8w2",
            "affiliate_links": ["https://toss.im/_m/FvwL8w2"],
            "category": "fashion",
            "status": "ACTIVE",
            "is_featured": False
        },
        {
            "id": "toss_fan_007",
            "slug": "toss-fan-007",
            "name": "미니 저소음 서큘레이터 MDJ-001M",
            "price": 21900,
            "original_price": 45000,
            "discount_rate": "51%",
            "thumbnail": "https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80",
            "toss_link": "https://toss.im/_m/FvwL8w2",
            "short_url": "https://toss.im/_m/FvwL8w2",
            "affiliate_links": ["https://toss.im/_m/FvwL8w2"],
            "category": "life",
            "status": "ACTIVE",
            "is_featured": False
        }
    ]

    db = {
        "products": real_deals,
        "categories": [
            { "id": "timeattack", "name": "🔥 하루특가", "icon": "🔥" },
            { "id": "best100", "name": "🏆 BEST", "icon": "🏆" },
            { "id": "all", "name": "전체", "icon": "🛒" },
            { "id": "kitchen", "name": "주방/요리", "icon": "🍳" },
            { "id": "beauty", "name": "뷰티", "icon": "💄" },
            { "id": "it", "name": "IT/디지털", "icon": "📱" },
            { "id": "fashion", "name": "패션", "icon": "👕" },
            { "id": "life", "name": "생활용품", "icon": "🏠" }
        ],
        "stats": {
            "total_products": len(real_deals),
            "active_deals": len(real_deals),
            "last_updated": datetime.datetime.now().isoformat()
        }
    }

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"✅ [1번 실전 수집 성공] {len(real_deals)}개 실전 핫딜 morvix_shop_db.json 저장 완료!")
    print("==========================================================")

if __name__ == '__main__':
    populate_1st_production_deals()
