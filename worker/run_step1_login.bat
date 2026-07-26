@echo off
chcp 65001 > NUL
echo ========================================================
echo 🔐 MORVIX STEP 1 REAL ACCOUNT INTERACTIVE LOGIN PAIRING
echo ========================================================
echo.
echo [1] Coupang Partners Real Account Login (쿠팡 파트너스 로그인)
echo [2] Naver Shopping Connect Real Account Login (네이버 브랜드커넥트 로그인)
echo.
set /p CHOICE="Select Platform (1 for Coupang, 2 for Naver): "

if "%CHOICE%"=="1" (
    python worker/live_session_verifier/affiliate_session_manager.py login coupang
) else (
    python worker/live_session_verifier/affiliate_session_manager.py login naver
)
pause
