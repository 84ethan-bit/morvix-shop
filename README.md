# 🚀 MORVIX SHOP OS v1.0.0 Architecture & Blueprint

> **The Ultimate Shortform E-Commerce Affiliate OS & Link Hub Engine**

---

## 🌟 1. System Overview

```text
Shortform Viral Content (Shorts / Reels / TikTok)
                 │
                 ▼
        Profile Short URL (e.g. morvix.kr/fan001)
                 │
                 ▼
 ┌────────────────────────────────────────────────────────┐
 │                    MORVIX SHOP OS                      │
 ├────────────────────────────────────────────────────────┤
 │ • 100만+ 바이럴 검증 라인업 & 카테고리 필터              │
 │ • 에피소드 웹툰 뷰어 & 4대 핵심 USP 카드                │
 │ • 단축 슬러그 리다이렉터 & 클릭/전환 트래커             │
 │ • Admin OS (자동 슬러그, QR, OG 메타, 전환 분석)       │
 └────────────────────────────────────────────────────────┘
                 │
                 ▼
       Coupang Partners CTA Link ➔ Purchase & Conversion!
```

---

## 🛠️ 2. Core Modules Included

1. **Frontend Landing & Link Hub (`index.html`, `styles.css`, `app.js`)**:
   - Dark mode glassmorphism UI with smooth animations
   - Category Filters: 🌟 오늘의 추천, ❄️ 여름 꿀템, 🏠 생활 꿀템, 🧹 청소, 🍳 주방, 🚗 자동차, 📦 전체
   - Interactive Product Modal with 4-USP bullet points & Coupang Partners CTA

2. **Short URL Redirector (`server.js`)**:
   - `morvix.kr/fan001` ➔ Product `PROD-010` (MORVIX 무선 파워 듀얼 서큘레이터)
   - `morvix.kr/blanket001` ➔ Product `PROD-009` (MORVIX 초냉감 얼음 이불)
   - `morvix.kr/car001` ➔ Product `PROD-008` (3초 접이식 차광 우산)
   - `morvix.kr/mosquito001` ➔ Product `PROD-002` (UV 광촉매 모기 포집기)

3. **Admin OS Management System (`admin-modal`)**:
   - **New Product Form:** Product Name, Category, Episode ID, Short Slug, Price, Subtitle, 4 USPs, Coupang Link.
   - **Click & Conversion Analytics:** Total Clicks, Conversion Rate %, Per-Slug Performance Table.

4. **Persistent JSON Database (`morvix_shop_db.json`)**:
   - Stores all product metadata, short URLs, click logs, and episode links.

---

## 🚀 3. How to Run Locally

```bash
cd MORVIX_Shop_OS
node server.js
```

Open browser at: `http://localhost:3000/` or `http://localhost:3000/fan001`
