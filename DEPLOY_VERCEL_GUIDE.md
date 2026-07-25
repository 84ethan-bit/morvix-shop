# 🚀 MORVIX SHOP OS - Vercel Free Deployment Guide v2.0

> **"비용 0원으로 morvix.vercel.app 브랜드 도메인, SSL, Edge CDN 및 Analytics를 동시 배포하는 가이드"**

---

## 1. 배포 요약 (Deployment Summary)

* **플랫폼:** Vercel (Free Tier)
* **프로젝트명:** `morvix` ➔ 라이브 URL: **`https://morvix.vercel.app`**
* **월 호스팅/SSL/CDN 비용:** **0원**
* **완료된 프로덕션 에셋:**
  - ✅ `package.json`, `vercel.json` (URL Rewrites & CORS Headers)
  - ✅ Open Graph / Kakao/Instagram 공유 카드 태그
  - ✅ `robots.txt` & `sitemap.xml` (Search Engine Indexing)
  - ✅ `favicon.svg` 브랜드 아이콘
  - ✅ GA4 (Google Analytics 4) & Microsoft Clarity 트래킹 태그 바인딩

---

## 2. 배포 5단계 가이드 (5-Minute Deployment)

### 1단계: GitHub Repository 생성 & 푸시
```bash
cd C:\옵시디언\Jarvis_Starter_Pack-jarvis-starter-pack-v2\NEXORA\MORVIX_Shop_OS
git init
git add .
git commit -m "feat: MORVIX SHOP OS v1.2.0 Production Ready"
git remote add origin https://github.com/YOUR_GITHUB_ID/morvix-shop.git
git push -u origin main
```

---

### 2단계: Vercel 프로젝트 생성 (`morvix`)
1. [Vercel Dashboard](https://vercel.com/new) 로그인
2. `morvix-shop` 레포지토리 **Import**
3. **Project Name** 필드에 **`morvix`** 입력 (중요: `morvix.vercel.app` 선점)
4. **Deploy** 버튼 클릭 ➔ 30초 내 배포 완료!

---

### 3단계: 라이브 URL 5대 핵심 기능 검증
* ✅ **HTTPS 정상 동작:** `https://morvix.vercel.app/`
* ✅ **모바일 1초 랜딩:** 모바일 반응형 UX 및 글래스모피즘 렌더링
* ✅ **단축 슬러그 리다이렉트:** `https://morvix.vercel.app/fan001` ➔ 모달 자동 오픈
* ✅ **쿠팡 파트너스 CTA:** `🛒 쿠팡 최저가 확인 및 구매` 클릭 후 이벤트 로깅
* ✅ **네이버 쇼핑커넥트 CTA:** `🟢 네이버 쇼핑커넥트 확인 및 구매` 클릭 후 이벤트 로깅

---

### 4단계: Analytics & Search Console 등록
1. **Google Search Console:** `https://search.google.com/search-console` 접속 ➔ `https://morvix.vercel.app` 소유권 확인 ➔ `sitemap.xml` 제출
2. **GA4 & Microsoft Clarity:** `index.html` 내 고유 측정 ID 수동 기입

---

### 5단계: Phase 2 수익 발생 시 `morvix.kr` 커스텀 도메인 결합
1. Vercel Dashboard ➔ **Project Settings** ➔ **Domains**
2. `morvix.kr` 등록 후 DNS CNAME `cname.vercel-dns.com` 연동 ➔ **기존 링크 손실 없이 100% 자동 계승!**
