@echo off
chcp 65001 > nul
echo ========================================
echo 🚀 새로운 11개 에이전트 통합 시스템
echo ========================================
echo.

cd /d "%~dp0"

echo 📋 시스템 구성:
echo   1. 메인 조율 에이전트 (전체 워크플로우 관리)
echo   2-8. 전문 에이전트들 (작가, 문법, 세계관, 역사, 독자10명, 연관성, 설정개선)
echo   9-11. 시스템 에이전트들 (품질평가, 개선실행, 데이터관리)
echo.

echo 🔄 운영 방식:
echo   • 35분 완전 사이클 (분석→검토→개선→저장)
echo   • 독자 10명 동시 다각도 평가
echo   • 1화→2화→3화 순차 처리 후 반복
echo.

set /p episodes="개선할 에피소드 번호들 (예: 1,2,3): "
set /p target="목표 점수 (예: 9.5): "

echo.
echo 🚀 새로운 시스템 시작: %episodes%화를 %target%점까지 무한 개선
echo ⏸️  중단하려면 Ctrl+C를 누르세요
echo.

python new_agent_system.py %episodes% %target%

echo.
echo 👋 새로운 에이전트 시스템이 종료되었습니다.
pause