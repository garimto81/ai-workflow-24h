@echo off
chcp 65001 > nul
echo ====================================
echo 🚀 Classic Isekai 자동화 시스템
echo ====================================
echo.

cd /d "%~dp0"

echo 📦 필요한 패키지 설치 중...
pip install schedule watchdog > nul 2>&1

echo.
echo 🔄 자동화 시스템 시작...
echo ⏸️  종료하려면 Ctrl+C를 누르세요
echo.

python full_automation.py

echo.
echo 👋 자동화 시스템이 종료되었습니다.
pause