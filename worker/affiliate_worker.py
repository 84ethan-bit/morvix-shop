import json
import os
import sys
import re

# Force UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def normalize_affiliate_link(raw_url, platform="coupang"):
    """Normalize and format affiliate URLs safely adhering to platform guidelines"""
    if not raw_url:
        return ""
    
    raw_url = raw_url.strip()
    
    if platform == "coupang":
        # Ensure proper Coupang Partners affiliate link structure
        if "link.coupang.com" in raw_url:
            return raw_url
        match = re.search(r'coupang\.com/vp/products/(\d+)', raw_url)
        if match:
            prod_id = match.group(1)
            return f"https://link.coupang.com/a/{prod_id}"
        return raw_url
        
    elif platform == "naver":
        if "search.shopping.naver.com" in raw_url or "brand.naver.com" in raw_url:
            return raw_url
        return raw_url

    return raw_url

def process_product_affiliates(product):
    """Process and audit affiliate links array for a given product master item"""
    if not product.get("affiliate_links"):
        product["affiliate_links"] = []
        
    links = product["affiliate_links"]
    updated_links = []
    
    for l in links:
        plat = l.get("platform", "naver")
        url = l.get("url", "")
        norm_url = normalize_affiliate_link(url, plat)
        
        updated_links.append({
            "platform": plat,
            "label": l.get("label", "🛒 최저가 확인 ➔"),
            "url": norm_url,
            "priority": l.get("priority", 1),
            "bg_gradient": l.get("bg_gradient", "linear-gradient(135deg, #ff4757, #ff6b81)")
        })
        
    product["affiliate_links"] = updated_links
    return product

if __name__ == "__main__":
    test_prod = {
        "name": "Test Fan",
        "affiliate_links": [{"platform": "coupang", "url": "https://www.coupang.com/vp/products/123456"}]
    }
    res = process_product_affiliates(test_prod)
    print("Affiliate Worker Output:", json.dumps(res, ensure_ascii=False, indent=2))
