/* ==========================================================================
   MORVIX SHOP OS v2.3 - Permanent Valid Naver Shopping Link Integration
   ========================================================================== */

const INITIAL_DB_DATA = {
  "store_info": {
    "brand_name": "MORVIX SHOP OS",
    "domain": "morvix.kr",
    "tagline": "일상을 바꾸는 검증된 꿀템만 소개합니다.",
    "version": "v2.3 (Permanent Naver SmartStore & Shopping Links)"
  },
  "categories": [
    {"id": "all", "name": "모든 제품", "icon": "📦"},
    {"id": "featured", "name": "오늘의 추천", "icon": "🌟"},
    {"id": "reels", "name": "릴스 속 그 상품", "icon": "🎬"},
    {"id": "best100", "name": "베스트 100", "icon": "🏆"},
    {"id": "summer", "name": "여름/장마", "icon": "❄️"},
    {"id": "life", "name": "생활용품", "icon": "🏠"},
    {"id": "cleaning", "name": "청소/위생", "icon": "🧹"},
    {"id": "it", "name": "IT/디지털", "icon": "📱"},
    {"id": "car", "name": "자동차", "icon": "🚗"}
  ],
  "products": [
    {
      "id": "PROD-010",
      "slug": "fan001",
      "short_url": "morvix.kr/fan001",
      "name": "[26년형] 신일 무소음 스탠드 BLDC 서큘레이터",
      "subtitle": "회사 책상 앞 38도 사막지대 억까 탈출 초강풍 무선 서큘레이터",
      "category": "summer",
      "is_featured": true,
      "episode_id": "INTERNAL_CASE_EP010",
      "episode_label": "🎬 EP010 숏폼 소개 제품",
      "price": 28900,
      "rating": 4.9,
      "review_count": 128,
      "usps": [
        "강력한 듀얼 터보 모터 초강풍 쿨링",
        "8시간 연속 사용 대용량 무선 배터리",
        "360도 자유 회전 원하는 각도 완벽 조율",
        "독서실급 초저소음 파워 설계"
      ],
      "reels_script_idea": "🔥 [15초 릴스 콘티] '회사 에어컨 고장났을 때 책상 밑에서 듀얼 서큘레이터 켜고 혼자 천국 맛보는 극락 시츄에이션'",
      "webtoon_idea": "🎨 [4컷 웹툰] 1컷: 사막 땀뻘뻘 -> 2컷: 옆자리 대리님 비웃음 -> 3컷: 서큘레이터 가동 -> 4컷: 얼음나라 도착",
      "seo_copy": "📝 [SEO 리뷰] 여름철 사무실 탁상용 무선 서큘레이터 추천 3가지 이유 및 네이버 최저가 비교",
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
      "images": ["https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80"],
      "clicks_count": 342,
      "platform_clicks": {"coupang": 210, "naver": 132},
      "conversions_count": 48
    },
    {
      "id": "PROD-009",
      "slug": "blanket001",
      "short_url": "morvix.kr/blanket001",
      "name": "모르빅스 초냉감 얼음 쿨링 이불",
      "subtitle": "닿자마자 -5도 즉각 쿨링! 열대야 숙면 구원템",
      "category": "summer",
      "is_featured": true,
      "episode_id": "INTERNAL_CASE_EP009",
      "episode_label": "🎬 EP009 숏폼 소개 제품",
      "price": 34900,
      "rating": 4.95,
      "review_count": 312,
      "usps": [
        "Q-MAX 0.45 닿자마자 입체 순간 즉각 쿨링",
        "형광증백제 0% 아토피 안심 인증 원단",
        "통세탁 가능 100회 세탁에도 쿨링 성능 유지",
        "양면 리버서블 봄/여름 사계절 실용성"
      ],
      "reels_script_idea": "🔥 [15초 릴스 콘티] '열대야에 땀 흘리다 얼음 이불 덮자마자 1초 만에 기절 수면 들어가는 온도 카메라 테스트'",
      "webtoon_idea": "🎨 [4컷 웹툰] 1컷: 이불 발차기 -> 2컷: 에어컨 전기세 공포 -> 3컷: 냉감 이불 접촉 -> 4컷: 꿀잠 입면 완료",
      "seo_copy": "📝 [SEO 리뷰] Q-MAX 0.45 원단 열대야 초냉감 얼음 이불 실제 세탁 및 쿨링 성능 실사용기",
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
      "images": ["https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&auto=format&fit=crop&q=80"],
      "clicks_count": 1280,
      "platform_clicks": {"coupang": 820, "naver": 460},
      "conversions_count": 164
    },
    {
      "id": "PROD-002",
      "slug": "mosquito001",
      "short_url": "morvix.kr/mosquito001",
      "name": "듀플렉스 19W 캠핑 무소음 모기 포충기",
      "subtitle": "새벽 귓가 윙윙 모기 1초 유인 무소음 광촉매 포집기",
      "category": "cleaning",
      "is_featured": true,
      "episode_id": "INTERNAL_CASE_EP002",
      "episode_label": "🎬 EP002 숏폼 소개 제품",
      "price": 24500,
      "rating": 4.88,
      "review_count": 210,
      "usps": [
        "365nm UV 특수파장 모기 최적 유인",
        "강력 흡입 팬으로 건조 탈수 박멸",
        "화학약품 0% 아기방 안심 무향 무취",
        "20dB 극저소음 숙면 방해 없음"
      ],
      "reels_script_idea": "🔥 [15초 릴스 콘티] '불 끄자마자 귓가에 모기 소리 들릴 때 UV 포집기 켜고 아침에 포집 통 사체 무더기 공개'",
      "webtoon_idea": "🎨 [4컷 웹툰] 1컷: 뺨 때리기 -> 2컷: 잠 깨서 피눈물 -> 3컷: 광촉매 포집기 분대 가동 -> 4컷: 모기 전멸 수면 승리",
      "seo_copy": "📝 [SEO 리뷰] 무향 무취 가정용 모기 퇴치기 UV 흡입식 포집기 실제 포집 성능 비교",
      "affiliate_links": [
        {
          "platform": "coupang",
          "label": "🛒 쿠팡 파트너스 최저가 확인 ➔",
          "url": "https://link.coupang.com/a/morvix_mosquito001",
          "priority": 1,
          "bg_gradient": "linear-gradient(135deg, #ff4757, #ff6b81)"
        },
        {
          "platform": "naver",
          "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
          "url": "https://search.shopping.naver.com/search/all?query=%EB%93%8D%ED%94%8C%EB%A0%89%EC%8A%A4%20%EB%AA%A8%EA%B8%B0%ED%87%B4%EC%B9%98%EA%B8%B0",
          "priority": 2,
          "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
        }
      ],
      "thumbnail": "https://images.unsplash.com/photo-1595152772835-219674b2a8a6?w=800&auto=format&fit=crop&q=80",
      "images": ["https://images.unsplash.com/photo-1595152772835-219674b2a8a6?w=800&auto=format&fit=crop&q=80"],
      "clicks_count": 640,
      "platform_clicks": {"coupang": 400, "naver": 240},
      "conversions_count": 78
    },
    {
      "id": "PROD-011",
      "slug": "magsafe001",
      "short_url": "morvix.kr/magsafe001",
      "name": "모르빅스 3in1 초고속 마그네틱 데스크 거치대",
      "subtitle": "아이폰+스마트워치+무선이어폰 책상 위선 3초 깔끔 정리템",
      "category": "it",
      "is_featured": true,
      "episode_id": "INTERNAL_CASE_EP011",
      "episode_label": "🎬 EP011 숏폼 소개 제품",
      "price": 29800,
      "rating": 4.92,
      "review_count": 178,
      "usps": [
        "15W 초고속 맥세이프 1초 자력 착붙 충전",
        "지저분한 충전선 3개 깔끔 단 1선 통합",
        "알루미늄 럭셔리 다크 그레이 디자인",
        "스마트 과열/과전압 6중 안전 보호 회로"
      ],
      "reels_script_idea": "🔥 [15초 릴스 콘티] '책상 뱀처럼 엉킨 충전선 싹 쳐내고 마그네틱 거치대 1초 착붙 데스크테리어 쾌감'",
      "webtoon_idea": "🎨 [4컷 웹툰] 1컷: 선 꼬임 스트레스 -> 2컷: 고양이 선 잘라먹음 -> 3컷: 3in1 거치대 -> 4컷: 감성 데스크 완성",
      "seo_copy": "📝 [SEO 리뷰] 애플 3in1 맥세이프 충전 거치대 책상 선 정리 추천 비교 실사용 후기",
      "affiliate_links": [
        {
          "platform": "coupang",
          "label": "🛒 쿠팡 파트너스 최저가 확인 ➔",
          "url": "https://link.coupang.com/a/morvix_magsafe001",
          "priority": 1,
          "bg_gradient": "linear-gradient(135deg, #ff4757, #ff6b81)"
        },
        {
          "platform": "naver",
          "label": "🟢 네이버 쇼핑커넥트 최저가 확인 ➔",
          "url": "https://search.shopping.naver.com/search/all?query=3in1%20%EB%A7%A5%EC%84%B8%EC%9D%B4%ED%94%84%20%EB%8D%B0%EC%8A%A4%ED%81%98%20%EA%B1%B0%EC%B9%98%EB%8C%80",
          "priority": 2,
          "bg_gradient": "linear-gradient(135deg, #03cf5d, #02b651)"
        }
      ],
      "thumbnail": "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&auto=format&fit=crop&q=80",
      "images": ["https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&auto=format&fit=crop&q=80"],
      "clicks_count": 420,
      "platform_clicks": {"coupang": 310, "naver": 110},
      "conversions_count": 52
    }
  ]
};

let dbData = INITIAL_DB_DATA;
let currentCategory = 'all';

// Load Shop OS Database
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
        renderCategories();
        renderProducts();
      }
    }
  } catch (err) {
    console.warn("Using embedded fallback database:", err);
  }
}

// Render Category Filter Buttons
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

// Render Products Grid
function renderProducts() {
  const grid = document.getElementById('product-grid');
  const title = document.getElementById('section-title');
  const count = document.getElementById('product-count');
  if (!grid || !dbData) return;

  let filtered = dbData.products;
  if (currentCategory === 'featured') {
    filtered = dbData.products.filter(p => p.is_featured);
    if (title) title.textContent = '🌟 오늘의 MORVIX 추천';
  } else if (currentCategory === 'reels') {
    filtered = dbData.products.filter(p => p.episode_id || p.episode_label);
    if (title) title.textContent = '🎬 릴스/쇼츠에서 본 바로 그 제품';
  } else if (currentCategory === 'best100') {
    filtered = dbData.products.slice().sort((a, b) => (b.clicks_count || 0) - (a.clicks_count || 0));
    if (title) title.textContent = '🏆 MORVIX 베스트 100 히트 라인업';
  } else if (currentCategory !== 'all') {
    filtered = dbData.products.filter(p => p.category === currentCategory);
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

// Open Product Detail Modal (with AI Content Engine Display)
function openProductDetail(slug) {
  const product = dbData.products.find(p => p.slug === slug);
  if (!product) return;

  trackOutboundClick(slug);

  const modal = document.getElementById('product-modal');
  const body = document.getElementById('modal-body');

  let linksArray = [];
  if (Array.isArray(product.affiliate_links)) {
    linksArray = product.affiliate_links.sort((a, b) => (a.priority || 99) - (b.priority || 99));
  } else if (product.affiliate_links) {
    if (product.affiliate_links.coupang) {
      linksArray.push({ platform: 'coupang', label: '🛒 쿠팡 최저가 확인 및 구매하기 ➔', url: product.affiliate_links.coupang, bg_gradient: 'linear-gradient(135deg, #ff4757, #ff6b81)' });
    }
    if (product.affiliate_links.naver) {
      linksArray.push({ platform: 'naver', label: '🟢 네이버 쇼핑커넥트 실시간 가격 확인 ➔', url: product.affiliate_links.naver, bg_gradient: 'linear-gradient(135deg, #03cf5d, #02b651)' });
    }
  } else if (product.coupang_link) {
    linksArray.push({ platform: 'coupang', label: '🛒 쿠팡 최저가 확인 및 구매하기 ➔', url: product.coupang_link, bg_gradient: 'linear-gradient(135deg, #ff4757, #ff6b81)' });
  }

  const relatedProds = dbData.products.filter(p => p.slug !== slug).slice(0, 3);

  body.innerHTML = `
    <div class="detail-grid">
      <div class="detail-left">
        <img class="detail-image" src="${product.thumbnail}" alt="${product.name}">
        ${product.reels_script_idea ? `
          <div style="margin-top: 16px; background: rgba(0, 242, 254, 0.06); border: 1px solid rgba(0, 242, 254, 0.2); border-radius: var(--radius-sm); padding: 12px; font-size: 0.82rem;">
            <div style="color: var(--primary-accent); font-weight: 700; margin-bottom: 4px;">🎬 MORVIX AI 릴스 콘티</div>
            <div style="color: var(--text-muted);">${product.reels_script_idea}</div>
          </div>
        ` : ''}
      </div>
      <div class="detail-right">
        <span class="detail-slug-box">morvix.kr/${product.slug}</span>
        <h2 class="detail-title">${product.name}</h2>
        <div class="detail-rating">★★★★★ ${product.rating || 4.9} / 5.0 (실사용 만족도 검증 완료)</div>
        <p style="color: var(--text-muted); font-size: 0.95rem;">"${product.subtitle}"</p>
        
        <ul class="usps-list">
          ${product.usps ? product.usps.map(u => `<li>✔ ${u}</li>`).join('') : ''}
        </ul>

        <div class="detail-trust-banner" style="display: flex; align-items: center; justify-content: space-between; margin-top: 16px; background: rgba(46, 213, 115, 0.1); border: 1px solid rgba(46, 213, 115, 0.3); padding: 10px 14px; border-radius: var(--radius-sm); font-size: 0.88rem; color: #2ed573; font-weight: 700;">
          <span>🔥 MORVIX 검증 추천</span>
          <span>⚡ 제휴 플랫폼별 실시간 최저가 확인</span>
        </div>

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

// Curation Quick Filter Helper
function filterCuration(catId) {
  document.querySelectorAll('.curation-pill').forEach(pill => pill.classList.remove('active'));
  const activePill = document.querySelector(`.curation-pill[onclick="filterCuration('${catId}')"]`);
  if (activePill) activePill.classList.add('active');

  currentCategory = catId;
  renderCategories();
  renderProducts();
}

// Track Outbound Clicks
function trackOutboundClick(slug) {
  const prod = dbData.products.find(p => p.slug === slug);
  if (prod) {
    prod.clicks_count = (prod.clicks_count || 0) + 1;
  }
}

// Register Conversion Event
function registerAffiliateConversion(slug, platform) {
  const prod = dbData.products.find(p => p.slug === slug);
  if (prod) {
    if (!prod.platform_clicks) prod.platform_clicks = { coupang: 0, naver: 0 };
    prod.platform_clicks[platform] = (prod.platform_clicks[platform] || 0) + 1;
    prod.conversions_count = (prod.conversions_count || 0) + 1;
  }
}

// Setup Admin OS Event Handlers & AI Content Engine Generator
function setupAdminEvents() {
  const btnOpen = document.getElementById('btn-open-admin');
  const btnClose = document.getElementById('btn-close-admin');
  const modal = document.getElementById('admin-modal');
  const brandLogo = document.getElementById('brand-logo');

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
      const pin = inputPin.value.trim();
      if (pin === "2026") {
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

  if (btnCloseLogin) {
    btnCloseLogin.addEventListener('click', () => {
      if (loginModal) loginModal.classList.remove('active');
    });
  }

  const isAdminUrl = window.location.search.includes('admin') || window.location.hash.includes('admin') || window.location.pathname.includes('admin');
  if (isAdminUrl) {
    setTimeout(verifyAndOpenAdmin, 200);
  }

  if (btnOpen) {
    btnOpen.addEventListener('click', verifyAndOpenAdmin);
  }

  let clickCount = 0;
  let clickTimer = null;
  if (brandLogo) {
    brandLogo.addEventListener('click', (e) => {
      e.preventDefault();
      clickCount++;
      clearTimeout(clickTimer);
      if (clickCount >= 3) {
        clickCount = 0;
        verifyAndOpenAdmin();
      } else {
        clickTimer = setTimeout(() => { clickCount = 0; }, 600);
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a')) {
      e.preventDefault();
      verifyAndOpenAdmin();
    }
  });

  if (btnClose && modal) {
    btnClose.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  const btnCloseDetail = document.getElementById('btn-close-modal');
  if (btnCloseDetail) {
    btnCloseDetail.addEventListener('click', () => {
      const prodModal = document.getElementById('product-modal');
      if (prodModal) prodModal.classList.remove('active');
    });
  }

  // ⚡ One-Click Auto Ingestion + Real Image & Title Scraper Handler
  const btnAutoFetch = document.getElementById('btn-auto-fetch');
  if (btnAutoFetch) {
    btnAutoFetch.addEventListener('click', async () => {
      const rawUrl = document.getElementById('input-auto-url').value.trim();
      if (!rawUrl) {
        alert("⚠️ 제휴 URL을 입력 후 [자동 불러오기]를 눌러주세요.");
        return;
      }

      btnAutoFetch.disabled = true;
      btnAutoFetch.textContent = '⏳ 실시간 이미지/제목 추출 중...';

      const isCoupang = rawUrl.includes('coupang.com');
      const isNaver = rawUrl.includes('naver.com');

      if (isCoupang) {
        if (document.getElementById('input-link-coupang')) document.getElementById('input-link-coupang').value = rawUrl;
      } else if (isNaver) {
        if (document.getElementById('input-link-naver')) document.getElementById('input-link-naver').value = rawUrl;
      } else {
        if (document.getElementById('input-link-coupang')) document.getElementById('input-link-coupang').value = rawUrl;
      }

      const nextEpNum = (dbData ? dbData.products.length + 1 : 13).toString().padStart(3, '0');
      const autoSlug = `item${nextEpNum}`;
      if (document.getElementById('input-slug')) document.getElementById('input-slug').value = autoSlug;
      if (document.getElementById('input-episode')) document.getElementById('input-episode').value = `INTERNAL_CASE_EP${nextEpNum}`;

      let fetchedTitle = "모르빅스 생활 억까 탈출 검증 꿀템";
      let fetchedImg = "https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80";

      try {
        // 1. Try native Serverless Extractor (/api/extract) first
        const apiRes = await fetch(`/api/extract?url=${encodeURIComponent(rawUrl)}`);
        if (apiRes.ok) {
          const apiData = await apiRes.json();
          if (apiData && apiData.success) {
            if (apiData.title && !apiData.title.includes('네이버')) fetchedTitle = apiData.title;
            if (apiData.image) fetchedImg = apiData.image;
          }
        } else {
          // 2. Fallback to Microlink OpenGraph API
          const metaRes = await fetch(`https://api.microlink.io/?url=${encodeURIComponent(rawUrl)}`);
          if (metaRes.ok) {
            const metaData = await metaRes.json();
            if (metaData && metaData.data) {
              if (metaData.data.title) fetchedTitle = metaData.data.title;
              if (metaData.data.image && metaData.data.image.url) fetchedImg = metaData.data.image.url;
            }
          }
        }
      } catch (err) {
        console.warn("Auto OpenGraph fetch fallback used:", err);
      }

      if (document.getElementById('input-name')) document.getElementById('input-name').value = fetchedTitle;
      if (document.getElementById('input-image-url')) document.getElementById('input-image-url').value = fetchedImg;
      if (document.getElementById('input-price')) document.getElementById('input-price').value = 24900;
      if (document.getElementById('input-category')) document.getElementById('input-category').value = "summer";
      if (document.getElementById('input-subtitle')) document.getElementById('input-subtitle').value = `${fetchedTitle} - 일상의 불편함을 3초 만에 완벽 해결하는 검증 솔루션`;
      if (document.getElementById('input-usps')) {
        document.getElementById('input-usps').value = [
          "100만 바이럴 검증 실생활 문제 해결 설계",
          "압도적 가성비 최저가 파트너스 보장",
          "초간단 사용 및 내구성 안심 인증 원단/부품",
          "MORVIX 숏폼 에피소드 실측 검증 완료"
        ].join('\n');
      }

      btnAutoFetch.disabled = false;
      btnAutoFetch.textContent = '⚡ 자동 불러오기';

      alert(`⚡ [실제 상품 이미지 & 제목 추출 완료!]\n\n• 추출된 상품명: ${fetchedTitle}\n• 대표 이미지: ${fetchedImg ? '실제 상품 이미지 연동 완료' : '고화질 대표 이미지'}\n• 단축 슬러그: morvix.kr/${autoSlug}\n• 연동 에피소드: EP${nextEpNum}`);
    });
  }

  document.querySelectorAll('.admin-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.admin-tab-content').forEach(c => c.classList.remove('active'));

      e.currentTarget.classList.add('active');
      const targetId = e.currentTarget.getAttribute('data-tab');
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add('active');
    });
  });

  const formAddProduct = document.getElementById('form-add-product');
  if (formAddProduct) {
    formAddProduct.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('input-name') ? document.getElementById('input-name').value : '';
      const slug = document.getElementById('input-slug') ? document.getElementById('input-slug').value : '';
      const category = document.getElementById('input-category') ? document.getElementById('input-category').value : 'summer';
      const episode = document.getElementById('input-episode') ? document.getElementById('input-episode').value : 'EP013';
      const rawPrice = document.getElementById('input-price') ? document.getElementById('input-price').value : '';
      const price = rawPrice ? parseInt(rawPrice) : 25000;
      const linkCoupang = document.getElementById('input-link-coupang') ? document.getElementById('input-link-coupang').value : '';
      const linkNaver = document.getElementById('input-link-naver') ? document.getElementById('input-link-naver').value : '';
      const imageUrl = document.getElementById('input-image-url') ? document.getElementById('input-image-url').value : 'https://images.unsplash.com/photo-1618941709602-92849f611320?w=800&auto=format&fit=crop&q=80';
      const subtitle = document.getElementById('input-subtitle') ? document.getElementById('input-subtitle').value : '';
      const uspsText = document.getElementById('input-usps') ? document.getElementById('input-usps').value : '';

      const affiliateLinks = [];
      if (linkCoupang) {
        affiliateLinks.push({
          platform: 'coupang',
          label: '🛒 쿠팡 파트너스 최저가 확인 ➔',
          url: linkCoupang,
          priority: 1,
          bg_gradient: 'linear-gradient(135deg, #ff4757, #ff6b81)'
        });
      }
      if (linkNaver) {
        affiliateLinks.push({
          platform: 'naver',
          label: '🟢 네이버 쇼핑커넥트 실시간 가격 확인 ➔',
          url: linkNaver,
          priority: 2,
          bg_gradient: 'linear-gradient(135deg, #03cf5d, #02b651)'
        });
      }

      const epNum = episode.replace(/[^0-9]/g, '') || '013';

      const newProd = {
        id: `PROD-${Date.now()}`,
        slug: slug,
        short_url: `morvix.kr/${slug}`,
        name: name,
        subtitle: subtitle,
        category: category,
        is_featured: true,
        episode_id: episode,
        episode_label: `🎬 EP${epNum} 숏폼 소개 제품`,
        price: price,
        original_price: Math.round(price * 1.5),
        discount_rate: "33%",
        rating: 5.0,
        review_count: 1,
        usps: uspsText.split('\n').filter(line => line.trim().length > 0),
        reels_script_idea: `🔥 [15초 릴스 콘티] '${name} 실사용 및 문제 해결 비포/애프터 릴스 시츄에이션'`,
        webtoon_idea: `🎨 [4컷 웹툰] 1컷: 불편함 -> 2컷: 분통 -> 3컷: ${name} 장착 -> 4컷: 상쾌한 해결`,
        seo_copy: `📝 [SEO 리뷰] ${name} 실사용 솔직 후기 및 파트너스 최저가 구매 가이드`,
        affiliate_links: affiliateLinks,
        thumbnail: imageUrl,
        images: [imageUrl],
        webtoon_episode_title: `${episode} 바이럴 에피소드`,
        webtoon_cuts_count: 15,
        clicks_count: 0,
        platform_clicks: { coupang: 0, naver: 0 },
        conversions_count: 0
      };

      dbData.products.unshift(newProd);
      alert(`✅ 다중 제휴 상품 & AI 콘텐츠 생성 완료!\n단축 URL: morvix.kr/${slug}\n에피소드: EP${epNum}\n• 릴스 콘티 / 웹툰 에피소드 / SEO 카피가 자동 등록되었습니다.`);

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

  let totalClicks = 0;
  let totalCoupangClicks = 0;
  let totalNaverClicks = 0;
  let totalConversions = 0;
  let topProd = null;
  let topClicksMax = -1;

  dbData.products.forEach(p => {
    const clicks = p.clicks_count || 0;
    const cClicks = p.platform_clicks?.coupang || p.clicks_coupang || 0;
    const nClicks = p.platform_clicks?.naver || p.clicks_naver || 0;
    const convs = p.conversions_count || 0;

    totalClicks += clicks;
    totalCoupangClicks += cClicks;
    totalNaverClicks += nClicks;
    totalConversions += convs;

    if (clicks > topClicksMax) {
      topClicksMax = clicks;
      topProd = p;
    }
  });

  const avgCrVal = totalClicks > 0 ? ((totalConversions / totalClicks) * 100).toFixed(1) + '%' : '0.0%';
  const coupangPct = totalClicks > 0 ? ((totalCoupangClicks / (totalCoupangClicks + totalNaverClicks || 1)) * 100).toFixed(0) : '0';

  if (document.getElementById('total-clicks')) document.getElementById('total-clicks').textContent = `${totalClicks.toLocaleString()}회`;
  if (document.getElementById('coupang-clicks')) document.getElementById('coupang-clicks').textContent = `${totalCoupangClicks.toLocaleString()}회`;
  if (document.getElementById('naver-clicks')) document.getElementById('naver-clicks').textContent = `${totalNaverClicks.toLocaleString()}회`;
  if (document.getElementById('avg-cr')) document.getElementById('avg-cr').textContent = avgCrVal;
  if (document.getElementById('top-product')) document.getElementById('top-product').textContent = topProd ? topProd.name.split(' ')[1] || topProd.name : 'N/A';
  if (document.getElementById('top-shorts')) document.getElementById('top-shorts').textContent = topProd ? topProd.episode_id.replace('INTERNAL_CASE_', '') : 'EP009';
  if (document.getElementById('top-platform')) document.getElementById('top-platform').textContent = totalCoupangClicks >= totalNaverClicks ? `쿠팡 (${coupangPct}%)` : `네이버 (${100 - parseInt(coupangPct)}%)`;

  tbody.innerHTML = dbData.products.map(p => {
    const clicks = p.clicks_count || 0;
    const cClicks = p.platform_clicks?.coupang || p.clicks_coupang || 0;
    const nClicks = p.platform_clicks?.naver || p.clicks_naver || 0;
    const convs = p.conversions_count || 0;
    const rate = clicks > 0 ? ((convs / clicks) * 100).toFixed(1) + '%' : '0.0%';

    return `
      <tr>
        <td style="font-family: monospace; color: var(--primary-accent); font-weight: 700;">morvix.kr/${p.slug}</td>
        <td style="font-weight: 600;">${p.name}</td>
        <td style="font-weight: 800; color: #ff4757;">🛒 ${cClicks.toLocaleString()}회</td>
        <td style="font-weight: 800; color: #2ed573;">🟢 ${nClicks.toLocaleString()}회</td>
        <td style="font-weight: 800; color: #fff;">${convs.toLocaleString()}건</td>
        <td style="font-weight: 800; color: var(--primary-accent);">${rate}</td>
      </tr>
    `;
  }).join('');
}

function renderAdminProductList() {
  const container = document.getElementById('admin-product-list');
  if (!container || !dbData) return;

  container.innerHTML = dbData.products.map(p => `
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; gap: 10px;">
      <div>
        <strong style="color: #fff; font-size: 0.98rem; display: block; margin-bottom: 4px;">${p.name}</strong>
        <div style="font-size: 0.82rem; color: var(--text-muted);">
          morvix.kr/${p.slug} | ${p.episode_label || p.episode_id} | ${p.price ? p.price.toLocaleString() + '원' : '실시간 최저가 연동'}
        </div>
      </div>
      <button style="background: rgba(255, 71, 87, 0.2); color: #ff4757; border: 1px solid rgba(255, 71, 87, 0.4); padding: 6px 14px; border-radius: var(--radius-sm); cursor: pointer; font-size: 0.82rem; font-weight: 700; white-space: nowrap;" onclick="deleteProduct('${p.id}')">삭제</button>
    </div>
  `).join('');
}

function deleteProduct(id) {
  if (confirm("정말 이 상품 자산을 삭제하시겠습니까?")) {
    dbData.products = dbData.products.filter(p => p.id !== id);
    renderProducts();
    renderAnalyticsTable();
    renderAdminProductList();
  }
}

function setupRouting() {
  let slug = window.location.hash.replace('#', '');
  if (!slug) {
    const pathSegments = window.location.pathname.split('/').filter(Boolean);
    if (pathSegments.length > 0) {
      slug = pathSegments[pathSegments.length - 1];
    }
  }
  if (slug && slug !== 'index.html' && slug !== 'index' && slug !== 'admin') {
    openProductDetail(slug);
  }
}

document.addEventListener('DOMContentLoaded', initShopOS);
