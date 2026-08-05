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
  "products": []
};

let dbData = INITIAL_DB_DATA;
let currentCategory = 'all';
let currentSort = 'popular';
let displayedProductCount = 24;


// --------------------------------------------------------------------------
// 1. Smart Category Auto Classifier (hot-deal-studio Engine Ported & Extended)
// --------------------------------------------------------------------------
function getAutoCategory(titleText) {
  const lk = (titleText || '').toLowerCase().replace(/\s+/g, '');

  // 1. Summer & Cooling (Priority 1)
  if (anyKeyword(lk, [
    "서큘레이터", "선풍기", "에어컨", "쿨링", "이불", "패드", "여름", "얼음", "장마", "모기", "포충기", "냉풍기",
    "초냉감", "열대야", "부채", "제습기", "냉매", "아이스", "얼음조끼", "쿨매트", "쿨베개", "냉감", "홑이불", "시원"
  ])) return "summer";

  // 2. Cleaning & Vacuum & Hygiene (Priority 2 - BEFORE general IT)
  if (anyKeyword(lk, [
    "청소기", "청소", "소독", "탈취", "세제", "위생", "스크러버", "휴지", "물티슈", "샴푸", "린스", "칫솔", "치약", "비누", "걸레",
    "유연제", "섬유유연제", "수건", "기저귀", "키친타올", "생리대", "면도기", "살충제", "제습제", "마스크", "손세정제",
    "방향제", "건전지", "세탁세제", "주방세제", "바디워시", "화장지", "티슈", "치실", "구강청결제", "로봇청소기"
  ])) return "cleaning";

  // 3. Kitchen & Cooking (Priority 3)
  if (anyKeyword(lk, [
    "냄비", "프라이팬", "식기", "그릇", "도마", "칼", "가위", "주방", "조리", "밥솥", "전기포트", "믹서기", "에어프라이어",
    "전자레인지", "텀블러", "밀폐용기", "도시락", "오븐", "토스터", "커피머신", "쌀통", "행주", "수세미", "니트릴", "호일",
    "랩", "지퍼백", "식세기", "식기세척기", "수저", "젓가락", "포크", "쟁반", "국자", "뒤집개", "집게", "위생장갑"
  ])) return "kitchen";

  // 4. IT & Electronics (Priority 4)
  if (anyKeyword(lk, [
    "맥세이프", "거치대", "충전기", "충전", "아이폰", "갤럭시", "데스크", "키보드", "마우스", "무선", "it", "디지털",
    "모니터", "노트북", "태블릿", "아이패드", "에어팟", "버즈", "워치", "스피커", "이어폰", "헤드폰", "공유기", "외장하드",
    "usb", "닌텐도", "플스", "게임기", "공기청정기", "가전", "tv", "노트북가방", "파우치", "케이블", "보조배터리"
  ])) return "it";

  // 5. Automotive (Priority 5)
  if (anyKeyword(lk, [
    "자동차", "차량", "햇빛", "차광", "우산", "세차", "블랙박스", "네비게이션", "와이퍼", "타이어", "광택", "방향제",
    "시트커버", "핸들커버", "차량용", "엔진오일", "워셔액", "하이패스", "세차용품", "트렁크", "차박"
  ])) return "car";

  // 6. Pets (Priority 6)
  if (anyKeyword(lk, [
    "강아지", "고양이", "펫", "사료", "간식", "장난감", "목줄", "하네스", "캣타워", "펫푸드", "반려동물", "애완",
    "멍멍", "야옹", "츄르", "모래", "배변패드", "이동장", "숨집", "애견", "캣"
  ])) return "pet";

  // 7. General Home & Living (Fallback)
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
  dbData.products.forEach(p => {
    if (!p.status || p.status === 'EXPIRED' || p.status === 'OUT_OF_STOCK') {
      p.status = 'ACTIVE';
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

// --------------------------------------------------------------------------
// Initialize MORVIX SHOP OS
// --------------------------------------------------------------------------
async function initShopOS() {
  try {
    const res = await fetch('morvix_shop_db.json?t=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const fetched = await res.json();
      if (fetched) {
        if (Array.isArray(fetched.products) && fetched.products.length > 0) {
          dbData.products = fetched.products;
        } else if (fetched.categories && Array.isArray(fetched.categories['전체']) && fetched.categories['전체'].length > 0) {
          dbData.products = fetched.categories['전체'];
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

  const categories = [
    { id: 'all', name: '📦 전체' },
    { id: 'fruit', name: '🍎 과일·신선' },
    { id: 'food', name: '🥦 식품' },
    { id: 'living', name: '🏠 생활·주방' },
    { id: 'car', name: '🚗 차량용품' },
    { id: 'fashion', name: '👔 패션·뷰티' },
    { id: 'health', name: '💊 건강' }
  ];

  container.style.display = 'flex';
  container.style.overflowX = 'auto';
  container.style.padding = '4px 0 12px';
  container.style.gap = '8px';
  container.style.webkitOverflowScrolling = 'touch';
  if (container.parentElement) container.parentElement.style.display = 'block';

  container.innerHTML = categories.map(cat => {
    const isActive = (currentCategory === cat.id) || (!currentCategory && cat.id === 'all');
    const activeStyle = 'background: #0F172A; color: #FFFFFF; border: 1.5px solid #0F172A; font-weight: 800; box-shadow: 0 4px 12px rgba(15,23,42,0.18);';
    const inactiveStyle = 'background: #F8FAFC; color: #475569; border: 1.5px solid #E2E8F0; font-weight: 700;';
    const style = isActive ? activeStyle : inactiveStyle;

    return `
      <button class="cat-pill ${isActive ? 'active' : ''}" data-cat="${cat.id}" style="${style} padding: 10px 20px; font-size: 0.92rem; border-radius: 24px; cursor: pointer; transition: all 0.2s ease; flex-shrink: 0; white-space: nowrap; font-family: 'Pretendard', sans-serif;">
        ${cat.name}
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

function trackOutboundClick(slug) {
  try {
    logRealClickEvent(slug, 'toss');
  } catch (e) {}
}
window.trackOutboundClick = trackOutboundClick;

function getTossShareLink(p) {
  if (!p) return 'https://toss.im';
  return p.shareUrl || p.share_link || p.toss_link || 'https://toss.im';
}

function parseDiscountNum(val) {
  if (!val) return 0;
  const nums = String(val).replace(/[^\d]/g, '');
  return nums ? parseInt(nums, 10) : 0;
}

function renderProducts() {
  const grid = document.getElementById('product-grid');
  const timeAttackGrid = document.getElementById('time-attack-grid');
  const title = document.getElementById('section-title');
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

  if (currentCategory && currentCategory !== 'all') {
    filtered = activeProducts.filter(p => p.category === currentCategory);
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

const EVENT_LOG_KEY = 'morvix_real_click_events_v1';

function logRealClickEvent(slug, platform) {
  try {
    const rawLogs = localStorage.getItem(EVENT_LOG_KEY);
    const logs = rawLogs ? JSON.parse(rawLogs) : [];
    logs.unshift({ timestamp: new Date().toISOString(), slug, platform });
    localStorage.setItem(EVENT_LOG_KEY, JSON.stringify(logs.slice(0, 500)));
  } catch (e) {}
}

const DB_STORAGE_KEY = 'morvix_master_db_products_v14';

async function saveMasterDbToStorage() {
  if (!dbData || !dbData.products) return;
  try {
    localStorage.setItem(DB_STORAGE_KEY, JSON.stringify(dbData.products));
  } catch (e) {}
}

async function loadMasterDbFromStorage() {
  try {
    const res = await fetch('morvix_shop_db.json?t=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const serverData = await res.json();
      
      let productList = [];
      if (serverData && serverData.categories && Array.isArray(serverData.categories['전체'])) {
        productList = serverData.categories['전체'];
      } else if (serverData && Array.isArray(serverData.products)) {
        productList = serverData.products;
      }

      if (productList.length > 0) {
        dbData.products = productList;
        localStorage.setItem(DB_STORAGE_KEY, JSON.stringify(dbData.products));
        return;
      }
    }
  } catch (err) {
    console.warn("Server DB fetch notice:", err);
  }

  try {
    const saved = localStorage.getItem(DB_STORAGE_KEY);
    if (saved) {
      const parsedProds = JSON.parse(saved);
      if (Array.isArray(parsedProds) && parsedProds.length > 0) {
        dbData.products = parsedProds;
      }
    }
  } catch (e) {}
}

function verifyAndOpenAdmin() {
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
