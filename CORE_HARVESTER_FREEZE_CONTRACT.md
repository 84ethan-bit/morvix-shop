# 🔒 MORVIX SHOP OS - 코어 수집기 아키텍처 동결(Freeze) & 회귀 방지 헌장 v1.0

> **지침 수발신:** NEXORA 대표이사(CEO) ➔ Antigravity AI 시스템  
> **발효 일시:** 2026년 7월 30일  
> **상태:** **전면 동결 (FREEZE ACTIVE)**  

---

## 1. 현재 상태 선언 (Status Declaration)

핵심 수집 엔진(Harvester Core)은 이미 기능 실측 및 검증이 100% 완수되었습니다.

### ✅ 검증 완료 6대 핵심 기능
1. 토스 파트너 로그인 (`sharelink.toss.im/home`)
2. 토스 쉐어링크 핫딜 포털 접속
3. 쉐어링크 (`toss.im/_m/XXXX`) 1초 자동 발급
4. 실시간 할인가 (Price) 정규식 추출
5. 할인율 (Discount Rate) 정규식 추출
6. 대표 고화질 1:1 이미지 (Thumbnail) 추출

---

## 2. 문제 진단 (Regression Diagnosis)

최근 데몬, 검증 게이트, 리팩터링 과정에서 이미 검증이 끝난 코드를 무분별하게 수정하면서 다음과 같은 **회귀 버그(Regression)**가 발생했음을 명확히 확인했습니다:
- DOM 선택자 수정으로 인한 썸네일 이미지 파싱 누락
- `4.7 (499)` 평점/리뷰 문구가 가격/할인율로 잘못 긁혀오는 오파싱(Dirty Text Parsing)
- 쉐어링크 추출 시 404 예시 링크 치환 오류

이는 **"신규 기능의 부족"이 아니라 "검증된 코드를 건드려 발생한 회귀 버그"**입니다.

---

## 3. 4대 절대 금지 규칙 (Supreme Freeze Directives)

앞으로는 **핵심 수집 로직(Harvester Core)에 대한 그 어떠한 수정도 일체 엄금**합니다.

```text
[ 🚫 절대 수정 금지 (FORBIDDEN) ]
 1. 쉐어링크 추출 및 네트워크 캐치 로직 (ShareLink Extractor)
 2. 썸네일 이미지 추출 로직 (Image Selector)
 3. 가격 & 할인율 정규식 추출 로직 (Price & Discount Parser)
 4. Playwright DOM 선택자 (Playwright Selectors)
 5. Harvester Core 수집 파이프라인 (worker/sharelink_toss_harvester.py)
```

---

## 4. 허용되는 작업 영역 (Allowed Scope)

```text
[ 🟢 허용되는 작업 (ALLOWED) ]
 1. UI / UX 디자인 개편 및 레이아웃 정돈
 2. CSS 스타일링 및 인터랙티브 애니메이션
 3. 모바일 뷰포트 반응형 보완
 4. 어드민(Admin) 관리자 화면 시각화
```

---

## 5. 단계별 개발 우선순위 (Operational Priority)

```text
1순위: 기존 검증된 Harvest Core 100% 원복 및 동결 (Freeze)
  │
2순위: 메인 홈페이지 정상 출력 및 1초 직행 쉐어링크 연동 검증
  │
3순위: 24시간 무인 가동 무결성 & 무장애 안정을 위한 모니터링
  │
4순위: UI / UX 모던 디자인 시스템 고도화
  │
5순위: 관리자(Admin) 편의 기능 보완
```

본 헌장은 발효 즉시 적용되며, AI 에이전트는 향후 코어 수집기 수정 요청이나 유혹이 있더라도 본 동결 규칙을 최우선으로 준수합니다.
