@echo off
chcp 65001 >nul
title MORVIX SHOP - Toss Harvester Runner

echo ==========================================
echo   MORVIX SHOP OS : Toss Harvester V32
echo ==========================================
echo.

:: 가상환경이 존재할 경우 자동 활성화 (venv 폴더가 있는 경우)
if exist venv\Scripts\activate (
    echo [INFO] 가상환경(venv) 활성화 중...
    call venv\Scripts\activate
) else if exist .venv\Scripts\activate (
    echo [INFO] 가상환경(.venv) 활성화 중...
    call .venv\Scripts\activate
)

echo [INFO] 토스 쉐어링크 정밀 수집기 실행 중...
echo.

python worker/sharelink_toss_harvester.py

echo.
echo ==========================================
echo   수집 및 깃허브 자동 푸시 작업이 종료되었습니다.
echo ==========================================
pause