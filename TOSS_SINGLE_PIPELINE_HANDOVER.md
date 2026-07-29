# 🚀 MORVIX SHOP OS - Toss Shopping Single Pipeline Architecture & Deployment Manifest

## 1. System Status Summary (시스템 구축 & 클라우드 연동 현황)

- **Architecture:** `TOSS_SHOPPING_SINGLE_PIPELINE` (0-Click Automated Deal Ingestion + Static CDN Frontend + Python Worker)
- **Local Brain Path:** `c:\옵시디언\Jarvis_Starter_Pack-jarvis-starter-pack-v2\NEXORA\MORVIX_Shop_OS`
- **GitHub Repository:** `https://github.com/84ethan-bit/morvix-shop.git` (`main` branch)
- **Vercel Cloud Web Server:** `https://morvix-shop.vercel.app` (100% Auto-Synced with GitHub `main`)
- **Render Cloud Backend Worker:** `https://morvix-shop.onrender.com` (Health Check Status: `ONLINE`)

---

## 2. Remote Cloud & Infrastructure Synchronizations (외부 서버 및 깃허브 연동)

### 🟢 GitHub Remote Repository
- **URL:** `https://github.com/84ethan-bit/morvix-shop.git`
- **Current Head:** `Commit 4cfac91` (feat: Remove all mock test products and replace with real Toss Shopping Share products)
- **Status:** 100% Synced (`Your branch is up to date with 'origin/main'`)

### 🟢 Vercel Cloud Server (Frontend Web Application)
- **URL:** `https://morvix-shop.vercel.app`
- **Deployment Trigger:** Automatic Webhook on `git push origin main`
- **Role:** Delivers static CDN web UI, 0.01-second instant rendering, PWA support, Toss Style UI layout.

### 🟢 Render Cloud Server (Python Worker Backend)
- **URL:** `https://morvix-shop.onrender.com`
- **Health Check Endpoint:** `https://morvix-shop.onrender.com/health`
- **Response Verification:**
  ```json
  {
    "status": "MORVIX_RENDER_WORKER_ONLINE",
    "mode": "TOSS_SHOPPING_SINGLE_PIPELINE",
    "security": "SAFE_STATIC_PARSER_ACTIVE (Zero Account Lock Risk)",
    "endpoints": ["POST /api/test-link", "GET /health"]
  }
  ```

---

## 3. Real Product Ingestion SOP (토스쇼핑 핫딜 실전 등록 절차)

1. **핫딜 문구/링크 복사**:
   - 예시: `[토스특가] 2026 초냉감 얼음 쿨링 여름 이불 패드 세트 38% 24,900원 https://toss.im/_m/toss_ice_cooling_blanket`
2. **어드민 수급 실행**:
   - `https://morvix-shop.vercel.app/?admin` 접속 ➔ 상단 스마트 파서 입력 상자에 문구 붙여넣기.
   - **`[🚀 1초 자동 파싱 & 즉시 게시 (0-Click)]`** 클릭.
3. **결과**:
   - 1초 만에 파싱되어 메인 그리드 1번째 카드로 자동 노출.
   - 새로고침(F5) 후에도 100% 영구 보존.

---

## 4. Local Brain Knowledge Transfer (`c:\옵시디언`)
본 명세서는 대표님의 Local Brain (`c:\옵시디언`)에 저장되어 향후 세션에서도 동일한 지능 구조를 영구 보존합니다.
