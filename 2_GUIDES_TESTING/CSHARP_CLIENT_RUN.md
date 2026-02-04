# 🔷 C# 클라이언트 실행 가이드

**목표**: OCPP 서버에 C# 클라이언트 연결하여 데이터 전송

---

## 📋 사전 준비

### 필수 항목

```powershell
# 1. OCPP 서버가 실행 중인지 확인
netstat -ano | findstr ":9000"
# 결과: LISTENING이 있어야 함

# 2. .NET SDK 설치 확인
dotnet --version
# 결과: 6.0 이상이어야 함

# 3. C# 프로젝트 디렉토리 확인
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"
ls

# 결과: .csproj 파일이 있어야 함
```

---

## 🚀 Step 1: 기본 실행

### 방법 1: 기본 명령어로 실행

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

# 프로젝트 빌드 및 실행
dotnet run
```

**예상 출력:**
```
Microsoft.NET.Sdk.
Building for .NET framework...

Starting OCPP 2.0.1 Charger Simulator...

[INFO] Connecting to ws://127.0.0.1:9000
[INFO] Connected successfully
[INFO] Sending BootNotification...
[SUCCESS] BootNotification accepted
```

---

### 방법 2: 인자와 함께 실행

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

# 충전기 ID와 서버 URL 지정
dotnet run -- --charger-id CHARGER_CSHARP_001 --server ws://localhost:9000

# 또는 짧은 형태
dotnet run -- -i CHARGER_CSHARP_001 -s ws://localhost:9000
```

---

## 🎯 Step 2: 상세 실행 (단계별 확인)

### 프로젝트 직접 빌드

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

# Step 1: 빌드
echo "[Step 1] 프로젝트 빌드 중..."
dotnet build -c Release

# Step 2: 실행
echo "[Step 2] 프로젝트 실행 중..."
dotnet run -c Release -- --charger-id CHARGER_CSHARP_001
```

**예상 출력:**
```
[Step 1] 프로젝트 빌드 중...
Microsoft.NET.Sdk.
Build started...
Build completed in 5.23s

[Step 2] 프로젝트 실행 중...
Starting OCPP 2.0.1 Charger Simulator...
...
```

---

## 📊 Step 3: 다양한 시나리오 실행

### 시나리오 1: 단일 충전기 - 기본 동작

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

dotnet run -- `
    --charger-id CHARGER_CSHARP_001 `
    --server ws://localhost:9000 `
    --duration 60
```

**기대 동작:**
1. 서버 연결
2. 부팅 메시지 전송
3. 60초 동안 주기적으로 Heartbeat 전송
4. 종료

---

### 시나리오 2: 거래 포함

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

dotnet run -- `
    --charger-id CHARGER_CSHARP_002 `
    --server ws://localhost:9000 `
    --transaction `
    --meter-interval 2
```

**기대 동작:**
1. 부팅
2. 거래 시작
3. 2초마다 전력량 데이터 전송
4. 거래 종료

---

### 시나리오 3: 다중 충전기 (동시 실행)

**Terminal A:**
```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"
dotnet run -- --charger-id CHARGER_CSHARP_001
```

**Terminal B:**
```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"
dotnet run -- --charger-id CHARGER_CSHARP_002
```

**Terminal C:**
```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"
dotnet run -- --charger-id CHARGER_CSHARP_003
```

**결과:**
- 3개 충전기가 동시에 서버 연결
- 각각 독립적으로 메시지 전송
- 대시보드에 3개 충전기 모두 표시

---

## 📁 Step 4: 설정 파일로 실행

### appsettings.json 사용

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

# 설정 파일 확인
cat appsettings.json

# 설정을 기반으로 실행
dotnet run -- --config appsettings.json
```

**appsettings.json 예시:**
```json
{
  "OcppSettings": {
    "ServerUrl": "ws://localhost:9000",
    "ChargerId": "CHARGER_CSHARP_001",
    "VendorName": "CSharp Simulator",
    "ModelName": "OCPPSimulator v1.0"
  },
  "SimulationSettings": {
    "Duration": 120,
    "HeartbeatInterval": 10,
    "MeterValuesInterval": 5,
    "StartTransaction": true
  }
}
```

---

## 🔍 Step 5: 실시간 모니터링

### 방법 1: 콘솔 로그 보기

**C# 프로세스 실행 중:**
```
[INFO] 2026-01-26 10:00:00 | Connecting to server...
[INFO] 2026-01-26 10:00:01 | Connected successfully
[INFO] 2026-01-26 10:00:02 | Sending BootNotification...
[SUCCESS] 2026-01-26 10:00:03 | BootNotification accepted
...
```

### 방법 2: OCPP 서버 로그 보기 (T1)

```powershell
# 서버 터미널에서 확인
# 충전기 연결 메시지를 봐야 함
# [INFO] New charger connected: CHARGER_CSHARP_001
```

### 방법 3: 대시보드에서 확인

```
http://localhost:8000
```

**확인 항목:**
- 새로운 충전기 `CHARGER_CSHARP_001` 추가됨
- 충전기 상태 변화 (connected → charging)
- 전력량 데이터 실시간 업데이트

---

## ✅ 확인 체크리스트

### 연결 확인

- [ ] C# 클라이언트 시작
- [ ] "Connected successfully" 메시지 표시
- [ ] OCPP 서버(T1)에서 연결 메시지 표시

### 메시지 전송 확인

- [ ] "Sending BootNotification" 메시지
- [ ] "BootNotification accepted" 메시지
- [ ] Heartbeat 메시지 주기적 전송

### 거래 확인 (거래 포함 시나리오)

- [ ] "Starting transaction" 메시지
- [ ] "Transaction started successfully" 메시지
- [ ] 전력량 데이터 주기적 전송
- [ ] "Stopping transaction" 메시지

### 대시보드 확인

- [ ] http://localhost:8000 접속 가능
- [ ] 새 충전기가 충전기 목록에 추가됨
- [ ] 충전 상태가 실시간으로 업데이트됨
- [ ] 거래 기록이 표시됨

---

## 🔧 커스텀 설정

### 명령어 옵션

```powershell
dotnet run -- [옵션]

# 주요 옵션:
# --charger-id, -i      충전기 ID (기본값: SIM_001)
# --server, -s          서버 URL (기본값: ws://localhost:9000)
# --duration, -d        실행 시간(초) (기본값: 120)
# --transaction, -t     거래 시작 여부 (기본값: false)
# --meter-interval, -m  전력량 전송 간격(초) (기본값: 5)
# --vendor              공급사 이름 (기본값: CSharp Simulator)
# --model               모델 이름 (기본값: OCPPSimulator)
# --help, -h            도움말 표시
```

### 예시 조합

```powershell
# 5분 동안 거래 수행, 2초마다 전력량 전송
dotnet run -- -i CHARGER_01 -d 300 -t -m 2

# 커스텀 공급사 정보
dotnet run -- -i CHARGER_02 --vendor "Tesla" --model "Model 3"

# 장시간 테스트
dotnet run -- -i CHARGER_STRESS_TEST -d 3600 -t
```

---

## 🐛 문제 해결

### 문제 1: .NET SDK 미설치

```
❌ dotnet: The term 'dotnet' is not recognized
```

**해결:**
1. https://dotnet.microsoft.com/download 에서 .NET SDK 설치
2. PowerShell 재시작
3. `dotnet --version` 확인

---

### 문제 2: 포트 연결 실패

```
❌ WebSocket connection failed: Connection refused
```

**해결:**
```powershell
# 1. OCPP 서버 실행 확인
netstat -ano | findstr ":9000"

# 2. 서버가 없으면 실행
# Terminal 1에서:
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python ocpp_server.py
```

---

### 문제 3: 빌드 실패

```
❌ Error: project file not found
```

**해결:**
```powershell
# 올바른 디렉토리인지 확인
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

# 프로젝트 파일 확인
ls *.csproj

# 없으면 생성
dotnet new console -n OCPPSimulator
```

---

### 문제 4: 메시지 전송 안 됨

```
❌ No response from server
```

**해결:**
```powershell
# 1. 데이터베이스 확인
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 2. 서버 로그 확인 (T1 터미널)
# 오류 메시지가 있는지 확인

# 3. 방화벽 확인
# 포트 9000이 방화벽 예외에 있는지 확인
```

---

## 📊 성공 시나리오 예시

### 성공적인 단일 거래 흐름

```
[00:00] Starting OCPP 2.0.1 Charger Simulator...
[00:01] Connecting to ws://localhost:9000
[00:02] ✅ Connected successfully
[00:03] Sending BootNotification
[00:04] ✅ BootNotification accepted
[00:05] Starting transaction
[00:06] ✅ Transaction started
[00:07] Sending meter values...
[00:09] ✓ Meter value #1 sent
[00:11] ✓ Meter value #2 sent
[00:13] ✓ Meter value #3 sent
[00:15] Stopping transaction
[00:16] ✅ Transaction stopped
[00:17] ✅ Simulation completed
```

---

## 🎯 다음 단계

### 테스트 완료 후:

1. **로그 분석**
   - 콘솔 출력 검토
   - 오류 확인

2. **대시보드 확인**
   - http://localhost:8000
   - 충전기 데이터 확인
   - 통계 확인

3. **Python 클라이언트와 비교**
   - 동일한 결과인지 확인
   - 차이점 분석

4. **다중 충전기 테스트**
   - 여러 Terminal에서 동시 실행
   - 안정성 확인

---

**C# 클라이언트 준비 완료! 실행하세요!** 🚀
