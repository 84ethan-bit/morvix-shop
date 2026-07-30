# 🛡️ MORVIX SHOP OS - 365일 무장애 연속 운영 안정화 헌장 v1.0

> **지침 수발신:** NEXORA 대표이사(CEO) ➔ Antigravity AI 시스템  
> **발효 일시:** 2026년 7월 30일  
> **프로젝트 성격 전환:** **"신규 기능 개발" ➔ "365일 멈추지 않는 무장애 서비스 운영"**  

---

## 1. 현재 핵심 인프라 확보 현황 (Baseline Scope)

현재 MORVIX SHOP OS의 핵심 인프라 파이프라인은 100% 실측 및 확보 완료되었습니다.

- ✅ 토스 파트너 로그인 세션 유지
- ✅ 핫딜 목록 자동 수집
- ✅ 1초 고유 쉐어링크 (`toss.im/_m/XXXX`) 발급
- ✅ 실시간 할인가 (Price) 정규식 추출
- ✅ 할인율 (Discount Rate) 정규식 추출
- ✅ 1:1 HD 대표 썸네일 이미지 파싱
- ✅ 모바일 2열 미니멀 UI 메인 노출
- ✅ GitHub ➔ Vercel 자동 라이브 배포

---

## 2. 365일 무장애 운영 5대 로드맵 (Operational Roadmap)

```text
[1단계: 파이프라인 동결] ➔ [2단계: 72h 연속 가동 테스트] ➔ [3단계: 5대 지표 모니터링] ➔ [4단계: UI/Admin 전용 고도화] ➔ [5단계: 버그만 원복]
```

### 1단계. 배포 파이프라인 완전 동결 (Pipeline Freeze)
- 현재 정상 동작하는 수집기(`worker/sharelink_toss_harvester.py`)와 Vercel 배포 흐름을 **기준 버전(Baseline v1.0)**으로 고정합니다.
- 백엔드 수집 로직은 신규 수정을 일체 금지하며, 버그 수정 시에도 최소 범위(Hotfix)만 허용합니다.

### 2단계. 72시간 이상 연속 운영 테스트 (72h Reliability Run)
- 일정한 주기마다 **수집 ➔ DB 저장 ➔ GitHub ➔ Vercel 반영**이 끊김 없이 자동 반복되는지 검증합니다.
- **실패 횟수, 재시도 횟수, 세션 만료 여부**를 저널 로그(`scratch/daemon_execution.log`)에 기록합니다.

### 3단계. 5대 운영 핵심 지표 실시간 모니터링 (Operational KPI Monitoring)
어드민 및 대시보드를 통해 다음 5대 지표를 한눈에 모니터링합니다:
1. **마지막 수집 성공 시간** (Last Ingestion Time)
2. **현재 활성 핫딜 수** (Active Product Count)
3. **검증 실패 핫딜 수** (Validation Failure Count)
4. **최근 라이브 배포 성공 시간** (Last Deploy Success Time)
5. **토스 파트너 세션 만료 여부** (Session Validity Status)

### 4단계. 프론트엔드 UI & 어드민 UX 전용 고도화 (UI Polish Only)
- 이 단계에서는 백엔드 수집 코드를 1px도 건드리지 않고, 오직 **디자인 개선, 반응형 뷰포트 정돈, 카테고리 UX, 어드민 모니터링 시각화**에만 집중합니다.

### 5단계. 운영 중 발견된 회귀 버그만 최소 수정 (Operational Bugfix Only)
- 새 기능 추가를 전면 중단하고, 24시간 실전 가동 중 발견되는 실제 버그만 최소 단위로 즉시 해결합니다.

---

## 3. 결언 (Conclusion)

본 프로젝트의 최고 목표는 "100개의 신규 기능"이 아니라 **"365일 멈추지 않는 신뢰의 서비스"**입니다.  
안정적인 운영 기반 위에서 서비스와 디자인을 발전시키는 원칙을 철저히 준수하겠습니다.
