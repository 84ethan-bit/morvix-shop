const https = require('https');
const http = require('http');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const targetUrl = req.query.url;
  if (!targetUrl) {
    return res.status(400).json({ error: 'Missing url query param' });
  }

  try {
    const data = await fetchUrlWithRedirects(targetUrl);
    
    // 1. Extract Image (OpenGraph or Naver/Coupang CDN regex)
    let image = getOgProperty(data, 'image') || getOgProperty(data, 'image:src');
    if (!image) {
      const phinfMatch = data.match(/(https:\/\/(shopping-phinf|shop-phinf)\.pstatic\.net\/main_[^"'\s>]+)/i);
      if (phinfMatch) image = phinfMatch[1];
    }
    if (!image) {
      const coupangMatch = data.match(/(https:\/\/thumbnail[^"'\s>]+\.coupangcdn\.com\/[^"'\s>]+)/i);
      if (coupangMatch) image = coupangMatch[1];
    }

    // 2. Extract Title
    let rawTitle = getOgProperty(data, 'title') || data.match(/<title[^>]*>([^<]+)<\/title>/i)?.[1] || '';
    let title = rawTitle.replace(/[-|:종합쇼핑몰|스마트스토어|쿠팡|네이버].*$/i, '').trim();
    if (!title || title.length < 2) title = '모르빅스 검증 꿀템';

    // 3. Extract Price & Discount
    let priceNum = null;
    const ogPrice = getOgProperty(data, 'price:amount') || getOgProperty(data, 'product:price:amount');
    if (ogPrice && !isNaN(parseInt(ogPrice))) {
      priceNum = parseInt(ogPrice);
    } else {
      const priceMatch = data.match(/["']price["']\s*:\s*["']?(\d{4,7})["']?/i) || data.match(/(\d{1,3}(,\d{3})+)\s*원/);
      if (priceMatch) {
        priceNum = parseInt(priceMatch[1].replace(/,/g, ''));
      }
    }
    if (!priceNum || priceNum < 1000) priceNum = 28900;

    const originalPrice = Math.round(priceNum * 1.4);
    const discountRate = `${Math.round(((originalPrice - priceNum) / originalPrice) * 100)}%`;

    // 4. Extract Brand
    let brand = getOgProperty(data, 'brand') || getOgProperty(data, 'site_name') || 'MORVIX PARTNERS';

    // 5. Infer Category from Title Keywords
    let inferredCategory = 'life';
    const lowerTitle = title.toLowerCase();
    if (/서큘레이터|선풍기|에어컨|쿨링|이불|여름|얼음|장마|모기|포충기/.test(title)) {
      inferredCategory = 'summer';
    } else if (/청소|소독|탈취|세제|위생|스크러버/.test(title)) {
      inferredCategory = 'cleaning';
    } else if (/주방|냄비|프라이팬|다지기|요리|식기|그릇/.test(title)) {
      inferredCategory = 'kitchen';
    } else if (/맥세이프|거치대|충전|아이폰|데스크|키보드|마우스|무선|it|디지털/.test(title)) {
      inferredCategory = 'it';
    } else if (/자동차|차량|햇빛|차광|우산|세차|블랙박스/.test(title)) {
      inferredCategory = 'car';
    } else if (/고양이|강아지|반려|펫|정수기|사료|간식/.test(title)) {
      inferredCategory = 'pet';
    }

    // 6. Auto-generate AI Content Engine Assets
    const reelsScriptIdea = `🔥 [15초 릴스 콘티] '${title} 실사용 시충격 문제 해결 비포/애프터 1초 극락 숏폼'`;
    const webtoonIdea = `🎨 [4컷 웹툰] 1컷: 일상의 억까 -> 2컷: 스트레스 폭발 -> 3컷: ${title} 구원 -> 4컷: 상쾌한 결말`;
    const seoCopy = `📝 [SEO 리뷰] ${title} 실제 사용 후기, 장단점 분석 및 쿠팡/네이버 파트너스 최저가 비교 가이드`;

    return res.status(200).json({
      success: true,
      title: title,
      image: image || 'https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80',
      price: priceNum,
      original_price: originalPrice,
      discount_rate: discountRate,
      brand: brand,
      category: inferredCategory,
      reels_script_idea: reelsScriptIdea,
      webtoon_idea: webtoonIdea,
      seo_copy: seoCopy,
      url: targetUrl
    });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
};

function fetchUrlWithRedirects(url, maxRedirects = 5) {
  return new Promise((resolve, reject) => {
    if (maxRedirects <= 0) return reject(new Error('Too many redirects'));

    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
      }
    }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        let redirectUrl = res.headers.location;
        if (redirectUrl.startsWith('/')) {
          const u = new URL(url);
          redirectUrl = `${u.protocol}//${u.host}${redirectUrl}`;
        }
        return fetchUrlWithRedirects(redirectUrl, maxRedirects - 1).then(resolve).catch(reject);
      }

      let body = '';
      res.on('data', chunk => { body += chunk; });
      res.on('end', () => resolve(body));
    });

    req.on('error', reject);
    req.setTimeout(8000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

function getOgProperty(html, property) {
  const match = html.match(new RegExp(`<meta[^>]*property=["']og:${property}["'][^>]*content=["']([^"']+)["']`, 'i')) ||
                html.match(new RegExp(`<meta[^>]*content=["']([^"']+)["'][^>]*property=["']og:${property}["']`, 'i')) ||
                html.match(new RegExp(`<meta[^>]*name=["']${property}["'][^>]*content=["']([^"']+)["']`, 'i'));
  return match ? match[1] : null;
}
