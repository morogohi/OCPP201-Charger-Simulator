@echo off
REM OCPP 2.0.1 통합 실행 - Windows CMD 버전

cd /d "%~dp0"

REM 가상환경 활성화
echo [1/3] 가상환경 활성화 중...
call .venv\Scripts\activate.bat

REM 환경변수 설정
echo [2/3] 환경변수 설정 중...
set DATABASE_URL=postgresql://charger_user:admin@localhost:5432/charger_db
set OCPP_PROTOCOL_DEBUG=false

REM 검증
echo [3/3] 설정 검증 중...
python verify_setup.py

echo.
echo ========================================
echo 준비 완료! 다음 명령어로 시작하세요:
echo ========================================
echo.
echo [Terminal 1] OCPP 서버
echo   python 4_PYTHON_SOURCE\ocpp_server.py
echo.
echo [Terminal 2] GIS 대시보드
echo   python 4_PYTHON_SOURCE\gis_dashboard_api.py
echo.
echo [Terminal 3] Python 시뮬레이터
echo   python 6_PYTHON_SCRIPTS\test_simulator.py
echo.
echo 또는 가이드를 참고하세요:
echo   QUICK_START_INTEGRATED.md
echo.
pause
