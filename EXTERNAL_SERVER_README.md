# MORVIX Shop OS - External Server Architecture
# =============================================
# 외부 서버가 이 README 1개만 읽으면 365일 무인 운영 가능

## 역할 분리 (최종 확정)

| 주체 | 역할 |
|------|------|
| **외부 서버** | 토스 수집 → DB 생성 → Git Push → Sleep → 반복 |
| **GitHub** | Push 수신만 (토스 접속 절대 없음) |
| **Vercel** | 배포만 (토스 접속 절대 없음) |
| **Telegram** | 장애 시에만 알림 |
| **회사 OS** | 최초 배포 후 개입 없음 |

---

## 외부 서버 실행법 (OS 무관 - 단 1개 명령어)

```bash
python worker/external_server_daemon.py
```

이것만 실행하면:
- 30분마다 자동으로 토스 접속 → 수집 → Git Push → Vercel 배포
- 장애 발생 시 Telegram 자동 알림
- 성공 시 아무 알림 없이 조용히 반복

---

## 토스 파트너 로그인 세션 준비 (최초 1회만)

```bash
python worker/sharelink_toss_harvester.py --save-session
```

브라우저가 열리면 토스 파트너 로그인 완료 → 세션 자동 저장 (`scratch/toss_sharelink_session.json`)

---

## 데이터 흐름

```
외부 서버
  └─ sharelink.toss.im 접속
  └─ 상품 수집 (오늘만 이 가격 전체 + BEST 전체)
  └─ 검증 (이미지/가격/할인율/쉐어링크)
  └─ morvix_shop_db.json 생성
  └─ git push origin main
        ↓
GitHub (저장소만)
        ↓
Vercel (배포만) → morvix-shop.vercel.app
        ↓
사용자 홈페이지 (JSON 읽어서 화면 출력)
```
