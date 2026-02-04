# C# OCPP 시뮬레이터 - 실행 매뉴얼 🚀

## 📋 사전 요구사항 확인

```powershell
# 1. .NET SDK 설치 확인
dotnet --version
# 출력: 6.0.xxx 이상이어야 함

# 2. 작업 디렉토리 확인
cd c:\Project\OCPP201\(P2M)
ls OCPPSimulator

# 3. Python 서버 확인
python --version
# 출력: 3.x 버전

# 4. PostgreSQL 확인
psql --version
# 출력: psql (PostgreSQL) 14.x 이상
```

---

## 🛠️ 빌드 방법 (3가지)

### 방법 1️⃣: PowerShell 자동화 스크립트 (권장)

```powershell
# 프로젝트 폴더 이동
cd c:\Project\OCPP201\(P2M)

# 자동 빌드 및 실행
.\build_and_run.ps1

# 특정 시나리오만 실행
.\build_and_run.ps1 1          # 시나리오 1
.\build_and_run.ps1 2          # 시나리오 2
.\build_and_run.ps1 all        # 모든 시나리오
```

**스크립트 내용:**
```powershell
param([string]$scenario = "all")

Write-Host "🔨 Building C# OCPP Simulator..." -ForegroundColor Green
dotnet build OCPPSimulator -c Release

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
    
    Write-Host "`n🚀 Running Scenario: $scenario" -ForegroundColor Yellow
    if ($scenario -eq "all") {
        dotnet run --project OCPPSimulator --no-build -c Release all
    } else {
        dotnet run --project OCPPSimulator --no-build -c Release $scenario
    }
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
}
```

---

### 방법 2️⃣: 배치 파일 (Windows CMD)

```batch
@echo off
cd /d c:\Project\OCPP201(P2M)

echo [*] Building C# OCPP Simulator...
dotnet build OCPPSimulator -c Release

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [+] Build successful!
    echo [*] Running tests...
    dotnet run --project OCPPSimulator --no-build -c Release all
) else (
    echo [-] Build failed!
    exit /b 1
)

pause
```

**실행:**
```batch
call build_and_test.bat
```

---

### 방법 3️⃣: 직접 명령어 (수동)

```powershell
# 1단계: 프로젝트 폴더 이동
cd c:\Project\OCPP201\(P2M)

# 2단계: 빌드
dotnet build OCPPSimulator -c Release

# 3단계: 디버그 모드로 실행 (테스트)
dotnet run --project OCPPSimulator -- 2

# 또는 릴리스 모드로 실행 (프로덕션)
dotnet run --project OCPPSimulator --no-build -c Release 2
```

---

## 📊 시나리오별 실행

### 시나리오 1: 기본 연결 (5초)

```powershell
# PowerShell
dotnet run --project OCPPSimulator -- 1

# 또는
.\build_and_run.ps1 1
```

**예상 출력:**
```
[연결] emart_jeju_01에 연결 중...
✓ WebSocket 연결 성공
[BootNotification 전송]
BootNotification 응답 수신

[✓] 시나리오 1 완료 - 기본 연결 테스트
실행 시간: 5.23초
```

**검증 항목:**
- ✅ WebSocket 연결 성공
- ✅ BootNotification 메시지 전송
- ✅ 서버에서 응답 수신
- ✅ Heartbeat 루프 시작

---

### 시나리오 2: 충전 세션 (30초)

```powershell
dotnet run --project OCPPSimulator -- 2
```

**예상 출력:**
```
[연결] emart_jeju_01에 연결 중...
✓ WebSocket 연결 성공
[BootNotification 전송]

[시작] 충전 세션 시작...
[TransactionEvent - Started]
  에너지: 0.00 kWh
  상태: Preparing → Charging

[5초 경과] TransactionEvent - Updated
  에너지: 0.14 kWh
  상태: Charging
  (비용: 21원)

[10초 경과] TransactionEvent - Updated
  에너지: 0.28 kWh
  상태: Charging
  (비용: 42원)

[15초 경과] TransactionEvent - Updated
  에너지: 0.42 kWh
  상태: Charging
  (비용: 63원)

[20초 경과] TransactionEvent - Updated
  에너지: 0.56 kWh
  상태: Charging
  (비용: 84원)

[종료] 충전 세션 종료...
[TransactionEvent - Ended]
  에너지: 0.56 kWh (최종)
  비용: 84원

[✓] 시나리오 2 완료
실행 시간: 30.45초
```

**검증 항목:**
- ✅ Started 이벤트에서 에너지 = 0.00 kWh
- ✅ Updated 이벤트들에서 에너지 증가
- ✅ Ended 이벤트에서 최종 에너지 저장
- ✅ 비용이 정확하게 계산 (에너지 × 150원/kWh)
- ✅ 데이터베이스에 기록됨

---

### 시나리오 3: 다중 충전기 (40초)

```powershell
dotnet run --project OCPPSimulator -- 3
```

**예상 출력:**
```
[다중 충전기 테스트] 3개 충전기 동시 실행

[충전기 1: emart_jeju_01 (100kW)]
  연결 중...
  [시작] 2시간 충전 시뮬레이션
  ...

[충전기 2: emart_jeju_02 (100kW)]
  연결 중...
  [시작] 2시간 충전 시뮬레이션
  ...

[충전기 3: emart_shinjeju_01 (50kW)]
  연결 중...
  [시작] 2시간 충전 시뮬레이션
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[결과 요약]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

충전기 1 (emart_jeju_01):
  - 최대 전력: 100 kW
  - 누적 에너지: 1.12 kWh
  - 예상 비용: 168원
  - 실행 시간: 40초

충전기 2 (emart_jeju_02):
  - 최대 전력: 100 kW
  - 누적 에너지: 1.12 kWh
  - 예상 비용: 168원
  - 실행 시간: 40초

충전기 3 (emart_shinjeju_01):
  - 최대 전력: 50 kW
  - 누적 에너지: 0.56 kWh
  - 예상 비용: 84원
  - 실행 시간: 40초

[✓] 시나리오 3 완료 - 다중 충전기
총 실행 시간: 40.67초
```

**검증 항목:**
- ✅ 3개 충전기 동시 연결
- ✅ 각 충전기별 에너지 누적
- ✅ 충전기별 전력 차이 반영 (100kW vs 50kW)
- ✅ 동시 데이터베이스 저장

---

### 시나리오 4: 에너지 데이터 검증 (10초)

```powershell
dotnet run --project OCPPSimulator -- 4
```

**예상 출력:**
```
[에너지 데이터 검증 시나리오]

[단계 1] 초기 에너지: 0.00 kWh
  TransactionEvent (Started)
  값 검증: ✓

[단계 2] 첫 번째 업데이트: 0.50 kWh
  TransactionEvent (Updated)
  값 검증: ✓
  증가량: 0.50 kWh

[단계 3] 두 번째 업데이트: 1.00 kWh
  TransactionEvent (Updated)
  값 검증: ✓
  증가량: 0.50 kWh

[단계 4] 최종 값: 1.50 kWh
  TransactionEvent (Ended)
  값 검증: ✓
  증가량: 0.50 kWh

[✓] 시나리오 4 완료
에너지 경로 검증:
  ✓ transactionData 추출
  ✓ chargingPeriods[0] 접근
  ✓ dimensions[] 배열 파싱
  ✓ "Energy.Active.Import.Register" 찾음
  ✓ Wh → kWh 변환
```

**검증 항목:**
- ✅ 에너지 값이 명시적으로 설정됨
- ✅ 단계별 증가 검증
- ✅ 최종 값 일치

---

### 시나리오 5: 스트레스 테스트 (40초)

```powershell
dotnet run --project OCPPSimulator -- 5
```

**예상 출력:**
```
[스트레스 테스트] 5개 트랜잭션 반복 실행

[트랜잭션 1/5]
  - 연결 시간: 0.5초
  - 충전 시간: 6초
  - 에너지: 0.17 kWh
  - 상태: ✓ 성공

[트랜잭션 2/5]
  - 연결 시간: 0.5초
  - 충전 시간: 6초
  - 에너지: 0.17 kWh
  - 상태: ✓ 성공

[트랜잭션 3/5]
  - 연결 시간: 0.5초
  - 충전 시간: 6초
  - 에너지: 0.17 kWh
  - 상태: ✓ 성공

[트랜잭션 4/5]
  - 연결 시간: 0.5초
  - 충전 시간: 6초
  - 에너지: 0.17 kWh
  - 상태: ✓ 성공

[트랜잭션 5/5]
  - 연결 시간: 0.5초
  - 충전 시간: 6초
  - 에너지: 0.17 kWh
  - 상태: ✓ 성공

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[성능 요약]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  성공한 트랜잭션: 5개
  실패한 트랜잭션: 0개
  평균 시간: 6.5초/트랜잭션
  총 에너지: 0.85 kWh
  총 비용: 127.5원
```

**검증 항목:**
- ✅ 모든 트랜잭션 성공
- ✅ 재연결 안정성
- ✅ 반복 에너지 누적

---

## 🔌 Python 서버와 통합 테스트

### 1단계: Python 서버 시작

```powershell
# 터미널 1: Python OCPP 서버 실행
python ocpp_server.py

# 출력:
# [INFO] OCPP Server listening on ws://localhost:9000
# [INFO] Server started. Press Ctrl+C to stop.
```

### 2단계: C# 시뮬레이터 실행

```powershell
# 터미널 2: C# 클라이언트 실행
.\build_and_run.ps1 2

# 또는
dotnet run --project OCPPSimulator -- 2
```

### 3단계: 서버 로그 확인

**Python 서버 터미널에서 보이는 로그:**
```
[WebSocket] Client connected: emart_jeju_01
[2026-01-21 10:30:45] BootNotification received
  → Charging Station: CSharpSimulator
  → Serial: SN-emart_jeju_01-001

[2026-01-21 10:30:47] TransactionEvent (Started)
  → transactionId: txn_001
  → energy: 0.00 kWh
  → status: Preparing

[2026-01-21 10:30:52] TransactionEvent (Updated)
  → transactionId: txn_001
  → energy: 0.14 kWh
  → status: Charging
  ✓ Saved to database

[2026-01-21 10:30:57] TransactionEvent (Updated)
  → transactionId: txn_001
  → energy: 0.28 kWh
  → status: Charging
  ✓ Saved to database

[WebSocket] Client disconnected: emart_jeju_01
```

---

## 💾 데이터베이스 검증

### 데이터 확인

```powershell
# Python 검증 스크립트 실행
python verify_energy_data.py

# 출력:
# ✓ Database connected
# ✓ Found 5 new records
#
# Recent transactions:
# ┌──────────────────┬────────────────┬─────────────────┐
# │ charger_id       │ energy_deliver │ total_charge    │
# ├──────────────────┼────────────────┼─────────────────┤
# │ emart_jeju_01    │ 0.56 kWh       │ 84.0 원         │
# │ emart_jeju_02    │ 1.12 kWh       │ 168.0 원        │
# │ emart_shinjeju_01│ 0.28 kWh       │ 42.0 원         │
# └──────────────────┴────────────────┴─────────────────┘
```

### SQL 직접 조회

```powershell
# PostgreSQL 직접 접속
psql -U postgres -d charger_db -c "
  SELECT charger_id, transaction_id, energy_delivered, total_charge
  FROM charger_usage_log
  WHERE created_at > NOW() - INTERVAL '5 minutes'
  ORDER BY created_at DESC
  LIMIT 10;
"

# 출력:
#        charger_id       │ transaction_id │ energy_delivered │ total_charge
# ──────────────────────┼─────────────────┼──────────────────┼──────────────
#  emart_jeju_01         │ txn_001         │             0.56 │           84
#  emart_jeju_02         │ txn_002         │             1.12 │          168
#  emart_shinjeju_01     │ txn_003         │             0.28 │           42
```

---

## ⚠️ 자주 나는 오류 및 해결

### 오류 1: "Unable to connect to server"

```
❌ [ERROR] Unable to connect: Connection refused
```

**원인:** Python 서버가 실행 중이 아님

**해결:**
```powershell
# 터미널에서 Python 서버 시작
python ocpp_server.py

# 서버가 포트 9000에 수신 중인지 확인
netstat -ano | findstr :9000

# PowerShell 확인 명령
Get-NetTCPConnection -LocalPort 9000
```

---

### 오류 2: "Build failed"

```
❌ System.Net.WebSockets not found
```

**원인:** .NET 프레임워크 버전 문제

**해결:**
```powershell
# .NET SDK 설치 확인
dotnet --version

# 필요하면 최신 버전 설치
# https://dotnet.microsoft.com/download

# 프로젝트 정리 후 재빌드
dotnet clean OCPPSimulator
dotnet build OCPPSimulator -c Release
```

---

### 오류 3: "Energy data not found in database"

```
❌ No records found in charger_usage_log
```

**원인:** 
- Python 서버가 데이터를 저장하지 못함
- 데이터베이스 연결 실패

**해결:**
```powershell
# PostgreSQL 연결 확인
psql -U postgres -d charger_db -c "SELECT 1;"

# 서버 로그에서 데이터베이스 오류 확인
# ocpp_server.py의 handle_transaction_event() 함수 확인

# 테이블 존재 확인
psql -U postgres -d charger_db -c "\d charger_usage_log"

# 필요하면 테이블 재생성
python -c "
from your_db_module import init_db
init_db()
"
```

---

### 오류 4: "WebSocket subprotocol negotiation failed"

```
❌ SubProtocolError: Server did not select an OCPP subprotocol
```

**원인:** 서버가 "ocpp2.0.1" 서브프로토콜을 지원하지 않음

**해결:**
```csharp
// OCPPClient.cs 수정
var clientOptions = new ClientWebSocketOptions();
clientOptions.AddSubProtocol("ocpp2.0.1");
// 또는
clientOptions.AddSubProtocol("ocpp2.0");
```

---

## 📈 성능 최적화

### 1. 릴리스 모드로 실행 (권장)

```powershell
# 디버그 모드 (느림)
dotnet run --project OCPPSimulator -- 2

# 릴리스 모드 (빠름, 권장)
dotnet run --project OCPPSimulator --no-build -c Release -- 2

# 직접 실행 파일 (가장 빠름)
.\OCPPSimulator\bin\Release\net6.0\OCPPSimulator.exe 2
```

### 2. 메모리 최적화

```csharp
// OCPPClient.cs에서 메모리 누수 방지
private async Task CleanupAsync()
{
    // WebSocket 연결 종료
    if (webSocket?.State == WebSocketState.Open)
    {
        await webSocket.CloseAsync(
            WebSocketCloseStatus.NormalClosure,
            "Closing",
            CancellationToken.None);
    }
    
    // 리소스 해제
    webSocket?.Dispose();
    cancellationTokenSource?.Cancel();
}
```

### 3. 동시 처리 최적화

```csharp
// Program.cs에서 병렬 처리
var tasks = new Task[]
{
    TestScenario3Async()  // 3개 충전기 동시
};

await Task.WhenAll(tasks);  // 모두 완료 대기
```

---

## 📚 고급 사용법

### 커스텀 시나리오 작성

```csharp
// Program.cs에 추가
async Task TestCustomScenarioAsync()
{
    var charger = new OCPPClient("custom_charger_01", maxPower: 150);
    
    try
    {
        await charger.ConnectAsync();
        
        // 커스텀 로직
        for (int i = 0; i < 5; i++)
        {
            await charger.SendTransactionEventAsync("Updated", 0.1 * i);
            await Task.Delay(2000);
        }
        
        await charger.DisconnectAsync();
    }
    catch (Exception ex)
    {
        Console.Error.WriteLine($"Error: {ex.Message}");
    }
}
```

---

### 고급 예제 실행

```powershell
# AdvancedExamples.cs의 예제 들 중 하나 선택
# Program.cs에서 메인 메서드 수정:

async Task Main()
{
    // 기존 시나리오 대신 고급 예제 실행
    await AdvancedExamples.Example5_PerformanceBenchmarkAsync();
}

# 재빌드 및 실행
dotnet run --project OCPPSimulator --no-build -c Release
```

---

## ✅ 전체 테스트 체크리스트

```
[ ] 1. 사전 요구사항 확인
    [ ] .NET SDK 설치 (6.0+)
    [ ] Python 설치 (3.x)
    [ ] PostgreSQL 설치
    [ ] 프로젝트 폴더 접근 가능

[ ] 2. 빌드 테스트
    [ ] dotnet build 성공
    [ ] 컴파일 오류 없음
    [ ] Release 빌드 가능

[ ] 3. 시나리오 1 (기본 연결)
    [ ] 서버 연결 성공
    [ ] BootNotification 전송됨
    [ ] Heartbeat 작동

[ ] 4. 시나리오 2 (충전 세션)
    [ ] 에너지 0 → 0.56 kWh
    [ ] 비용 계산 (84원)
    [ ] 데이터베이스 저장됨

[ ] 5. 시나리오 3 (다중 충전기)
    [ ] 3개 충전기 동시 실행
    [ ] 각 충전기별 에너지 누적
    [ ] 병렬 처리 정상

[ ] 6. 시나리오 4 (에너지 검증)
    [ ] 0 → 0.5 → 1.0 → 1.5 kWh
    [ ] 데이터 경로 검증

[ ] 7. 시나리오 5 (스트레스 테스트)
    [ ] 5개 트랜잭션 모두 성공
    [ ] 안정성 검증

[ ] 8. 데이터베이스 검증
    [ ] 에너지 값 저장됨
    [ ] 비용 계산 정확함
    [ ] 타임스탬프 기록됨

[ ] 9. 에러 처리
    [ ] 서버 재시작 시 재연결
    [ ] 네트워크 오류 처리
    [ ] Graceful 종료
```

---

**이제 C# 시뮬레이터를 바로 실행할 수 있습니다!** 🎉

**빠른 시작:**
```powershell
cd c:\Project\OCPP201\(P2M)
.\build_and_run.ps1 2
```
