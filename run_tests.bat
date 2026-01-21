@echo off
REM OCPP 2.0.1 C# 시뮬레이터 및 Python 서버 연동 테스트 배치 스크립트

setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo   OCPP 2.0.1 C# 시뮬레이터 연동 테스트
echo ════════════════════════════════════════════════════════════════════════════════
echo.

REM 현재 디렉토리 저장
set PROJECT_DIR=%cd%

REM 파이썬 서버 실행 확인
echo [1/3] Python OCPP 서버 상태 확인...
netstat -ano | findstr ":9000" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  포트 9000에서 서버 실행 중이 아닙니다.
    echo.
    echo 다음 명령어를 다른 터미널에서 실행하세요:
    echo   cd %PROJECT_DIR%
    echo   python ocpp_server.py
    echo.
    pause
) else (
    echo ✅ Python 서버가 포트 9000에서 실행 중입니다.
)

echo.
echo [2/3] C# 시뮬레이터 빌드 확인...
if not exist "OCPP201ChargerSimulator.csproj" (
    echo.
    echo 📦 C# 프로젝트가 없습니다. 새로 생성합니다...
    echo.
    
    REM dotnet 설치 확인
    dotnet --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ .NET SDK가 설치되어 있지 않습니다.
        echo    https://dotnet.microsoft.com/download에서 다운로드하세요.
        pause
        exit /b 1
    )
    
    REM 프로젝트 생성
    dotnet new console -n OCPP201ChargerSimulator -f net6.0 -force
    cd OCPP201ChargerSimulator
    
    REM NuGet 패키지 설치
    dotnet add package WebSocketSharp
    
    REM Program.cs 업데이트
    echo 프로젝트 설정 중...
    
    cd ..
)

REM 빌드
if exist "OCPP201ChargerSimulator.csproj" (
    echo.
    echo 🔨 C# 프로젝트 빌드...
    dotnet build OCPP201ChargerSimulator.csproj -c Release
    
    if !errorlevel! neq 0 (
        echo ❌ 빌드 실패
        pause
        exit /b 1
    )
    echo ✅ 빌드 완료
) else (
    echo ⚠️  프로젝트 파일이 없습니다.
)

echo.
echo [3/3] 테스트 선택...
echo.
echo   1. 시나리오 1: 기본 연결 테스트
echo   2. 시나리오 2: 충전 세션 테스트
echo   3. 시나리오 3: 다중 충전기 테스트
echo   4. C# 시뮬레이터 실행
echo   5. Python 테스트 클라이언트 (Scenario 1)
echo   6. Python 테스트 클라이언트 (Scenario 2)
echo   7. Python 테스트 클라이언트 (Scenario 3)
echo   8. 데이터베이스 조회
echo   9. 종료
echo.

set /p CHOICE="선택 (1-9): "

if "%CHOICE%"=="1" goto scenario1
if "%CHOICE%"=="2" goto scenario2
if "%CHOICE%"=="3" goto scenario3
if "%CHOICE%"=="4" goto run_csharp
if "%CHOICE%"=="5" goto python_test1
if "%CHOICE%"=="6" goto python_test2
if "%CHOICE%"=="7" goto python_test3
if "%CHOICE%"=="8" goto db_query
if "%CHOICE%"=="9" goto end

echo ❌ 잘못된 선택입니다.
pause
goto end

:scenario1
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo [시나리오 1] 기본 연결 및 BootNotification (5초)
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo 예상 결과:
echo   ✅ 서버 연결 성공
echo   ✅ BootNotification 전송
echo   ✅ Heartbeat 시작
echo.
if exist "bin\Release\net6.0\OCPP201ChargerSimulator.exe" (
    start "OCPP Simulator" cmd /k "bin\Release\net6.0\OCPP201ChargerSimulator.exe scenario1"
) else (
    echo 📥 Python 테스트 클라이언트로 실행합니다...
    python test_csharp_integration.py 1
)
pause
goto end

:scenario2
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo [시나리오 2] 충전 세션 (30초)
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo 예상 결과:
echo   ✅ TransactionEvent Started 전송
echo   ✅ 에너지 누적 (0 → 20.15 kWh)
echo   ✅ TransactionEvent Ended 전송
echo.
if exist "bin\Release\net6.0\OCPP201ChargerSimulator.exe" (
    start "OCPP Simulator" cmd /k "bin\Release\net6.0\OCPP201ChargerSimulator.exe scenario2"
) else (
    echo 📥 Python 테스트 클라이언트로 실행합니다...
    python test_csharp_integration.py 2
)
pause
goto end

:scenario3
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo [시나리오 3] 다중 충전기 (45초)
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo 예상 결과:
echo   ✅ 3개 충전기 동시 연결
echo   ✅ 총 250kW 동시 전력 소비
echo   ✅ 각 충전기 독립적 이벤트 처리
echo.
if exist "bin\Release\net6.0\OCPP201ChargerSimulator.exe" (
    start "OCPP Simulator" cmd /k "bin\Release\net6.0\OCPP201ChargerSimulator.exe scenario3"
) else (
    echo 📥 Python 테스트 클라이언트로 실행합니다...
    python test_csharp_integration.py 3
)
pause
goto end

:run_csharp
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo C# 시뮬레이터 실행
echo ════════════════════════════════════════════════════════════════════════════════
echo.

if not exist "bin\Release\net6.0\OCPP201ChargerSimulator.exe" (
    echo 🔨 먼저 빌드를 수행합니다...
    dotnet build OCPP201ChargerSimulator.csproj -c Release
)

if exist "bin\Release\net6.0\OCPP201ChargerSimulator.exe" (
    start "OCPP Simulator" cmd /k "bin\Release\net6.0\OCPP201ChargerSimulator.exe"
    echo ✅ 시뮬레이터가 시작되었습니다.
) else (
    echo ❌ 시뮬레이터 실행 파일을 찾을 수 없습니다.
)

pause
goto end

:python_test1
echo.
echo Python 테스트 클라이언트 - 시나리오 1
python test_csharp_integration.py 1
pause
goto end

:python_test2
echo.
echo Python 테스트 클라이언트 - 시나리오 2
python test_csharp_integration.py 2
pause
goto end

:python_test3
echo.
echo Python 테스트 클라이언트 - 시나리오 3
python test_csharp_integration.py 3
pause
goto end

:db_query
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo 데이터베이스 조회
echo ════════════════════════════════════════════════════════════════════════════════
echo.

python -c "
import psycopg2
from datetime import datetime, timedelta

try:
    conn = psycopg2.connect(
        host='localhost',
        database='charger_db',
        user='charger_user',
        password='admin'
    )
    cur = conn.cursor()
    
    # 최근 거래 조회
    print('[최근 거래 기록 (최근 30분)]')
    print('=' * 100)
    cur.execute('''
        SELECT charger_id, transaction_id, energy_consumed, cost, duration_seconds, start_time
        FROM charger_usage_log
        WHERE start_time > NOW() - INTERVAL '30 minutes'
        ORDER BY start_time DESC
        LIMIT 20
    ''')
    
    for row in cur.fetchall():
        charger_id, tid, energy, cost, duration, start_time = row
        print(f'  {charger_id}: {energy:.2f}kWh, ₩{cost:.0f}, {duration}초, {start_time}')
    
    print()
    
    # 충전기별 통계
    print('[충전기별 오늘 통계]')
    print('=' * 100)
    cur.execute('''
        SELECT charger_id, COUNT(*) as transactions, SUM(energy_consumed) as total_energy, SUM(cost) as total_cost
        FROM charger_usage_log
        WHERE DATE(start_time) = CURRENT_DATE
        GROUP BY charger_id
        ORDER BY charger_id
    ''')
    
    for row in cur.fetchall():
        charger_id, trans, energy, cost = row
        if energy:
            print(f'  {charger_id}: {trans}건, {energy:.2f}kWh, ₩{cost:.0f}')
    
    conn.close()
    print()
    print('✅ 조회 완료')
    
except Exception as e:
    print(f'❌ 오류: {e}')
    print()
    print('데이터베이스 연결 정보:')
    print('  Host: localhost')
    print('  Database: charger_db')
    print('  User: charger_user')
    print('  Password: admin')
"

pause
goto end

:end
echo.
echo 종료합니다.
endlocal
