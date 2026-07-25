# 🚀 MORVIX SHOP OS - Master Project Handover & System Status

## 1. Project Status (프로젝트 시스템 구축 현황)

**Status:** `READY_FOR_LIVE` (🟢 v1.2.0 - 릴리즈 메타데이터 `release.json` 및 프로덕션 검증 완료)  
**Location:** `c:\옵시디언\Jarvis_Starter_Pack-jarvis-starter-pack-v2\NEXORA\MORVIX_Shop_OS`

### 📂 Core Codebase Files
- `index.html` (프리미엄 랜딩, 동적 CTA 모달, KPI 성과 대시보드, OG 메타 카드)
- `styles.css` (글래스모피즘 & 애니메이션 디자인 시스템)
- `app.js` (동적 `affiliate_links` 배열 맵핑, unified `buy_click` 이벤트 트래킹, KPI 자동 계산)
- `server.js` (쇼츠/릴스 단축 슬러그 `morvix.kr/{slug}` 리다이렉션 서버 엔진)
- `morvix_shop_db.json` (동적 제휴 배열 스키마, 통합 시계열 로그 DB)
- `release.json` (배포 버전 `v1.2.0`, 릴리즈 날짜 및 target_domain `morvix.vercel.app` 명세)
- `README.md` (아키텍처 및 구동 가이드)

### 📚 Core Governance & Architecture Documents (5대 표준 명세서)
- ✅ `MVP_CHECKLIST.md` (개발 범위 억제 및 MUST/SHOULD/LATER 기능 우선순위 기준표)
- ✅ `URL_POLICY.md` (1,000+ 상품 확장을 위한 수평적·계층적 단축 URL 네이밍 및 리다이렉션 규격)
- ✅ `PRODUCT_PUBLISHING_SOP.md` (상품 선정부터 숏폼 제작, DB 등록, 제휴 CTA 연결, 트래킹 개시까지 8단계 SOP)
- ✅ `EVENT_DICTIONARY.md` (유입, 행동 패턴, 뷰/통합 buy_click 트래킹 이벤트 표준 데이터 사전)
- ✅ `DESIGN_SYSTEM.md` (웹툰, 숏폼 에이전트, 쇼핑몰, 어드민 OS 통일 UI/UX 디자인 토큰)

---

## 2. Production Pre-Flight Checklist (배포 전 5대 검증)

* ✅ **GA4 & Clarity 바인딩:** `index.html` 내 트래킹 태그 바인딩 완료
* ✅ **OG Image URL 검증:** 카카오톡/인스타 공유용 1200x630 고해상도 메타 이미지 바인딩 완료
* ✅ **Dynamic Sitemap:** `sitemap.xml` 내 카테고리 네임스페이스 경로 전수 명시
* ✅ **Favicon Multi-Format:** SVG & PNG 호환 파비콘 바인딩 완료
* ✅ **Release Governance:** `release.json` 메타데이터 파일 동기화 완료

---

## 3. New Chat Prompt Strategy (새 채팅 가이드라인)

다음 새 채팅(MORVIX SHOP OS 전담 개발 세션) 시작 시 아래 프롬프트를 복사하여 첫 메시지로 선언하십시오:

```text
NEXORA AI

Project:
MORVIX SHOP OS

Role:
당신은 MORVIX SHOP OS의 CTO이자 Full Stack Architect이다.

목표는 단순한 링크 모음 사이트가 아닌,
MORVIX 공식 커머스 숏폼 에이전트 플랫폼을 지속적으로 확장 및 고도화하는 것이다.

개발 원칙:
- 모바일 퍼스트 (Mobile-First Optimization)
- 동적 제휴 배열 스키마 (affiliate_links Array - UI 수정 없는 무한 확장)
- 통계/이벤트 스키마 단일화 (event: buy_click, platform: coupang|naver|11st)
- 프리미엄 UX/UI (바이브 코딩 & 인터랙티브 프론트엔드)
- 관리자 KPI 대시보드 (Top Shorts, Top Product, Top Platform)

앞으로는 설계보다 실제 코드 구현 및 데이터 수집을 최우선으로 진행한다.
```
