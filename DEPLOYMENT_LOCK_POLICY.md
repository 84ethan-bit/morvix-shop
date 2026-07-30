# 🔒 MORVIX SHOP OS - 배포 원자성 & 상태 잠금 정책 (Deployment Lock Policy) v1.0

> **지침 수발신:** NEXORA 대표이사(CEO) ➔ Antigravity AI 시스템  
> **발효 일시:** 2026년 7월 30일  
> **상태:** **원자적 상태 잠금 강제 발효 (DEPLOYMENT LOCK ACTIVE)**  

---

## 1. 개요 (Overview)

Git Push가 성공하여 Vercel 클라우드 배포가 시작된 후 다른 프로세스가 DB를 수정하거나 수집/검증/삭제 작업을 병행할 경우 **레이스 컨디션(Race Condition) 및 데이터 불일치 장애**가 발생할 위험이 있습니다.

따라서 배포 프로세스는 절대 쪼개지지 않는 **하나의 원자적(Atomic) 작업**으로 취급하며, 배포 진행 중에는 전체 시스템이 **`DEPLOYING` (Read-Only)** 상태로 완벽히 잠깁니다.

---

## 2. 10단계 원자적 상태 머신 (Atomic State Machine Sequence)

```text
① IDLE (대기)
   │
   ▼
② HARVESTING (토스 파트너 수집)
   │
   ▼
③ VALIDATING (5대 수율 검증)
   │
   ▼
④ SAVING (DB 파일 기록)
   │
   ▼
⑤ COMMITTING (Git Commit)
   │
   ▼
⑥ PUSHING (Git Push)
   │
   ▼
══════════════════════════════════════════════════════════════════════════
⑦ DEPLOYING (Vercel 배포 진행 중 - 🔒 READ ONLY LOCK)
  • DB 수정 금지 | 삭제 금지 | 추가 금지 | Validation 금지 | Harvester 재실행 금지
  • 오직 "Vercel 배포 끝났나?" 배포 성공 여부만 전용 관측
══════════════════════════════════════════════════════════════════════════
   │
   ▼
⑧ VERIFY_DEPLOY (배포 성공/실패 여부 최종 확정)
   │
   ▼
⑨ TELEGRAM_NOTIFY (결과 관제 로그/텔레그램 발송)
   │
   ▼
⑩ SLEEP (30분 무장애 잠자기)
```

---

## 3. 원자적 배포 잠금 원칙 (Deployment Lock Directives)

> **Deployment Lock Policy**
> 
> 1. Git Push가 성공하여 Vercel 배포가 시작되는 순간 시스템은 `DEPLOYING` 상태로 전환한다.
> 2. `DEPLOYING` 상태에서는 새로운 수집, DB 수정, 검증, 삭제, 생성 작업을 일체 수행하지 않는다.
> 3. 시스템은 배포 완료 여부만 모니터링하며, 완료 후 성공/실패를 기록하고 텔레그램으로 알린 뒤 `SLEEP` 상태로 전환한다.

본 정책은 데이터 무결성과 365일 무장애 가동을 위한 최고 규칙으로 엄격히 강제 적용됩니다.
