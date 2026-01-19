@echo off
REM PostgreSQL 설치 및 환경 설정 검증 스크립트
REM Windows CMD/PowerShell 공용

setlocal enabledelayedexpansion

echo.
echo ====================================================================
echo   PostgreSQL 설치 및 환경 설정 검증
echo ====================================================================
echo.

REM PostgreSQL 설치 경로 확인
set "PG_BIN=C:\Program Files\PostgreSQL\18\bin"
set "PG_PSQL=%PG_BIN%\psql.exe"

echo [1단계] PostgreSQL 설치 확인
echo ────────────────────────────────────────────────────────────────
if exist "%PG_PSQL%" (
    echo  ✓ PostgreSQL 설치됨: %PG_BIN%
) else (
    echo  ✗ PostgreSQL 설치되지 않음
    echo    경로: %PG_BIN%
    pause
    exit /b 1
)
echo.

REM psql 버전 확인
echo [2단계] PostgreSQL 버전 확인
echo ────────────────────────────────────────────────────────────────
"%PG_PSQL%" --version
if errorlevel 1 (
    echo  ✗ PostgreSQL 버전 확인 실패
    pause
    exit /b 1
)
echo.

REM 현재 환경변수 확인
echo [3단계] 현재 환경변수 확인
echo ────────────────────────────────────────────────────────────────

if defined DATABASE_URL (
    echo  ✓ DATABASE_URL 설정됨: !DATABASE_URL!
) else (
    echo  ✗ DATABASE_URL 미설정
)
echo.

REM 데이터베이스 연결 테스트
echo [4단계] 데이터베이스 연결 테스트
echo ────────────────────────────────────────────────────────────────

if not defined DATABASE_URL (
    set "DATABASE_URL=postgresql://charger_user:admin@localhost:5432/charger_db"
    echo  임시로 DATABASE_URL 설정: !DATABASE_URL!
)

"%PG_PSQL%" -U charger_user -d charger_db -h localhost -c "SELECT version();" > nul 2>&1

if errorlevel 1 (
    echo  ✗ 데이터베이스 연결 실패
    echo    다음을 확인하세요:
    echo    - PostgreSQL 서버가 실행 중인지 확인
    echo    - 사용자명/암호 확인 (charger_user / admin)
    echo    - 포트 5432가 열려있는지 확인
) else (
    echo  ✓ 데이터베이스 연결 성공
    "%PG_PSQL%" -U charger_user -d charger_db -h localhost -c "SELECT version();"
)
echo.

REM PATH 설정 확인
echo [5단계] PATH 설정 확인
echo ────────────────────────────────────────────────────────────────
echo %PATH% | find "%PG_BIN%" > nul

if errorlevel 1 (
    echo  ⚠ PostgreSQL PATH가 설정되지 않았습니다
    echo  다음 명령어로 설정하세요 (PowerShell 관리자 모드):
    echo.
    echo  $pgBin = "C:\Program Files\PostgreSQL\18\bin"
    echo  [Environment]::SetEnvironmentVariable^(
    echo      "PATH",
    echo      "$^([Environment]::GetEnvironmentVariable('PATH', 'Machine'));$pgBin",
    echo      "Machine"
    echo  ^)
) else (
    echo  ✓ PostgreSQL PATH 설정됨
)
echo.

echo ====================================================================
echo   검증 완료
echo ====================================================================
echo.
echo 실행 방법:
echo   1. API 서버: python gis_dashboard_api.py
echo   2. 대시보드: http://localhost:8000/docs
echo.

pause
