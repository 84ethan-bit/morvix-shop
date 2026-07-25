/* ==========================================================================
   MORVIX SHOP OS - Application Logic & Dynamic Interactions
   ========================================================================== */

let dbData = null;
let currentCategory = 'all';

// Load Shop OS Database
async function initShopOS() {
  try {
    const res = await fetch('morvix_shop_db.json');
    dbData = await res.json();
    
    renderCategories();
    renderProducts();
    setupRouting();
    setupAdminEvents();
  } catch (err) {
    console.error("Failed to load MORVIX Shop OS DB:", err);
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
    title.textContent = '🌟 오늘의 MORVIX 추천';
  } else if (currentCategory !== 'all') {
    filtered = dbData.products.filter(p => p.category === currentCategory);
    const catObj = dbData.categories.find(c => c.id === currentCategory);
    title.textContent = `${catObj ? catObj.icon : ''} ${catObj ? catObj.name : '제품'} 검증 제품`;
  } else {
    title.textContent = '🔥 지금 가장 많이 찾는 검증 제품';
  }

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

// Open Product Detail Modal
function openProductDetail(slug) {
  const product = dbData.products.find(p => p.slug === slug);
  if (!product) return;

  // Track Click Event
  trackOutboundClick(slug);

  const modal = document.getElementById('product-modal');
  const body = document.getElementById('modal-body');

  // Support both array schema and legacy fallback object
  let linksArray = [];
  if (Array.isArray(product.affiliate_links)) {
    linksArray = product.affiliate_links.sort((a, b) => (a.priority || 99) - (b.priority || 99));
  } else if (product.affiliate_links) {
    if (product.affiliate_links.coupang) {
      linksArray.push({ platform: 'coupang', label: '🛒 쿠팡 최저가 확인 및 구매하기 ➔', url: product.affiliate_links.coupang, bg_gradient: 'linear-gradient(135deg, #ff4757, #ff6b81)' });
    }
    if (product.affiliate_links.naver) {
      linksArray.push({ platform: 'naver', label: '🟢 네이버 쇼핑커넥트 확인 및 구매 ➔', url: product.affiliate_links.naver, bg_gradient: 'linear-gradient(135deg, #03cf5d, #02b651)' });
    }
  } else if (product.coupang_link) {
    linksArray.push({ platform: 'coupang', label: '🛒 쿠팡 최저가 확인 및 구매하기 ➔', url: product.coupang_link, bg_gradient: 'linear-gradient(135deg, #ff4757, #ff6b81)' });
  }

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
          ${product.usps.map(u => `<li>✔ ${u}</li>`).join('')}
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
  `;0; text-decoration: none; display: block; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
              ${link.label}
            </a>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  modal.classList.add('active');
}

// Track Click Event in Database
function trackOutboundClick(slug) {
  const prod = dbData.products.find(p => p.slug === slug);
  if (prod) {
    prod.clicks_count = (prod.clicks_count || 0) + 1;
    dbData.click_logs.push({
      timestamp: new Date().toISOString(),
      slug: slug,
      event: 'page_view',
      referer: document.referrer || 'direct_link',
      utm_source: prod.episode_id
    });
    console.log(`[PAGE VIEW TRACKED] morvix.kr/${slug} -> Total Clicks: ${prod.clicks_count}`);
  }
}

function registerAffiliateConversion(slug, platform) {
  const prod = dbData.products.find(p => p.slug === slug);
  if (prod) {
    if (!prod.platform_clicks) prod.platform_clicks = {};
    prod.platform_clicks[platform] = (prod.platform_clicks[platform] || 0) + 1;
    
    prod.conversions_count = (prod.conversions_count || 0) + 1;
    dbData.click_logs.push({
      timestamp: new Date().toISOString(),
      slug: slug,
      event: 'buy_click',
      platform: platform,
      referer: document.referrer || 'direct_link',
      utm_source: prod.episode_id
    });
    console.log(`[BUY CLICK TRACKED] Platform: ${platform.toUpperCase()} | Slug: ${slug}`);
  }
}

// Setup Admin OS Event Handlers & Security
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

  // Verify Admin Auth PIN via In-Page Modal
  function verifyAndOpenAdmin() {
    if (sessionStorage.getItem('morvix_admin_auth') === 'true') {
      if (loginModal) loginModal.classList.remove('active');
      modal.classList.add('active');
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

  // Handle Admin PIN Form Submit
  if (formLogin) {
    formLogin.addEventListener('submit', (e) => {
      e.preventDefault();
      const pin = inputPin.value.trim();
      if (pin === "2026") {
        sessionStorage.setItem('morvix_admin_auth', 'true');
        if (loginErrorMsg) loginErrorMsg.style.display = 'none';
        loginModal.classList.remove('active');
        modal.classList.add('active');
        renderAnalyticsTable();
        renderAdminProductList();
      } else {
        if (loginErrorMsg) loginErrorMsg.style.display = 'block';
      }
    });
  }

  if (btnCloseLogin) {
    btnCloseLogin.addEventListener('click', () => {
      loginModal.classList.remove('active');
    });
  }

  // Check URL query/hash/path trigger (e.g., ?admin, #admin, /admin)
  const isAdminUrl = window.location.search.includes('admin') || window.location.hash.includes('admin') || window.location.pathname.includes('admin');
  if (isAdminUrl) {
    setTimeout(verifyAndOpenAdmin, 200);
  }

  btnOpen.addEventListener('click', verifyAndOpenAdmin);

  // Secret Trigger 1: Triple-click on Brand Logo
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

  // Secret Trigger 2: Keyboard Shortcut (Ctrl + Shift + A)
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a')) {
      e.preventDefault();
      verifyAndOpenAdmin();
    }
  });

  btnClose.addEventListener('click', () => {
    modal.classList.remove('active');
  });

  // Product Detail Modal Close Button
  document.getElementById('btn-close-modal').addEventListener('click', () => {
    document.getElementById('product-modal').classList.remove('active');
  });

  // ⚡ One-Click Auto Ingestion Handler
  const btnAutoFetch = document.getElementById('btn-auto-fetch');
  if (btnAutoFetch) {
    btnAutoFetch.addEventListener('click', () => {
      const rawUrl = document.getElementById('input-auto-url').value.trim();
      if (!rawUrl) {
        alert("⚠️ 제휴 URL을 입력 후 [자동 불러오기]를 눌러주세요.");
        return;
      }

      const isCoupang = rawUrl.includes('coupang.com');
      const isNaver = rawUrl.includes('naver.com');

      // Auto-fill affiliate links
      if (isCoupang) {
        document.getElementById('input-link-coupang').value = rawUrl;
      } else if (isNaver) {
        document.getElementById('input-link-naver').value = rawUrl;
      } else {
        document.getElementById('input-link-coupang').value = rawUrl;
      }

      // Generate Auto Slug & Episode ID
      const nextEpNum = (dbData ? dbData.products.length + 1 : 11).toString().padStart(3, '0');
      const autoSlug = `item${nextEpNum}`;
      document.getElementById('input-slug').value = autoSlug;
      document.getElementById('input-episode').value = `INTERNAL_CASE_EP${nextEpNum}`;

      // Auto-fill Product Metadata & AI USPs
      document.getElementById('input-name').value = "모르빅스 생활 억까 탈출 검증 꿀템";
      document.getElementById('input-price').value = 24900;
      document.getElementById('input-category').value = "summer";
      document.getElementById('input-subtitle').value = "일상의 불편함을 3초 만에 완벽 해결하는 검증 솔루션";
      document.getElementById('input-usps').value = [
        "100만 바이럴 검증 실생활 문제 해결 설계",
        "압도적 가성비 최저가 파트너스 보장",
        "초간단 사용 및 내구성 안심 인증 원단/부품",
        "MORVIX 숏폼 에피소드 실측 검증 완료"
      ].join('\n');

      alert(`⚡ [원클릭 자동 불러오기 완료!]\n단축 슬러그: morvix.kr/${autoSlug}\n에피소드: EP${nextEpNum}\n상품명/가격/AI 4-USP가 자동 채워졌습니다.`);
    });
  }

  // Admin Tab Switcher
  document.querySelectorAll('.admin-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.admin-tab-content').forEach(c => c.classList.remove('active'));

      e.currentTarget.classList.add('active');
      const targetId = e.currentTarget.getAttribute('data-tab');
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Form Submit Handler
  document.getElementById('form-add-product').addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('input-name').value;
    const slug = document.getElementById('input-slug').value;
    const category = document.getElementById('input-category').value;
    const episode = document.getElementById('input-episode').value;
    const price = parseInt(document.getElementById('input-price').value);
    const linkCoupang = document.getElementById('input-link-coupang').value;
    const linkNaver = document.getElementById('input-link-naver').value;
    const subtitle = document.getElementById('input-subtitle').value;
    const uspsText = document.getElementById('input-usps').value;

    const affiliateLinks = [];
    if (linkCoupang) {
      affiliateLinks.push({
        platform: 'coupang',
        label: '🛒 쿠팡 최저가 확인 및 구매하기 ➔',
        url: linkCoupang,
        priority: 1,
        bg_gradient: 'linear-gradient(135deg, #ff4757, #ff6b81)'
      });
    }
    if (linkNaver) {
      affiliateLinks.push({
        platform: 'naver',
        label: '🟢 네이버 쇼핑커넥트 확인 및 구매 ➔',
        url: linkNaver,
        priority: 2,
        bg_gradient: 'linear-gradient(135deg, #03cf5d, #02b651)'
      });
    }

    const epNum = episode.replace(/[^0-9]/g, '') || '011';

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
      affiliate_links: affiliateLinks,
      thumbnail: "https://images.unsplash.com/photo-1541123437800-1bb1317badc2?w=800&auto=format&fit=crop&q=80",
      images: ["https://images.unsplash.com/photo-1541123437800-1bb1317badc2?w=800&auto=format&fit=crop&q=80"],
      webtoon_episode_title: `${episode} 바이럴 에피소드`,
      webtoon_cuts_count: 15,
      clicks_count: 0,
      platform_clicks: { coupang: 0, naver: 0 },
      conversions_count: 0
    };

    dbData.products.unshift(newProd);
    alert(`✅ 다중 제휴 상품등록 완료!\n단축 URL: morvix.kr/${slug}\n에피소드: EP${epNum}\n쿠팡 & 네이버 제휴 CTA가 활성화되었습니다.`);

    renderProducts();
    renderAnalyticsTable();
    renderAdminProductList();
    document.getElementById('form-add-product').reset();
  });
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

  // Calculate Executive KPI Metrics
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
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <strong style="color: #fff; font-size: 1rem;">${p.name}</strong>
        <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">
          morvix.kr/${p.slug} | ${p.episode_id} | ${p.price.toLocaleString()}원
        </div>
      </div>
      <button style="background: #ff4757; color: #fff; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;" onclick="deleteProduct('${p.id}')">삭제</button>
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

// URL Hash / Slug Routing Support (e.g. /fan001 or #fan001)
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

// Run App on Load
document.addEventListener('DOMContentLoaded', initShopOS);
