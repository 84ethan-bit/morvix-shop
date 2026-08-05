/* ==========================================================================
   MORVIX SHOP OS v3.1 - Master DB Lifecycle Engine & Smart Auto Classifier
   ========================================================================== */

function openTossMobileView(url, e) {
  if (!url) return;
  if (e) e.preventDefault();
  window.location.href = url;
}

const INITIAL_DB_DATA = {
  "store_info": {
    "brand_name": "MORVIX SHOP OS",
    "domain": "morvix.kr",
    "tagline": "일상을 바꾸는 검증된 꿀템만 소개합니다.",
    "version": "v3.1 (State-Based Lifecycle Engine)"
  },
  "categories": [
    {"id": "all", "name": "모든 제품", "icon": "📦"},
    {"id": "best", "name": "베스트", "icon": "🏆"},
    {"id": "today", "name": "오늘만 이가격", "icon": "⏰"},
    {"id": "summer", "name": "여름/장마", "icon": "❄️"},
    {"id": "life", "name": "생활용품", "icon": "🏠"},
    {"id": "cleaning", "name": "청소/위생", "icon": "🧹"},
    {"id": "kitchen", "name": "주방/요리", "icon": "🍳"},
    {"id": "it", "name": "IT/디지털", "icon": "📱"}
  ],
  "products": []
};

let dbData = INITIAL_DB_DATA;
let currentCategory = 'all';
let currentSort = 'popular';
let displayedProductCount = 24;

// --------------------------------------------------------------------------
// 1. Smart Category Auto Classifier
// --------------------------------------------------------------------------
function getAutoCategory(titleText) {
  const lk = (titleText || '').toLowerCase().replace(/\s+/g, '');

  if (anyKeyword(lk, ["서큘레이터", "선풍기", "에어컨", "쿨링", "이불", "패드", "여름", "얼음", "장마", "모기", "냉풍기", "아이스", "쿨매트", "냉감", "시원"])) return "summer";
  if (anyKeyword(lk, ["청소기", "청소", "소독", "세제", "휴지", "물티슈", "샴푸", "칫솔", "치약", "비누", "걸레", "유연제", "수건", "기저귀", "키친타올", "생리대", "면도기", "살충제", "마스크", "방향제", "바디워시", "화장지"])) return "cleaning";
  if (anyKeyword(lk, ["냄비", "프라이팬", "식기", "그릇", "도마", "칼", "주방", "조리", "밥솥", "전기포트", "믹서기", "에어프라이어", "전자레인지", "텀블러", "밀폐용기", "오븐", "식기세척기", "수저", "젓가락"])) return "kitchen";
  if (anyKeyword(lk, ["맥세이프", "거치대", "충전기", "아이폰", "갤럭시", "키보드", "마우스", "무선", "디지털", "모니터", "노트북", "태블릿", "에어팟", "버즈", "워치", "스피커", "이어폰", "헤드폰", "usb", "케이블", "보조배터리"])) return "it";

  return "life";
}

function anyKeyword(text, keywords) {
  return keywords.some(kw => text.includes(kw));
}

function updateProductLifecycleStates() {
  if (!dbData || !dbData.products) return;
  dbData.products.forEach(p => {
    if (!p.status || p.status === 'EXPIRED' || p.status === 'OUT_OF_STOCK') {
      p.status = 'ACTIVE';
    }
    if (!p.category || p.category === '전체') {
      p.category = getAutoCategory(p.name);
    }
  });
}


function renderCategories() {
  const container = document.getElementById('category-container');
  if (container) {
    container.style.display = 'none';
    if (container.parentElement) container.parentElement.style.display = 'none';
  }
  return;
}

function normalizeProductSchema(rawList, defaultCategory = '') {
  if (!Array.isArray(rawList)) return [];
  return rawList.map(p => {
    if (!p) return null;
    const thumbnail = p.thumbnail || p.imageUrl || p.image || '';
    const name = p.name || p.title || '';
    const price = typeof p.price === 'number' ? p.price : parseInt(String(p.price || 0).replace(/[^0-9]/g, '')) || 0;
    const original_price = typeof p.originalPrice === 'number' ? p.originalPrice : (typeof p.original_price === 'number' ? p.original_price : parseInt(String(p.originalPrice || p.original_price || 0).replace(/[^0-9]/g, '')) || 0);
    const toss_link = p.shareUrl || p.toss_link || p.url || '#';
    const slug = String(p.productId || p.slug || p.id || Math.random());
    const discount_rate = p.discount_rate || (original_price > price ? Math.round((1 - price / original_price) * 100) + '%' : '');
    const isTodayPrice = defaultCategory === '오늘만 이가격' || p.category === '오늘만 이가격' || p.category === '오늘만 이 가격' || p.section === 'today_price' || p.category === 'today_price';
    
    return {
      ...p,
      id: slug,
      slug: slug,
      name: name,
      price: price,
      original_price: original_price,
      discount_rate: discount_rate,
      thumbnail: thumbnail,
      toss_link: toss_link,
      section: isTodayPrice ? 'today_price' : (p.section || 'best_seller'),
      category: p.category || defaultCategory || 'all',
      status: 'ACTIVE'
    };
  }).filter(p => p && p.name && p.thumbnail);
}

// --------------------------------------------------------------------------
// Initialize MORVIX SHOP OS
// --------------------------------------------------------------------------
async function initShopOS() {
  try {
    const res = await fetch('morvix_shop_db.json?t=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const fetched = await res.json();
      let normalizedProducts = [];

      if (fetched && Array.isArray(fetched.products)) {
        normalizedProducts = normalizeProductSchema(fetched.products);
      } else if (fetched && fetched.categories) {
        const todayPriceList = fetched.categories['오늘만 이가격'] || fetched.categories['오늘만 이 가격'] || [];
        const todaySlugs = new Set(todayPriceList.map(p => String(p.productId || p.slug || p.id)));

        const allList = fetched.categories['전체'] || [];
        
        const normalizedToday = normalizeProductSchema(todayPriceList, '오늘만 이가격');
        const normalizedAll = normalizeProductSchema(allList, 'all').map(p => {
          if (todaySlugs.has(p.slug)) p.section = 'today_price';
          return p;
        });

        // Merge & Deduplicate
        const map = new Map();
        [...normalizedToday, ...normalizedAll].forEach(p => {
          if (!map.has(p.slug)) map.set(p.slug, p);
        });
        normalizedProducts = Array.from(map.values());
      }

      if (normalizedProducts.length > 0) {
        dbData.products = normalizedProducts;
      }
    }
  } catch (err) {
    console.warn("Primary DB fetch warning:", err);
  }

  updateProductLifecycleStates();
  renderCategories();
  renderProducts();
  setupRouting();
  setupAdminEvents();
  setupSection1Scroll();
}

function setupSection1Scroll() {
  const grid = document.getElementById('time-attack-grid');
  const btnLeft = document.getElementById('btn-scroll-left');
  const btnRight = document.getElementById('btn-scroll-right');
  if (!grid || !btnLeft || !btnRight) return;

  btnLeft.addEventListener('click', (e) => {
    e.preventDefault();
    grid.scrollBy({ left: -450, behavior: 'smooth' });
  });

  btnRight.addEventListener('click', (e) => {
    e.preventDefault();
    grid.scrollBy({ left: 450, behavior: 'smooth' });
  });
}

// Render Categories UI
function renderCategories() {
  const container = document.getElementById('category-container');
  if (!container) return;

  const categories = [
    { 
      id: 'all', 
      name: '전체', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"></rect><rect x="14" y="3" width="7" height="7" rx="1.5"></rect><rect x="14" y="14" width="7" height="7" rx="1.5"></rect><rect x="3" y="14" width="7" height="7" rx="1.5"></rect></svg>'
    },
    { 
      id: 'today_price', 
      name: '오늘만 이가격', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3.5z"></path></svg>'
    },
    { 
      id: 'best', 
      name: 'BEST', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"></path></svg>'
    },
    { 
      id: 'fruit', 
      name: '과일·신선', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.91 4.91 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06z"></path><path d="M10 2c1 .5 2 2 2 5"></path></svg>'
    },
    { 
      id: 'food', 
      name: '식품', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>'
    },
    { 
      id: 'living', 
      name: '생활·주방', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>'
    },
    { 
      id: 'car', 
      name: '차량용품', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H7c-.7 0-1.3.3-1.8.7C4.3 8.6 3 10 3 10s-2.7.6-4.5 1.1C.7 11.3 0 12.1 0 13v3c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><path d="M9 17h6"></path><circle cx="17" cy="17" r="2"></circle></svg>'
    },
    { 
      id: 'fashion', 
      name: '패션·뷰티', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"></path></svg>'
    },
    { 
      id: 'health', 
      name: '건강', 
      iconSvg: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>'
    }
  ];

  container.style.display = 'flex';
  container.style.overflowX = 'auto';
  container.style.padding = '4px 0 12px';
  container.style.gap = '8px';
  container.style.webkitOverflowScrolling = 'touch';
  if (container.parentElement) container.parentElement.style.display = 'block';

  container.innerHTML = categories.map(cat => {
    const isActive = (currentCategory === cat.id) || (!currentCategory && cat.id === 'all');
    const activeStyle = 'background: #0052CC; color: #FFFFFF; border: 1.5px solid #0052CC; font-weight: 800; box-shadow: 0 4px 12px rgba(0,82,204,0.22);';
    const inactiveStyle = 'background: #F8FAFC; color: #475569; border: 1.5px solid #E2E8F0; font-weight: 700;';
    const style = isActive ? activeStyle : inactiveStyle;

    return `
      <button class="cat-pill ${isActive ? 'active' : ''}" data-cat="${cat.id}" style="${style} padding: 9px 18px; font-size: 0.9rem; border-radius: 24px; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; white-space: nowrap; font-family: 'Pretendard', sans-serif; display: inline-flex; align-items: center; gap: 6px;">
        <span class="cat-icon" style="display: inline-flex; align-items: center; color: ${isActive ? '#FFFFFF' : '#64748B'};">${cat.iconSvg}</span>
        <span>${cat.name}</span>
      </button>
    `;
  }).join('');

  container.querySelectorAll('.cat-pill').forEach(btn => {
    btn.addEventListener('click', (e) => {
      currentCategory = e.currentTarget.getAttribute('data-cat');
      displayedProductCount = 16;
      renderCategories();
      renderProducts();
    });
  });
}

// Countdown Clock Engine
function startCountdownClock() {
  const clockEl = document.getElementById('countdown-clock');
  if (!clockEl) return;

  function updateClock() {
    const now = new Date();
    const endOfDay = new Date();
    endOfDay.setHours(23, 59, 59, 999);
    const diff = Math.max(0, Math.floor((endOfDay - now) / 1000));

    const h = String(Math.floor(diff / 3600)).padStart(2, '0');
    const m = String(Math.floor((diff % 3600) / 60)).padStart(2, '0');
    const s = String(diff % 60).padStart(2, '0');

    clockEl.textContent = `${h}:${m}:${s}`;
  }

  updateClock();
  setInterval(updateClock, 1000);
}

// Universal ProductCard Component Generator
function renderUniversalProductCard(p, badgeHTML = '', extraCardStyle = '') {
  if (!p) return '';
  
  const title = p.name || '';
  const thumb = p.imageUrl || p.thumbnail || '';
  if (!title || !thumb) return '';

  let cleanTitle = title.trim();

  const numPrice = typeof p.price === 'number' ? p.price : parseInt(String(p.price || 0).replace(/[^0-9]/g, '')) || 0;
  const priceStr = numPrice > 0 ? numPrice.toLocaleString() + '원' : '특가 확인';

  const numOrig = typeof p.originalPrice === 'number' ? p.originalPrice : parseInt(String(p.originalPrice || 0).replace(/[^0-9]/g, '')) || 0;
  const origPriceStr = numOrig > numPrice ? numOrig.toLocaleString() + '원' : '';

  const tossLink = getTossShareLink(p);

  // 3. 네온 할인율 뱃지 (시선 강탈)
  let discountBadgeHTML = '';
  if (discRate) {
    const formattedRate = discRate.includes('%') ? discRate : '-' + discRate + '%';
    discountBadgeHTML = `<span style="position: absolute; top: 8px; right: 8px; background: linear-gradient(135deg, #FF4757 0%, #FF6B81 100%); color: #FFFFFF; font-size: 0.76rem; font-weight: 900; padding: 3px 8px; border-radius: 8px; box-shadow: 0 3px 10px rgba(255,71,87,0.35); z-index: 3; letter-spacing: -0.3px;">${formattedRate}</span>`;
  }

  return `
    <a href="${tossLink}" target="_self" class="product-card-v2" onclick="handleProductCardClick(event, '${tossLink}', '${p.slug}')" style="${extraCardStyle}">
      <!-- 1. Pure 1:1 Image Box with Absolute Badge -->
      <div class="card-thumb-frame" style="position: relative;">
        <img class="card-thumb-img" src="${p.thumbnail}" alt="${cleanTitle}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80';">
        ${badgeHTML}
        ${discountBadgeHTML}
      </div>

      <!-- 2. Clean 3-Part Information Hierarchy & CTA Tag -->
      <div class="card-info-wrap">
        <h3 class="card-item-title">${cleanTitle}</h3>
        <div class="card-bottom-row" style="display: flex; justify-content: space-between; align-items: flex-end; width: 100%; margin-top: auto; padding-top: 6px; flex-wrap: nowrap;">
          <div class="card-price-row" style="margin: 0;">
            <span class="card-price-text">${priceStr}</span>
            ${origPriceStr ? `<span class="card-orig-price" style="display: block; font-size: 0.75rem;">${origPriceStr}</span>` : ''}
          </div>
          <span class="cta-direct-btn" style="background: rgba(0, 82, 204, 0.07); color: #0052CC; border: 1px solid rgba(0, 82, 204, 0.2); font-size: 0.73rem; font-weight: 800; padding: 5px 9px; border-radius: 8px; display: inline-flex; align-items: center; gap: 3px; flex-shrink: 0; white-space: nowrap; transition: all 0.2s ease;">
            토스 특가 보기 ➔
          </span>
        </div>
      </div>
    </a>
  `;
}

function handleProductCardClick(e, url, slug) {
  if (e) {
    e.preventDefault();
    if (e.stopPropagation) e.stopPropagation();
  }
  if (!url || url === '#') return;
  try {
    trackOutboundClick(slug);
  } catch (err) {}

  // 팝업창/인앱 브라우저 새창을 100% 원천 차단하고 
  // 현재 창 direct 이동(window.location.href)을 수행하여 토스 앱을 즉시 실행(Deep Linking)
  window.location.href = url;
}
window.handleProductCardClick = handleProductCardClick;

function loadMoreProducts() {
  displayedProductCount += 16;
  renderProducts();
}

function getTossShareLink(p) {
  if (!p) return 'https://toss.im';
  return p.shareUrl || p.share_link || p.toss_link || 'https://toss.im';
}

function renderProducts() {
  const grid = document.getElementById('product-grid');
  const count = document.getElementById('product-count');
  const sortSelect = document.getElementById('sort-select');
  const loadMoreWrap = document.getElementById('load-more-wrap');
  const btnLoadMore = document.getElementById('btn-load-more');
  if (!grid || !dbData) return;

  updateProductLifecycleStates();
  startCountdownClock();

  if (sortSelect && !sortSelect.hasAttribute('data-bound')) {
    sortSelect.setAttribute('data-bound', 'true');
    sortSelect.addEventListener('change', (e) => {
      currentSort = e.target.value;
      displayedProductCount = 16;
      renderProducts();
    });
  }

  // Filter out any invalid/null product entries
  let activeProducts = dbData.products.filter(p => p && p.name && p.thumbnail && (p.status === 'ACTIVE' || !p.status));

  const metricToday = document.getElementById('metric-today-count');
  if (metricToday && activeProducts.length > 0) {
    metricToday.textContent = `${activeProducts.length}개`;
  }
  const catTitles = {
    'all': '📦 전체 핫딜 모음집',
    'fruit': '🍎 과일·신선 핫딜 모음집',
    'food': '🥦 식품 핫딜 모음집',
    'living': '🏠 생활·주방 핫딜 모음집',
    'car': '🚗 차량용품 핫딜 모음집',
    'fashion': '👔 패션·뷰티 핫딜 모음집',
    'health': '💊 건강 핫딜 모음집'
  };

  // 카테고리 필터링 적용 (오늘만 이가격 매칭 포함)
  if (currentCategory && currentCategory !== 'all') {
    if (currentCategory === 'best') {
      filtered = activeProducts.filter(p => p.category === '베스트');
    } else if (currentCategory === 'today') {
      filtered = activeProducts.filter(p => p.category === '오늘만 이가격' || p.category === 'today');
    } else {
      filtered = activeProducts.filter(p => p.category === currentCategory || getAutoCategory(p.name) === currentCategory);
    }
  }

  if (count) count.textContent = `총 ${filtered.length}개 핫딜 노출 중`;

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; background: #ffffff; border: 1px dashed #cbd5e1; border-radius: 20px;">
        <div style="font-size: 2.8rem; margin-bottom: 12px;">🛒</div>
        <h3 style="font-size: 1.2rem; font-weight: 800; color: #0f172a; margin-bottom: 6px;">현재 등록된 핫딜이 없습니다</h3>
      </div>
    `;
    if (loadMoreWrap) loadMoreWrap.style.display = 'none';
    return;
  }

  const paginatedProducts = filtered.slice(0, displayedProductCount);

  if (loadMoreWrap && btnLoadMore) {
    if (paginatedProducts.length < filtered.length) {
      loadMoreWrap.style.display = 'block';
      btnLoadMore.textContent = `📦 핫딜 더보기 (${paginatedProducts.length}/${filtered.length})`;
    } else {
      loadMoreWrap.style.display = 'none';
    }
  }

  grid.innerHTML = paginatedProducts.map((p, idx) => {
    let rankBadgeHTML = '';
    if (idx === 0) rankBadgeHTML = '<span class="rank-badge-gold">🥇 BEST 1위</span>';
    else if (idx === 1) rankBadgeHTML = '<span class="rank-badge-silver">🥈 BEST 2위</span>';
    else if (idx === 2) rankBadgeHTML = '<span class="rank-badge-bronze">🥉 BEST 3위</span>';

    return renderUniversalProductCard(p, rankBadgeHTML);
  }).join('');
}

function openProductDetail(slug) {
  if (!dbData || !dbData.products) return;
  const product = dbData.products.find(p => p.slug === slug || p.productId === slug);
  if (!product) return;
  const tossLink = getTossShareLink(product);
  if (tossLink) {
    window.location.href = tossLink;
  }
}

const DB_STORAGE_KEY = 'morvix_master_db_products_v14';

async function verifyAndOpenAdmin() {
  const modal = document.getElementById('admin-modal');
  const loginModal = document.getElementById('admin-login-modal');
  if (sessionStorage.getItem('morvix_admin_auth') === 'true') {
    if (loginModal) loginModal.classList.remove('active');
    if (modal) modal.classList.add('active');
    return;
  }
  if (loginModal) loginModal.classList.add('active');
}

function setupAdminEvents() {
  const btnOpen = document.getElementById('btn-open-admin');
  const btnClose = document.getElementById('btn-close-admin');
  const modal = document.getElementById('admin-modal');
  if (btnOpen) btnOpen.addEventListener('click', verifyAndOpenAdmin);
  if (btnClose && modal) btnClose.addEventListener('click', () => modal.classList.remove('active'));
}

function setupRouting() {
  const hash = window.location.hash.replace('#', '');
  if (hash === 'admin') verifyAndOpenAdmin();
}

document.addEventListener('DOMContentLoaded', initShopOS);
