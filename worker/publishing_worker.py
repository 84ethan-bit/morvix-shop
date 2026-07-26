import json
import os
import sys

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def generate_publishing_assets(product):
    """Generate multi-channel publishing scripts and SEO assets for a product"""
    name = product.get("name", "핫딜 상품")
    price = product.get("price", 0)
    discount = product.get("discount_rate", "특가")

    content_assets = product.get("content_assets", {})

    if not content_assets.get("reels_script_idea"):
        content_assets["reels_script_idea"] = f"🔥 [15초 릴스 콘티] '{name} {discount}할인 억까 탈출! 실제 사용 후기 3초 요약'"

    if not content_assets.get("webtoon_idea"):
        content_assets["webtoon_idea"] = f"🎨 [4컷 웹툰] 1컷: 가격 부담 땀뻘뻘 -> 2컷: 모르빅스 핫딜 발견 -> 3컷: {price}원 득템 -> 4컷: 극락 경험"

    if not content_assets.get("seo_copy"):
        content_assets["seo_copy"] = f"📝 [SEO 블로그] {name} 구매 전 필수 체크 포인트 3가지 및 쿠팡/네이버 최저가 가격 비교"

    product["content_assets"] = content_assets
    return product

if __name__ == "__main__":
    test_prod = {"name": "[특가] 무선 서큘레이터", "price": 28900, "discount_rate": "35%"}
    res = generate_publishing_assets(test_prod)
    print("Publishing Worker Output:", json.dumps(res, ensure_ascii=False, indent=2))
