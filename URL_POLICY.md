# 🌐 MORVIX SHOP OS - URL Policy Specification v1.0

> **"1,000+ 상품 확장을 위한 수평적·계층적 단축 URL 네이밍 및 리다이렉션 규격 문서"**

---

## 1. 개요 (Overview)

MORVIX SHOP OS는 숏폼 바이럴 트래픽(Shorts/Reels/TikTok)을 쿠팡 파트너스 커머스 자산으로 전환하는 **Link Hub Engine**입니다.  
초기 단일 슬러그 방식(`/fan001`)에서 벗어나 수백~수천 개 단위의 상품 수집 시 체계적인 분류와 분석이 가능한 **카테고리 네임스페이스 규칙**을 정립합니다.

---

## 2. URL 구조 및 규칙 (URL Structure Rules)

### Standard Hierarchy
```text
https://morvix.kr/{category}/{slug_id}
```

* **Primary Category:** 상품의 상위 카테고리 식별자 (소문자 ASCII 알파벳)
* **Slug ID:** 영문 상품 키워드 + 3자리 시퀀스 넘버 (`fan001`, `blanket001` 등)

### Legacy Fallback Compatibility (하위 호환성)
기존 발행 완료된 단일 슬러그(`/fan001`, `/blanket001`)와의 호환성을 위해 302 리다이렉터는 단일 슬러그 및 계층형 URL을 모두 지원합니다.
* `morvix.kr/fan001` ➔ `morvix.kr/#summer/fan001` 자동 매핑
* `morvix.kr/summer/fan001` ➔ `morvix.kr/#summer/fan001` 자동 매핑

---

## 3. 카테고리 네임스페이스 표 (Category Namespace Table)

| Category Key | 카테고리명 | 사용 예시 URL | 비고 |
| :--- | :--- | :--- | :--- |
| `summer` | 계절/여름 꿀템 | `morvix.kr/summer/fan001` | 계절성 고전환 라인업 |
| `kitchen` | 주방/요리 | `morvix.kr/kitchen/pan001` | 조리기구, 소형가전 |
| `clean` | 청소/위생 | `morvix.kr/clean/vacuum001` | 청소용품, 소독기 |
| `car` | 차량/용품 | `morvix.kr/car/holder001` | 차광막, 차량 거치대 |
| `life` | 생활/자취 | `morvix.kr/life/desk001` | 자취생 필수템, 데스크테리어 |

---

## 4. Slug ID 네이밍 상세 규칙

1. **소문자 영문 + 숫자 조합:** 특수문자, 공백, 한글 금지 (하이픈 `-`만 허용)
2. **최대 길이지정:** 20자 이내 준수 (`fan001`, `ice-blanket001` 등)
3. **고유성 보장:** `morvix_shop_db.json` 내 `slug` 필드는 시퀀스상 유일해야 함
