@echo off
chcp 65001 > nul
echo ========================================
echo 🔄 무한 반복 개선 시스템
echo ========================================
echo.

cd /d "%~dp0"

echo 📝 사용법:
echo   이 스크립트는 지정된 에피소드들을 24시간 내내 개선합니다
echo.
echo 🎯 예시:
echo   1,2,3화를 목표 9.0점까지 개선: python infinite_improvement.py 1,2,3 9.0
echo   1화만 목표 9.5점까지 개선: python infinite_improvement.py 1 9.5
echo.

set /p episodes="개선할 에피소드 번호들을 입력하세요 (예: 1,2,3): "
set /p target="목표 점수를 입력하세요 (예: 9.0): "

echo.
echo 🚀 %episodes%화를 목표 %target%점까지 무한 개선을 시작합니다...
echo ⏸️  중단하려면 Ctrl+C를 누르세요
echo.

python infinite_improvement.py %episodes% %target%

echo.
echo 👋 무한 개선 시스템이 종료되었습니다.
pause