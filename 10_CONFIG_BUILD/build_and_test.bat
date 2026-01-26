@echo off
REM OCPP C# Simulator 빌드 및 실행 스크립트

setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║           OCPP 2.0.1 C# Simulator 빌드 및 테스트                               ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.

REM 프로젝트 디렉토리
set PROJECT_DIR=%~dp0OCPPSimulator
set BUILD_DIR=%PROJECT_DIR%\bin\Release\net8.0

echo [1/3] 의존성 복원 중...
cd /d "%PROJECT_DIR%"
dotnet restore
if errorlevel 1 (
    echo ❌ 의존성 복원 실패
    exit /b 1
)
echo ✅ 의존성 복원 완료

echo.
echo [2/3] 프로젝트 빌드 중...
dotnet build -c Release
if errorlevel 1 (
    echo ❌ 빌드 실패
    exit /b 1
)
echo ✅ 빌드 완료

echo.
echo [3/3] 테스트 실행 준비...
echo.
echo 사용 가능한 시나리오:
echo   - 1: 기본 연결 및 BootNotification
echo   - 2: 충전 세션 (에너지 추적)
echo   - 3: 다중 충전기 동시 운영
echo   - 4: 에너지 데이터 검증
echo   - 5: 스트레스 테스트
echo   - all: 모든 시나리오 실행
echo.

REM 매개변수가 있으면 해당 시나리오 실행
if "%~1"=="" (
    echo 기본값: 시나리오 1 실행
    set SCENARIO=1
) else (
    set SCENARIO=%~1
)

echo 시나리오 %SCENARIO% 실행 중...
"%BUILD_DIR%\OCPPSimulator.exe" %SCENARIO%

echo.
echo ✅ 테스트 완료!
pause
