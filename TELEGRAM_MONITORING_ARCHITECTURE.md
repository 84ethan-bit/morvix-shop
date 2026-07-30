# 📲 MORVIX SHOP OS - 디커플링 텔레그램 관제 & 무장애 알림 아키텍처 v1.0

> **지침 수발신:** NEXORA 대표이사(CEO) ➔ Antigravity AI 시스템  
> **발효 일시:** 2026년 7월 30일  
> **상태:** **무장애 관제 모듈 연동 완료 (MONITORING ACTIVE)**  

---

## 1. 개요 및 관제 아키텍처 (Overview)

365일 무인 운영 환경에서 장애 발생 시 사람이 며칠 동안 모르고 방치되는 사고를 원천 차단하기 위해 **디커플링 텔레그램 관제 모듈**을 구축했습니다.

```text
[ 30분 단위 무인 가동 루프 ]
 토스 수집 ➔ Validation ➔ DB 저장 ➔ Git Push ➔ Vercel 배포 ➔ 배포 검증
                                                                │
                 ┌──────────────────────────────────────────────┴──────────────────────────────┐
                 ▼                                                                            ▼
        [ SUCCESS (정상) ]                                                          [ FAIL (장애 발생) ]
                 │                                                                            │
      저널 로그 전용 기록                                                            📲 텔레그램 즉시 알림
   (scratch/daemon_execution.log)                                              (Critical / Warning / Daily)
```

---

## 2. 텔레그램 발송 조건 및 규격 (Alert Specification)

### 🚨 1) Critical Alert (즉시 장애 알림)
다음 8가지 상황 발생 시 관리자에게 즉시 텔레그램 발송:
1. 토스 파트너 로그인 세션 만료
2. `sharelink.toss.im` 포털 접속 실패
3. 쉐어링크 생성/파싱 실패
4. 대표 썸네일 이미지 100% 추출 실패
5. Git Push 실패
6. Vercel 배포 실패
7. DB (`morvix_shop_db.json`) 저장/쓰기 실패
8. 프로그램 미처리 예외(Unhandled Exception) 발생

### ⚠️ 2) Warning Alert (경고 요약 알림)
- Validation 실패율 30% 이상 경고
- 신규 등록 상품 수 0개 경고
- 동일 상품 중복 등록 경고

### 📊 3) Daily Summary Report (매일 아침 09:00 KST 정기 보고)
- 24시간 동안의 **총 수집 횟수, 신규 상품 수, Validation 성공률 %, Git/Vercel 배포 성공 수, 현재 활성 상품 수(17개), 오류 건수** 7대 지표 정기 발송.

---

## 3. 디커플링 구현 모듈 (Module Files)

1. **`worker/morvix_telegram_notifier.py`**:
   - 텔레그램 Bot API 전용 통신 엔진 (`notify_critical_alert`, `notify_warning_alert`, `notify_daily_report`).
   - 수집기 코어를 1px도 건드리지 않는 완전 분리 구조.
2. **`worker/morvix_monitoring_daemon.py`**:
   - 30분 단위 무장애 헬스체크 루프 실행 및 저널 저널링.

---

## 4. 환경 변수 세팅 안내 (Setup Guide)

대표님의 텔레그램 봇으로 실시간 알림을 수신하려면 서버 환경 변수에 아래 2가지를 입력하시면 즉시 연동됩니다:
- `TELEGRAM_BOT_TOKEN`: 텔레그램 BotFather에서 발급받은 봇 토큰
- `TELEGRAM_CHAT_ID`: 알림을 수신할 대표님의 텔레그램 채팅방 ID

(환경변수 미세팅 시에도 시스템이 다운되지 않고 `scratch/daemon_execution.log` 파일에 안전 저널링됩니다.)
