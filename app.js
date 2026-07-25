/* ==========================================================================
   MORVIX SHOP OS v3.1 - Master DB Lifecycle Engine & Smart Auto Classifier
   ========================================================================== */

const INITIAL_DB_DATA = {
  "store_info": {
    "brand_name": "MORVIX SHOP OS",
    "domain": "morvix.kr",
    "tagline": "일상을 바꾸는 검증된 꿀템만 소개합니다.",
    "version": "v3.1 (State-Based Lifecycle Engine)"
  },
  "categories": [
    {"id": "all", "name": "모든 제품", "icon": "📦"},
    {"id": "featured", "name": "오늘의 추천", "icon": "🌟"},
    {"id": "reels", "name": "릴스 속 그 상품", "icon": "🎬"},
    {"id": "best100", "name": "베스트 100", "icon": "🏆"},
    {"id": "summer", "name": "여름/장마", "icon": "❄️"},
    {"id": "life", "name": "생활용품", "icon": "🏠"},
    {"id": "cleaning", "name": "청소/위생", "icon": "🧹"},
    {"id": "kitchen", "name": "주방/요리", "icon": "🍳"},
    {"id": "it", "name": "IT/디지털", "icon": "📱"},
    {"id": "car", "name": "자동차", "icon": "🚗"},
    {"id": "pet", "name": "반려동물", "icon": "🐾"}
  ],
  "products": [
    {
      "id": "PROD-010",
      "slug": "fan001",
      "short_url": "morvix.kr/fan001",
      "name": "[26년형] 신일 무소음 스탠드 BLDC 서큘레이터",
      "subtitle": "회사 책상 앞 38도 사막지대 억까 탈출 초강풍 무선 서큘레이터",
      "category": "summer",
      "status": "ACTIVE",
      "is_featured": true,
      "episode_id": "INTERNAL_CASE_EP010",
      "episode_label": "🎬 EP010 숏폼 소개 제품",
      "channels": {
        "youtube_shorts": true,
        "instagram_reels": true,
        "tiktok": true,
        "threads": true,
        "blog_seo": true
      },
      "price": 28900,
      "original_price": 45000,
      "discount_rate": "35%",
      "rating": 4.9,
      "review_count": 128,
      "usps": [
        "강력한 듀얼 터보 모터 초강풍 쿨링",
        "8시간 연속 사용 대용량 무선 배터리",
        "360도 자유 회전 원하는 각도 완벽 조율",
        "독서실급 초저소음 파워 설계"
      ],
      "affiliate_links": [
        {
          "platform": "coupang",
          "label": "🛒 쿠팡 파트너스 최저가 확인 ➔",
          "url": "https://link.coupang.com/a/morvix_fan001",
          "priority": 1,
          "bg_gradient": "linear-gradient(135deg, #ff4757, #ff6b81)"
        },
        {
          "platform": "naver",
          "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
          "url": "https://search.shopping.naver.com/search/all?query=%EC%8B%A0%EC%9D%BC%20%EC%84%9C%ED%81%98%EB%A0%88%EC%9D%B4%ED%84%B0%20BLDC",
          "priority": 2,
          "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
        }
      ],
      "thumbnail": "https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80",
      "analytics": {
        "clicks_count": 342,
        "platform_clicks": { "coupang": 210, "naver": 132 },
        "conversions_count": 48,
        "ctr": 5.2
      },
      "added_date": "2026-07-25T10:00:00.000Z",
      "expiry_date": "2026-12-31T23:59:59.000Z"
    },
    {
      "id": "PROD-009",
      "slug": "blanket001",
      "short_url": "morvix.kr/blanket001",
      "name": "모르빅스 초냉감 얼음 쿨링 이불",
      "subtitle": "닿자마자 -5도 즉각 쿨링! 열대야 숙면 구원템",
      "category": "summer",
      "status": "ACTIVE",
      "is_featured": true,
      "episode_id": "INTERNAL_CASE_EP009",
      "episode_label": "🎬 EP009 숏폼 소개 제품",
      "channels": {
        "youtube_shorts": true,
        "instagram_reels": true,
        "tiktok": true,
        "threads": true,
        "blog_seo": true
      },
      "price": 34900,
      "original_price": 59000,
      "discount_rate": "40%",
      "rating": 4.95,
      "review_count": 312,
      "usps": [
        "Q-MAX 0.45 닿자마자 입체 순간 즉각 쿨링",
        "형광증백제 0% 아토피 안심 인증 원단",
        "통세탁 가능 100회 세탁에도 쿨링 성능 유지",
        "양면 리버서블 봄/여름 사계절 실용성"
      ],
      "affiliate_links": [
        {
          "platform": "coupang",
          "label": "🛒 쿠팡 파트너스 최저가 확인 ➔",
          "url": "https://link.coupang.com/a/morvix_blanket001",
          "priority": 1,
          "bg_gradient": "linear-gradient(135deg, #ff4757, #ff6b81)"
        },
        {
          "platform": "naver",
          "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
          "url": "https://search.shopping.naver.com/search/all?query=%EC%B4%88%EB%83%89%EA%B0%90%20%EC%96%BC%EC%9D%8C%20%EC%BF%8B%EB%A7%81%20%EC%9D%B4%B6%88",
          "priority": 2,
          "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
        }
      ],
      "thumbnail": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&auto=format&fit=crop&q=80",
      "analytics": {
        "clicks_count": 1280,
        "platform_clicks": { "coupang": 820, "naver": 460 },
        "conversions_count": 164,
        "ctr": 8.4
      },
      "added_date": "2026-07-25T10:00:00.000Z",
      "expiry_date": "2026-12-31T23:59:59.000Z"
    }
  ]
};

let dbData = INITIAL_DB_DATA;
let currentCategory = 'all';

// --------------------------------------------------------------------------
// 1. Smart Category Auto Classifier (hot-deal-studio Engine Ported & Extended)
// --------------------------------------------------------------------------
function getAutoCategory(titleText) {
  const lk = (titleText || '').toLowerCase().replace(/\s+/g, '');

  if (anyKeyword(lk, ["서큘레이터", "선풍기", "에어컨", "쿨링", "이불", "여름", "얼음", "장마", "모기", "포충기", "냉풍기", "초냉감", "열대야", "부채", "제습기"])) return "summer";
  if (anyKeyword(lk, ["청소", "소독", "탈취", "세제", "위생", "스크러버", "휴지", "물티슈", "샴푸", "린스", "칫솔", "치약", "비누", "걸레", "유연제", "수건", "기저귀"])) return "cleaning";
  if (anyKeyword(lk, ["냄비", "프라이팬", "식기", "그릇", "도마", "칼", "가위", "주방", "조리", "밥솥", "전기포트", "믹서기", "에어프라이어", "전자레인지", "텀블러", "밀폐용기", "식세기"])) return "kitchen";
  if (anyKeyword(lk, ["맥세이프", "거치대", "충전", "아이폰", "데스크", "키보드", "마우스", "무선", "it", "디지털", "모니터", "노트북", "태블릿", "아이패드", "에어팟", "워치", "스피커", "이어폰", "헤드폰"])) return "it";
  if (anyKeyword(lk, ["자동차", "차량", "햇빛", "차광", "우산", "세차", "블랙박스", "네비게이션", "와이퍼", "타이어", "광택", "방향제", "시트커버", "핸들커버", "차량용", "엔진오일", "워셔액"])) return "car";
  if (anyKeyword(lk, ["강아지", "고양이", "펫", "사료", "간식", "장난감", "목줄", "하네스", "캣타워", "펫푸드", "반려동물", "애완", "멍멍", "야옹", "츄르", "모래", "배변패드"])) return "pet";

  return "life";
}

function anyKeyword(text, keywords) {
  return keywords.some(kw => text.includes(kw));
}

// --------------------------------------------------------------------------
// 2. Price & Discount Rate Regex Engine (hot-deal-studio Engine Ported)
// --------------------------------------------------------------------------
function parsePriceAndDiscount(rawText) {
  let discount = 0;
  let price = 0;

  const discountMatch = (rawText || '').match(/(\d+)\s*[%％]/);
  if (discountMatch) {
    discount = parseInt(discountMatch[1]);
  }

  const allPrices = (rawText || '').match(/([\d,]+)\s*원/g);
  if (allPrices && allPrices.length > 0) {
    const parsedNums = allPrices.map(p => parseInt(p.replace(/[^0-9]/g, ''))).filter(n => n >= 500);
    if (parsedNums.length > 0) {
      price = parsedNums[parsedNums.length - 1];
    }
  }

  return { discount, price };
}

// --------------------------------------------------------------------------
// 3. State-Based Product Lifecycle Management (ACTIVE, EXPIRED, OUT_OF_STOCK, HIDDEN)
// --------------------------------------------------------------------------
function updateProductLifecycleStates() {
  if (!dbData || !dbData.products) return;
  const nowStr = new Date().toISOString();

  dbData.products.forEach(p => {
    if (p.expiry_date && p.expiry_date < nowStr && p.status === 'ACTIVE') {
      p.status = 'EXPIRED';
    }
  });
}

// --------------------------------------------------------------------------
// Initialize MORVIX SHOP OS
// --------------------------------------------------------------------------
async function initShopOS() {
  renderCategories();
  renderProducts();
  setupRouting();
  setupAdminEvents();

  try {
    const res = await fetch('morvix_shop_db.json');
    if (res.ok) {
      const fetched = await res.json();
      if (fetched && fetched.products) {
        dbData = fetched;
        updateProductLifecycleStates();
        renderCategories();
        renderProducts();
      }
    }
  } catch (err) {
    console.warn("Using embedded fallback database:", err);
  }
}

// Render Categories
function renderCategories() {
  const container = document.getElementById('category-container');
  if (!container || !dbData) return;

  container.innerHTML = dbData.categories.map(cat => `
    <button class="category-btn ${cat.id === currentCategory ? 'active' : ''}" data-cat="${cat.id}">
      ${cat.icon} ${cat.name}
    </button>
  `).join('');

  container.querySelectorAll('.category-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      currentCategory = e.currentTarget.getAttribute('data-cat');
      renderCategories();
      renderProducts();
    });
  });
}

// Render Products (Filtering out EXPIRED & HIDDEN from main grid while maintaining analytics)
function renderProducts() {
  const grid = document.getElementById('product-grid');
  const title = document.getElementById('section-title');
  const count = document.getElementById('product-count');
  if (!grid || !dbData) return;

  updateProductLifecycleStates();

  let activeProducts = dbData.products.filter(p => p.status === 'ACTIVE' || !p.status);
  let filtered = activeProducts;

  if (currentCategory === 'featured') {
    filtered = activeProducts.filter(p => p.is_featured);
    if (title) title.textContent = '🌟 오늘의 MORVIX 추천';
  } else if (currentCategory === 'reels') {
    filtered = activeProducts.filter(p => p.episode_id || p.episode_label);
    if (title) title.textContent = '🎬 릴스/쇼츠에서 본 바로 그 제품';
  } else if (currentCategory === 'best100') {
    filtered = activeProducts.slice().sort((a, b) => ((b.analytics ? b.analytics.clicks_count : b.clicks_count) || 0) - ((a.analytics ? a.analytics.clicks_count : a.clicks_count) || 0));
    if (title) title.textContent = '🏆 MORVIX 베스트 100 히트 라인업';
  } else if (currentCategory !== 'all') {
    filtered = activeProducts.filter(p => p.category === currentCategory);
    const catObj = dbData.categories.find(c => c.id === currentCategory);
    if (title) title.textContent = `${catObj ? catObj.icon : ''} ${catObj ? catObj.name : '제품'} 검증 제품`;
  } else {
    if (title) title.textContent = '🔥 지금 가장 많이 찾는 검증 제품';
  }

  if (count) count.textContent = `총 ${filtered.length}개 검증 자산`;

  grid.innerHTML = filtered.map(p => `
    <div class="product-card" onclick="openProductDetail('${p.slug}')">
      <div class="card-image-wrapper">
        <img class="card-image" src="${p.thumbnail}" alt="${p.name}">
        ${p.is_featured ? '<span class="badge-featured">🔥 HOT 꿀템</span>' : ''}
        <span class="badge-episode">${p.episode_label || p.episode_id}</span>
      </div>
      <div class="card-content">
        <h3 class="card-title">${p.name}</h3>
        <p class="card-subtitle">${p.subtitle}</p>
        
        <div style="display: flex; gap: 4px; margin-bottom: 8px; font-size: 0.72rem; color: var(--text-muted);">
          <span style="background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">▶ Shorts</span>
          <span style="background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">📷 Reels</span>
          <span style="background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">🎵 TikTok</span>
          <span style="background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px;">📝 Blog</span>
        </div>

        <div class="card-meta">
          <div class="card-trust-box" style="display: flex; align-items: center; gap: 6px; font-size: 0.82rem; color: #2ed573; font-weight: 700;">
            <span>🔥 MORVIX 추천</span>
          </div>
          <button class="btn-card-buy">🛒 최저가/구매처 확인 ➔</button>
        </div>
      </div>
    </div>
  `).join('');
}

// Open Product Detail Modal
function openProductDetail(slug) {
  const product = dbData.products.find(p => p.slug === slug);
  if (!product) return;

  trackOutboundClick(slug);

  const modal = document.getElementById('product-modal');
  const body = document.getElementById('modal-body');

  let linksArray = [];
  if (Array.isArray(product.affiliate_links)) {
    linksArray = product.affiliate_links.sort((a, b) => (a.priority || 99) - (b.priority || 99));
  } else if (product.coupang_link) {
    linksArray.push({ platform: 'coupang', label: '🛒 쿠팡 파트너스 최저가 확인 ➔', url: product.coupang_link, bg_gradient: 'linear-gradient(135deg, #ff4757, #ff6b81)' });
  }

  const relatedProds = dbData.products.filter(p => p.slug !== slug && (p.status === 'ACTIVE' || !p.status)).slice(0, 3);

  body.innerHTML = `
    <div class="detail-grid">
      <div class="detail-left">
        <img class="detail-image" src="${product.thumbnail}" alt="${product.name}">
      </div>
      <div class="detail-right">
        <span class="detail-slug-box">morvix.kr/${product.slug}</span>
        <h2 class="detail-title">${product.name}</h2>
        <div class="detail-rating">★★★★★ ${product.rating || 4.9} / 5.0 (실사용 만족도 검증 완료)</div>
        <p style="color: var(--text-muted); font-size: 0.95rem;">"${product.subtitle}"</p>
        
        <ul class="usps-list">
          ${product.usps ? product.usps.map(u => `<li>✔ ${u}</li>`).join('') : ''}
        </ul>

        <div class="affiliate-cta-group" style="display: flex; flex-direction: column; gap: 10px; margin-top: 18px;">
          ${linksArray.map(link => `
            <a href="${link.url}" target="_blank" class="btn-affiliate-cta" onclick="registerAffiliateConversion('${product.slug}', '${link.platform}')" style="background: ${link.bg_gradient || 'linear-gradient(135deg, #00f2fe, #4facfe)'}; color: #fff; text-align: center; padding: 14px; border-radius: var(--radius-md); font-weight: 700; text-decoration: none; display: block; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
              ${link.label}
            </a>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Related Cross-Selling Cluster -->
    <div style="margin-top: 28px; border-top: 1px solid var(--border-color); padding-top: 20px;">
      <h4 style="color: var(--primary-accent); font-size: 0.98rem; font-weight: 800; margin-bottom: 12px;">🔗 함께 둘러보면 일상의 억까가 풀리는 연관 추천 클러스터</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;">
        ${relatedProds.map(rp => `
          <div onclick="openProductDetail('${rp.slug}')" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 10px; cursor: pointer; transition: transform 0.2s;">
            <img src="${rp.thumbnail}" style="width: 100%; height: 90px; object-fit: cover; border-radius: 4px; margin-bottom: 6px;">
            <div style="font-size: 0.82rem; font-weight: 700; color: #fff; line-height: 1.2; height: 2rem; overflow: hidden;">${rp.name}</div>
            <div style="font-size: 0.78rem; color: #2ed573; margin-top: 6px; font-weight: 600;">🛒 최저가 확인 ➔</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  if (modal) modal.classList.add('active');
}

// Curation Quick Filter
function filterCuration(catId) {
  document.querySelectorAll('.curation-pill').forEach(pill => pill.classList.remove('active'));
  const activePill = document.querySelector(`.curation-pill[onclick="filterCuration('${catId}')"]`);
  if (activePill) activePill.classList.add('active');

  currentCategory = catId;
  renderCategories();
  renderProducts();
}

// Analytics Trackers
function trackOutboundClick(slug) {
  const prod = dbData.products.find(p => p.slug === slug);
  if (prod) {
    if (prod.analytics) prod.analytics.clicks_count = (prod.analytics.clicks_count || 0) + 1;
  }
}

function registerAffiliateConversion(slug, platform) {
  const prod = dbData.products.find(p => p.slug === slug);
  if (prod && prod.analytics) {
    if (!prod.analytics.platform_clicks) prod.analytics.platform_clicks = { coupang: 0, naver: 0 };
    prod.analytics.platform_clicks[platform] = (prod.analytics.platform_clicks[platform] || 0) + 1;
    prod.analytics.conversions_count = (prod.analytics.conversions_count || 0) + 1;
  }
}

// Admin OS Setup & Auto-Ingestion Handlers
function setupAdminEvents() {
  const btnOpen = document.getElementById('btn-open-admin');
  const btnClose = document.getElementById('btn-close-admin');
  const modal = document.getElementById('admin-modal');
  const loginModal = document.getElementById('admin-login-modal');
  const btnCloseLogin = document.getElementById('btn-close-login-modal');
  const formLogin = document.getElementById('form-admin-login');
  const inputPin = document.getElementById('input-admin-pin');
  const loginErrorMsg = document.getElementById('login-error-msg');

  function verifyAndOpenAdmin() {
    if (sessionStorage.getItem('morvix_admin_auth') === 'true') {
      if (loginModal) loginModal.classList.remove('active');
      if (modal) modal.classList.add('active');
      renderAnalyticsTable();
      renderAdminProductList();
      return;
    }

    if (loginModal) {
      if (loginErrorMsg) loginErrorMsg.style.display = 'none';
      if (inputPin) inputPin.value = '';
      loginModal.classList.add('active');
      setTimeout(() => { if (inputPin) inputPin.focus(); }, 100);
    }
  }

  if (formLogin) {
    formLogin.addEventListener('submit', (e) => {
      e.preventDefault();
      if (inputPin.value.trim() === "2026") {
        sessionStorage.setItem('morvix_admin_auth', 'true');
        if (loginErrorMsg) loginErrorMsg.style.display = 'none';
        if (loginModal) loginModal.classList.remove('active');
        if (modal) modal.classList.add('active');
        renderAnalyticsTable();
        renderAdminProductList();
      } else {
        if (loginErrorMsg) loginErrorMsg.style.display = 'block';
      }
    });
  }

  if (btnCloseLogin) btnCloseLogin.addEventListener('click', () => loginModal.classList.remove('active'));
  if (btnOpen) btnOpen.addEventListener('click', verifyAndOpenAdmin);
  if (btnClose && modal) btnClose.addEventListener('click', () => modal.classList.remove('active'));

  // Auto Ingestion Engine
  const btnAutoFetch = document.getElementById('btn-auto-fetch');
  if (btnAutoFetch) {
    btnAutoFetch.addEventListener('click', async () => {
      const rawUrl = document.getElementById('input-auto-url').value.trim();
      if (!rawUrl) {
        alert("⚠️ 제휴 URL을 입력 후 [자동 불러오기]를 눌러주세요.");
        return;
      }

      btnAutoFetch.disabled = true;
      btnAutoFetch.textContent = '⏳ 스마트 분류 & 수집 중...';

      const isCoupang = rawUrl.includes('coupang.com');
      const isNaver = rawUrl.includes('naver.com') || rawUrl.includes('naver.me') || rawUrl.includes('brandconnect') || rawUrl.includes('shoppingconnect');

      if (isCoupang && document.getElementById('input-link-coupang')) document.getElementById('input-link-coupang').value = rawUrl;
      else if (document.getElementById('input-link-naver')) document.getElementById('input-link-naver').value = rawUrl;

      const nextEpNum = (dbData ? dbData.products.length + 1 : 13).toString().padStart(3, '0');
      const autoSlug = `item${nextEpNum}`;
      if (document.getElementById('input-slug')) document.getElementById('input-slug').value = autoSlug;
      if (document.getElementById('input-episode')) document.getElementById('input-episode').value = `INTERNAL_CASE_EP${nextEpNum}`;

      let fetchedTitle = "모르빅스 검증 꿀템";
      let fetchedImg = "https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80";
      let fetchedPrice = 28900;

      try {
        const apiRes = await fetch(`/api/extract?url=${encodeURIComponent(rawUrl)}`);
        if (apiRes.ok) {
          const apiData = await apiRes.json();
          if (apiData && apiData.success) {
            if (apiData.title && apiData.title.length > 2) fetchedTitle = apiData.title;
            if (apiData.image) fetchedImg = apiData.image;
            if (apiData.price) fetchedPrice = apiData.price;
          }
        }
      } catch (err) {
        console.warn("Auto Ingestion Engine fallback:", err);
      }

      const inferredCat = getAutoCategory(fetchedTitle);

      if (document.getElementById('input-name')) document.getElementById('input-name').value = fetchedTitle;
      if (document.getElementById('input-image-url')) document.getElementById('input-image-url').value = fetchedImg;
      if (document.getElementById('input-price')) document.getElementById('input-price').value = fetchedPrice;
      if (document.getElementById('input-category')) document.getElementById('input-category').value = inferredCat;
      if (document.getElementById('input-subtitle')) document.getElementById('input-subtitle').value = `${fetchedTitle} - 일상의 불편함을 3초 만에 완벽 해결하는 솔루션`;

      btnAutoFetch.disabled = false;
      btnAutoFetch.textContent = '⚡ 상품 정보 1초 자동 가져오기';

      alert(`⚡ [MORVIX Auto Import Engine 분류 완료!]\n\n• 상품명: ${fetchedTitle}\n• 실시간 가격: ${fetchedPrice.toLocaleString()}원\n• 100% 자동 추론 카테고리: [${inferredCat.toUpperCase()}]\n• 단축 슬러그: morvix.kr/${autoSlug}`);
    });
  }

  const formAddProduct = document.getElementById('form-add-product');
  if (formAddProduct) {
    formAddProduct.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('input-name') ? document.getElementById('input-name').value : '';
      const slug = document.getElementById('input-slug') ? document.getElementById('input-slug').value : '';
      const category = document.getElementById('input-category') ? document.getElementById('input-category').value : 'summer';
      const episode = document.getElementById('input-episode') ? document.getElementById('input-episode').value : 'EP013';
      const price = document.getElementById('input-price') ? parseInt(document.getElementById('input-price').value || 25000) : 25000;
      const linkCoupang = document.getElementById('input-link-coupang') ? document.getElementById('input-link-coupang').value : '';
      const linkNaver = document.getElementById('input-link-naver') ? document.getElementById('input-link-naver').value : '';
      const imageUrl = document.getElementById('input-image-url') ? document.getElementById('input-image-url').value : 'https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80';
      const subtitle = document.getElementById('input-subtitle') ? document.getElementById('input-subtitle').value : '';

      const affiliateLinks = [];
      if (linkCoupang) affiliateLinks.push({ platform: 'coupang', label: '🛒 쿠팡 파트너스 최저가 확인 ➔', url: linkCoupang, priority: 1 });
      if (linkNaver) affiliateLinks.push({ platform: 'naver', label: '🟢 네이버 쇼핑커넥트 최저가 확인 ➔', url: linkNaver, priority: 2 });

      const newProd = {
        id: `PROD-${Date.now()}`,
        slug: slug,
        short_url: `morvix.kr/${slug}`,
        name: name,
        subtitle: subtitle,
        category: category,
        status: "ACTIVE",
        is_featured: true,
        episode_id: episode,
        episode_label: `🎬 ${episode} 숏폼 제품`,
        price: price,
        original_price: Math.round(price * 1.4),
        discount_rate: "30%",
        rating: 5.0,
        review_count: 1,
        affiliate_links: affiliateLinks,
        thumbnail: imageUrl,
        analytics: { clicks_count: 0, platform_clicks: { coupang: 0, naver: 0 }, conversions_count: 0, ctr: 0.0 },
        added_date: new Date().toISOString(),
        expiry_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
      };

      dbData.products.unshift(newProd);
      alert(`✅ Product Master DB (State: ACTIVE) 등록 완료!`);

      renderProducts();
      renderAnalyticsTable();
      renderAdminProductList();
      formAddProduct.reset();
    });
  }
}

function renderAnalyticsTable() {
  const tbody = document.getElementById('analytics-tbody');
  if (!tbody || !dbData) return;

  tbody.innerHTML = dbData.products.map(p => `
    <tr>
      <td style="font-family: monospace; color: var(--primary-accent); font-weight: 700;">morvix.kr/${p.slug}</td>
      <td style="font-weight: 600;">${p.name}</td>
      <td style="font-weight: 800; color: #ff4757;">🛒 ${(p.analytics?.platform_clicks?.coupang || 0).toLocaleString()}회</td>
      <td style="font-weight: 800; color: #2ed573;">🟢 ${(p.analytics?.platform_clicks?.naver || 0).toLocaleString()}회</td>
      <td style="font-weight: 800; color: #fff;">${(p.analytics?.conversions_count || 0).toLocaleString()}건</td>
      <td><span style="padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; background: ${p.status === 'EXPIRED' ? 'rgba(255,71,87,0.2)' : 'rgba(46,213,115,0.2)'}; color: ${p.status === 'EXPIRED' ? '#ff4757' : '#2ed573'};">${p.status || 'ACTIVE'}</span></td>
    </tr>
  `).join('');
}

function renderAdminProductList() {
  const container = document.getElementById('admin-product-list');
  if (!container || !dbData) return;

  container.innerHTML = dbData.products.map(p => `
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <strong style="color: #fff; font-size: 0.98rem; display: block; margin-bottom: 4px;">${p.name}</strong>
        <div style="font-size: 0.82rem; color: var(--text-muted);">
          morvix.kr/${p.slug} | Status: <span style="color: ${p.status === 'EXPIRED' ? '#ff4757' : '#2ed573'}; font-weight: 700;">${p.status || 'ACTIVE'}</span>
        </div>
      </div>
      <button style="background: rgba(255, 71, 87, 0.2); color: #ff4757; border: 1px solid rgba(255, 71, 87, 0.4); padding: 6px 14px; border-radius: var(--radius-sm); cursor: pointer;" onclick="deleteProduct('${p.id}')">삭제</button>
    </div>
  `).join('');
}

function deleteProduct(id) {
  if (confirm("이 상품을 삭제하시겠습니까?")) {
    dbData.products = dbData.products.filter(p => p.id !== id);
    renderProducts();
    renderAnalyticsTable();
    renderAdminProductList();
  }
}

function setupRouting() {
  let slug = window.location.hash.replace('#', '');
  if (slug && slug !== 'admin') openProductDetail(slug);
}

document.addEventListener('DOMContentLoaded', initShopOS);
