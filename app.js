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
    // 카테고리 자동 지정 (없을 경우 이름 기반 추론)
    if (!p.category || p.category === '전체') {
      p.category = getAutoCategory(p.name);
    }
  });
}

// --------------------------------------------------------------------------
// Initialize MORVIX SHOP OS
// --------------------------------------------------------------------------
async function initShopOS() {
  try {
    const res = await fetch('morvix_shop_db.json?t=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const fetched = await res.json();
      if (fetched) {
        if (fetched.categories && Array.isArray(fetched.categories['전체'])) {
          dbData.products = fetched.categories['전체'];
        } else if (Array.isArray(fetched.products)) {
          dbData.products = fetched.products;
        }
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
}

// Render Categories UI
function renderCategories() {
  const container = document.getElementById('category-container');
  if (!container) return;

  const categories = dbData.categories || [
    { id: 'all', name: '📦 전체' },
    { id: 'best', name: '🏆 베스트' },
    { id: 'today', name: '⏰ 오늘만 이가격' },
    { id: 'summer', name: '❄️ 여름/장마' },
    { id: 'life', name: '🏠 생활용품' },
    { id: 'cleaning', name: '🧹 청소/위생' },
    { id: 'kitchen', name: '🍳 주방/요리' },
    { id: 'it', name: '📱 IT/디지털' }
  ];

  container.style.display = 'flex';
  container.style.overflowX = 'auto';
  container.style.padding = '4px 0 12px';
  container.style.gap = '8px';
  container.style.webkitOverflowScrolling = 'touch';
  if (container.parentElement) container.parentElement.style.display = 'block';

  container.innerHTML = categories.map(cat => {
    const catId = cat.id || cat;
    const catName = cat.name || cat;
    const isActive = (currentCategory === catId) || (!currentCategory && catId === 'all');
    const activeStyle = 'background: #0F172A; color: #FFFFFF; border: 1.5px solid #0F172A; font-weight: 800; box-shadow: 0 4px 12px rgba(15,23,42,0.18);';
    const inactiveStyle = 'background: #F8FAFC; color: #475569; border: 1.5px solid #E2E8F0; font-weight: 700;';
    const style = isActive ? activeStyle : inactiveStyle;

    return `
      <button class="cat-pill ${isActive ? 'active' : ''}" data-cat="${catId}" style="${style} padding: 10px 20px; font-size: 0.92rem; border-radius: 24px; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; white-space: nowrap; font-family: 'Pretendard', sans-serif;">
        ${catName}
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

  return `
    <a href="${tossLink}" class="product-card-v2" onclick="handleProductCardClick(event, '${tossLink}', '${p.productId || p.slug}')" style="${extraCardStyle}">
      <div class="card-thumb-frame">
        <img class="card-thumb-img" src="${thumb}" alt="${cleanTitle}" referrerpolicy="no-referrer" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80';">
        ${badgeHTML}
      </div>
      <div class="card-info-wrap">
        <h3 class="card-item-title">${cleanTitle}</h3>
        <div class="card-price-row">
          <span class="card-price-text">${priceStr}</span>
          ${origPriceStr ? `<span class="card-orig-price">${origPriceStr}</span>` : ''}
        </div>
      </div>
    </a>
  `;
}

function handleProductCardClick(e, url, slug) {
  if (!url) return;
  if (e) e.preventDefault();
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

  let activeProducts = dbData.products.filter(p => p && (p.name || '').trim());
  let filtered = activeProducts;

  // 카테고리 필터링 적용
  if (currentCategory && currentCategory !== 'all') {
    if (currentCategory === 'best') {
      filtered = activeProducts.filter(p => p.category === '베스트');
    } else if (currentCategory === 'today') {
      filtered = activeProducts.filter(p => p.category === '오늘만 이가격');
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
