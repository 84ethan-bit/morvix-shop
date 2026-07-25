# 📊 MORVIX SHOP OS - Analytics Event Dictionary v1.0

> **"사용자 유입, 행동 패턴, 몰입도 및 수수료 전환 추적을 위한 트래킹 이벤트 데이터 규격"**

---

## 1. 개요 (Overview)

본 문서는 MORVIX SHOP OS 웹사이트 내에서 발생하는 모든 유저 인터랙션 및 아웃바운드 클릭 이벤트를 일관된 명명 규칙으로 정의하고 추적하기 위한 데이터 사전(Event Dictionary)입니다.

---

## 2. 코어 이벤트 정의 (Core Event Definitions)

| Event Name | 발생 시점 (Trigger Window) | 주요 수집 목적 | 필수 파라미터 (Parameters) |
| :--- | :--- | :--- | :--- |
| `page_view` | 랜딩 페이지 또는 단축 URL 랜딩 시점 | 전체 유입 트래픽 및 채널별 유입 분석 | `slug`, `category`, `referer`, `utm_source` |
| `product_click` | 상품 카드를 클릭하여 모달 상세창 오픈 시 | 상품 관심도 (CTR) 및 뷰 전환율 분석 | `slug`, `product_id`, `category`, `position` |
| `buy_click_coupang` | 모달 내 "🛒 쿠팡 최저가 확인 및 구매" 클릭 시 | 쿠팡 파트너스 개별 유입 및 아웃바운드 분석 | `slug`, `product_id`, `price`, `platform: "coupang"` |
| `buy_click_naver` | 모달 내 "🟢 네이버 쇼핑커넥트 확인 및 구매" 클릭 시 | 네이버 쇼핑커넥트 개별 유입 및 아웃바운드 분석 | `slug`, `product_id`, `price`, `platform: "naver"` |
| `share` | 상품 상세 모달 내 링크 복사 또는 SNS 공유 클릭 | 자생적 바이럴 파급력 트래킹 | `slug`, `share_platform` |
| `scroll_50` | 페이지 스크롤 깊이 50% 지점 도달 시 | 탐색 몰입도 파악 | `slug`, `viewport_height` |
| `scroll_100` | 페이지 최하단(Footer 및 전체 모음집) 도달 시 | 완독률 및 카탈로그 전체 탐색률 파악 | `slug`, `time_spent_sec` |
| `profile_visit` | SNS 바이오 프로필(Short Link)을 통해 첫 진입 시 | 숏폼 바이럴 틱톡/릴스/쇼츠 채널별 기여도 | `referer`, `channel_name`, `episode_id` |

---

## 3. 이벤트 페이로드 스키마 (Event Payload Schema Example)

```json
{
  "timestamp": "2026-07-26T00:09:00+09:00",
  "event_name": "buy_click",
  "slug": "fan001",
  "product_id": "PROD-010",
  "category": "summer",
  "episode_id": "INTERNAL_CASE_EP010",
  "referer": "instagram_reels",
  "utm_source": "ep010_shorts",
  "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X)..."
}
```

---

## 4. 데이터 활용 가이드 (Data Utilization)

- **Conversion Funnel Analytics:** `page_view` ➔ `product_click` ➔ `buy_click` 전환 파이프라인 분석
- **Content ROI Verification:** 에피소드(`episode_id`)별 생성 수수료 수익 검증 및 순위 매김
