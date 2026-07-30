# 🛑 MORVIX SHOP OS - 엄격 운영 모드 전환 및 에이전트 관망 지침 (Strict Operations Mode Directive) v1.0

> **지침 수발신:** NEXORA 대표이사(CEO) ➔ Antigravity AI 시스템  
> **발효 일시:** 2026년 7월 30일  
> **최고 운영 원칙:** **"성공했으면 아무것도 하지 않는다. 실패했을 때만 행동한다."**  

---

## 1. 운영 모드(Operations Mode) 5대 금지령 (Strict Prohibitions)

운영 모드에 진입한 현재 시점부터 회사 OS(AI 에이전트)는 다음 모든 행동을 **100% 금지**합니다:

```text
[ 🚫 회사 OS 절대 금지 사항 (FORBIDDEN IN OPERATIONS MODE) ]
 1. 새로운 정책 생성 ❌
 2. 데이터베이스(DB) 수정 및 재가공 ❌
 3. UI 및 CSS 임의 수정 ❌
 4. 코드 자동 리팩토링 ❌
 5. 시스템 아키텍처 및 구조 변경 ❌
```

회사 OS는 오직 **`Deploy ➔ Wait (배포 후 침묵 대기)`**만을 이행합니다.

---

## 2. 외부 독립 서버의 최고 작동 원칙 (External Server Golden Rule)

> **Golden Rule of Unattended Server**
>
> **"성공했으면 아무것도 하지 않는다. 실패했을 때만 행동한다."**

```text
[ ✅ 정상 성공 시 ➔ Silent Sleep ]
 • 수집 성공 ➔ Git Push ➔ 즉시 종료 (Sleep 30m)
 • GitHub Push 성공 ➔ 즉시 종료 (Sleep 30m)
 • Vercel 배포 성공 ➔ 즉시 종료 (Sleep 30m)

[ ❌ 실패 발생 시 ➔ Alert Only ]
 • 토스 포털 접속 실패 ➔ 📲 Telegram 알림
 • 파트너 로그인 세션 만료 ➔ 📲 Telegram 알림
 • Git Push 3회 재시도 실패 ➔ 📲 Telegram 알림
 • Vercel 배포 3회 재시도 실패 ➔ 📲 Telegram 알림
```

---

## 3. 최종 실서비스 운영 5단계 이행 로드맵

```text
1. UI 디자인 마감 & 동결 (Complete & Frozen)
   │
2. 외부 독점 서버 30분 무인 가동 개시
   │
3. 24시간 며칠간 무인 무장애 안착 테스트 (Silent Multi-Day Run)
   │
4. 텔레그램 장애 발생 알림 세팅 및 수신 검증
   │
5. 장애 없을 시 현 구조 그대로 365일 영구 무인 운용
```

본 지침은 MORVIX SHOP OS의 장기적 365일 무장애 안정을 위한 최고 조항으로 영구 적용됩니다.
