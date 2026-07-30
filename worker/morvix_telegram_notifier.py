"""
=============================================================================
MORVIX SHOP OS - Decoupled Telegram Monitoring & Alerting Engine
worker/morvix_telegram_notifier.py

[핵심 기능]
1. 🚨 Critical / ⚠️ Warning / 📊 Daily Summary 텔레그램 알림 자동 발송
2. 수집기 코어(sharelink_toss_harvester.py)를 1px도 건드리지 않는 완벽 디커플링 구조
3. TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID 환경변수 바인딩 + 로깅 페일세이프
=============================================================================
"""
import sys, os, json, requests, datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Env or Config Fallbacks
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_message(text):
    """텔레그램 메시지 발송 (환경변수 세팅 시 실제 발송, 미세팅 시 로그 저널 기록)"""
    if BOT_TOKEN and CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
            res = requests.post(url, json=payload, timeout=8)
            if res.ok:
                print("📲 [TELEGRAM] 텔레그램 알림 발송 성공")
                return True
            else:
                print(f"⚠️ [TELEGRAM] 발송 실패: {res.text}")
        except Exception as e:
            print(f"⚠️ [TELEGRAM] 통신 예외 발생: {e}")
    else:
        print("ℹ️ [TELEGRAM] BOT_TOKEN/CHAT_ID 미세팅 상태 - 저널 로그로 기록됨:")
        print(text)
    return False

def notify_critical_alert(title, cause, retry_status="2 / 3", log_file="daemon_execution.log"):
    """🚨 Critical 장애 즉시 알림"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = (
        f"🚨 <b>MORVIX SHOP CRITICAL ALERT</b>\n\n"
        f"<b>시간:</b> {now_str}\n"
        f"<b>장애:</b> {title}\n"
        f"<b>원인:</b> {cause}\n"
        f"<b>자동 재시도:</b> {retry_status}\n"
        f"<b>현재 상태:</b> 운영 계속 (자동 복구 시도 중)\n"
        f"<b>로그:</b> {log_file}"
    )
    return send_telegram_message(msg)

def notify_warning_alert(title, detail):
    """⚠️ Warning 경고 알림"""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = (
        f"⚠️ <b>MORVIX SHOP WARNING</b>\n\n"
        f"<b>시간:</b> {now_str}\n"
        f"<b>경고:</b> {title}\n"
        f"<b>상세:</b> {detail}\n"
        f"<b>관리자 확인 권장</b>"
    )
    return send_telegram_message(msg)

def notify_daily_report(run_count, new_count, validation_rate, push_success, vercel_success, active_count, err_count):
    """📊 데일리 요약 리포트 (매일 아침 09:00 KST)"""
    msg = (
        f"📊 <b>MORVIX Daily Report</b>\n\n"
        f"<b>수집 횟수:</b> {run_count}회\n"
        f"<b>신규 상품:</b> {new_count}개\n"
        f"<b>Validation 성공률:</b> {validation_rate}%\n"
        f"<b>Git Push:</b> {push_success}\n"
        f"<b>Vercel:</b> {vercel_success}\n"
        f"<b>현재 활성 상품:</b> {active_count}개\n"
        f"<b>오류:</b> {err_count}건"
    )
    return send_telegram_message(msg)

if __name__ == '__main__':
    print("Testing Telegram Notifier Module...")
    notify_daily_report(48, 17, 99.2, "48/48 성공", "48/48 성공", 17, 0)
