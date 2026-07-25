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
    
    // Extract og:image
    let image = getOgProperty(data, 'image') || getOgProperty(data, 'image:src');
    
    // Fallback 1: search for Naver CDN image URLs inside HTML (shopping-phinf or shop-phinf)
    if (!image) {
      const phinfMatch = data.match(/(https:\/\/(shopping-phinf|shop-phinf)\.pstatic\.net\/main_[^"'\s>]+)/i);
      if (phinfMatch) image = phinfMatch[1];
    }
    // Fallback 2: search for Coupang CDN image URLs inside HTML
    if (!image) {
      const coupangMatch = data.match(/(https:\/\/thumbnail[^"'\s>]+\.coupangcdn\.com\/[^"'\s>]+)/i);
      if (coupangMatch) image = coupangMatch[1];
    }

    // Extract og:title
    let title = getOgProperty(data, 'title') || data.match(/<title[^>]*>([^<]+)<\/title>/i)?.[1] || '';
    title = title.replace(/[-|].*$/, '').trim();

    return res.status(200).json({
      success: true,
      title: title || '네이버/쿠팡 검증 꿀템',
      image: image || null,
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
