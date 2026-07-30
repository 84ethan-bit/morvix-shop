# 🌐 MORVIX SHOP OS - 토스 파트너 포털 전 섹션 무제한 자동 동기화 정책 v1.0

> **지침 수발신:** NEXORA 대표이사(CEO) ➔ Antigravity AI 시스템  
> **발효 일시:** 2026년 7월 30일  
> **운영 원칙:** **개수 제한(9개/15개 등) 폐기 ➔ 토스 파트너 포털 내 유효 핫딜 전수 순회 동기화**  

---

## 1. 개요 및 운영 철학 (Overview)

MORVIX Shop은 단순한 "몇 개의 핫딜을 가져오는 사이트"가 아니라, **토스 파트너 포털의 전체 판매 영역을 자동 동기화하는 무장애 쇼핑 플랫폼**으로 운영합니다.

```text
토스 파트너 포털 전 판매 영역
├── 오늘만 이 가격 (today_price) ➔ 전부 수집 (12개든 20개든 전수 수집)
├── 많이 팔리는 베스트 (best_seller) ➔ 전부 수집 (47개든 100개든 전수 수집)
├── 추천 상품 (featured) ➔ 전부 수집
├── 시즌 특가 (season_special) ➔ 전부 수집
└── 신규 노출 섹션 (new_arrivals) ➔ 자동 인식 후 전부 수집
```

---

## 2. 무제한 전수 순회 수칙 (Unbounded Harvesting Directives)

1. **개수 고정 자르기 금지:**
   - 기존의 `slice(0, 15)`와 같은 고정 개수 자르기를 전면 금지합니다.
   - 오늘만 이 가격이 12개면 12개 전부, 많이 팔리는 베스트가 47개면 47개 전부, 내일 63개로 늘어나면 63개 전부를 끝까지 순회하여 수집합니다.

2. **섹션 출처 태깅 (Section Metadata Tagging):**
   각 상품에는 반드시 출처 섹션과 우선순위 메타데이터가 기록됩니다:
   ```json
   {
     "name": "CJ제일제당 햇반 라이스플랜 세트",
     "price": 39900,
     "original_price": 53865,
     "discount_rate": "42% 특가",
     "thumbnail": "https://resources-fe.toss.im/...",
     "toss_link": "https://toss.im/_m/ZIZeB1hc",
     "section": "today_price",
     "priority": 1,
     "category": "kitchen",
     "status": "ACTIVE"
   }
   ```

3. **6대 필수 저장 필드 (Mandatory Fields):**
   - `name` (상품명)
   - `price` (판매가)
   - `discount_rate` (할인율)
   - `thumbnail` (대표 이미지)
   - `toss_link` (`toss.im/_m/XXXX` 쉐어링크)
   - `section` (원본 섹션: `today_price`, `best_seller`, `season_special`, `new_arrivals`)

---

## 3. UI 렌더링 동기화 (UI Synchronization)

- **🔥 오늘만 이 가격:** `section === 'today_price'` 출처 상품 자동 동기화.
- **🏆 지금 많이 팔리는 BEST:** `section === 'best_seller'` 출처 및 중복 제거된 실시간 베스트 라인업 자동 동기화.

본 정책은 토스 파트너 포털과의 100% 실시간 무장애 자동 동기화를 위한 핵심 규정입니다.
