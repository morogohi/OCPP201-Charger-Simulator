# 🚀 실시간 서버 실행 및 클라이언트 테스트 가이드

**목표**: OCPP 서버 실행 → Python/C# 클라이언트 연결 → 대시보드 실시간 모니터링

**소요시간**: 20-30분 (전체 프로세스)

---

## 📋 준비 사항 확인

### 필수 조건

```powershell
# 1. PostgreSQL 실행 확인
Get-Service postgresql* | Where-Object { $_.Status -eq 'Running' }
# 결과: State Running이면 OK

# 2. 데이터베이스 확인
psql -U charger_user -d charger_db -c "SELECT 1"
# 결과: 1이 나오면 OK

# 3. 포트 사용 확인 (서버가 사용할 포트)
netstat -ano | findstr "9000\|8000\|3000"
# 결과: LISTENING이 없어야 함 (포트가 비어있어야 함)
```

---

## 🎯 전체 실행 계획

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: 터미널 4개 열기                                 │
│  ├─ T1: OCPP WebSocket 서버                            │
│  ├─ T2: REST API 서버                                  │
│  ├─ T3: Python 클라이언트                               │
│  └─ T4: 모니터링 (선택사항)                              │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│  Step 2: 서버 실행 확인                                  │
│  ├─ T1에서 OCPP 서버 실행 (포트 9000)                    │
│  ├─ T2에서 REST API 서버 실행 (포트 8000)               │
│  └─ 서버가 시작되었다는 메시지 확인                        │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│  Step 3: 대시보드 접속                                   │
│  └─ http://localhost:8000 브라우저로 열기               │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│  Step 4: 클라이언트 실행                                 │
│  ├─ T3에서 Python 클라이언트 실행                        │
│  └─ OR C# 클라이언트 실행                               │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│  Step 5: 실시간 모니터링                                │
│  ├─ 클라이언트 메시지 확인 (T3)                         │
│  ├─ 서버 로그 확인 (T1)                                 │
│  └─ 대시보드 데이터 확인 (브라우저)                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Step 1: 터미널 4개 준비

### Terminal 1: OCPP 서버
```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1

echo "T1: OCPP WebSocket 서버 터미널"
# 아직 실행하지 않음. Step 2에서 실행
```

### Terminal 2: REST API/GIS 대시보드 서버
```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1

echo "T2: REST API & GIS 대시보드 서버 터미널"
# 아직 실행하지 않음. Step 2에서 실행
```

### Terminal 3: Python 클라이언트
```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1

echo "T3: Python 클라이언트 실행 터미널"
# 아직 실행하지 않음. Step 4에서 실행
```

### Terminal 4: 모니터링 (선택사항)
```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1

echo "T4: 실시간 데이터 모니터링"
# 선택사항이지만, 권장함
```

---

## 🌐 Step 2: 서버 실행

### Step 2-1: OCPP WebSocket 서버 실행 (T1)

**Terminal 1에서 실행:**

```powershell
# OCPP 서버 실행
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python ocpp_server.py
```

**예상 출력:**
```
2026-01-26 10:00:00 | INFO     | Server started
2026-01-26 10:00:00 | INFO     | WebSocket listening on ws://0.0.0.0:9000
```

✅ **확인**: `WebSocket listening on ws://0.0.0.0:9000` 메시지가 나오면 성공!

---

### Step 2-2: REST API & GIS 대시보드 서버 실행 (T2)

**Terminal 2에서 실행:**

```powershell
# REST API 서버 실행
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python gis_dashboard_api.py
```

**예상 출력:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **확인**: `Uvicorn running on http://0.0.0.0:8000` 메시지가 나오면 성공!

---

### Step 2-3: 포트 확인 (T4 또는 별도 터미널)

```powershell
# 포트 리스닝 확인
netstat -ano | findstr "9000\|8000"

# 또는 PowerShell로 확인
$ports = 9000, 8000
foreach($port in $ports) {
    $listener = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
    if ($listener.Port -contains $port) {
        Write-Host "✅ 포트 $port: LISTENING" -ForegroundColor Green
    } else {
        Write-Host "❌ 포트 $port: 미사용" -ForegroundColor Red
    }
}
```

**예상 결과:**
```
✅ 포트 9000: LISTENING
✅ 포트 8000: LISTENING
```

---

## 🌐 Step 3: 대시보드 접속

### 브라우저에서 열기

```
http://localhost:8000
```

**예상 화면:**
- GIS 지도가 표시됨
- 충전소 위치가 마커로 표시됨
- 초기 데이터베이스 데이터가 표시됨

### 대시보드 주요 화면

1. **홈 페이지** (`http://localhost:8000`)
   - GIS 지도
   - 충전소 목록
   - 실시간 통계

2. **API 문서** (`http://localhost:8000/docs`)
   - Swagger UI
   - API 엔드포인트 확인

3. **데이터 조회** (`http://localhost:8000/api/stations`)
   - JSON 형식 데이터

---

## 🐍 Step 4-A: Python 클라이언트 실행

### 옵션 1: 단일 충전기 시뮬레이션

**Terminal 3에서 실행:**

```powershell
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

python -c "
import asyncio
from charger_simulator import ChargerSimulator

async def main():
    print('='*70)
    print('🚗 Python 충전기 시뮬레이터 - 단일 충전기')
    print('='*70)
    print()
    
    # 충전기 정보
    charger = ChargerSimulator(
        charger_id='CHARGER_PYTHON_001',
        server_url='ws://localhost:9000'
    )
    
    try:
        # Step 1: 서버 연결
        print('[Step 1] 서버 연결 중...')
        await charger.connect()
        print('✅ 서버 연결 성공')
        print()
        
        # Step 2: 부팅
        print('[Step 2] 충전기 부팅...')
        await charger.boot()
        print('✅ 부팅 완료')
        print()
        
        # Step 3: 사용 대기
        print('[Step 3] 사용 대기 중... (30초)')
        await asyncio.sleep(5)
        
        # Step 4: 거래 시작
        print('[Step 4] 거래 시작...')
        await charger.start_transaction()
        print('✅ 거래 시작')
        print()
        
        # Step 5: 전력량 전송
        print('[Step 5] 전력량 전송 중... (10초, 5회)')
        for i in range(5):
            await asyncio.sleep(2)
            await charger.send_meter_values()
            print(f'   ✓ 전력량 전송 #{i+1}')
        print()
        
        # Step 6: 거래 종료
        print('[Step 6] 거래 종료...')
        await charger.stop_transaction()
        print('✅ 거래 종료')
        print()
        
        print('[완료] 시뮬레이션 완료')
        print('대시보드에서 충전 기록을 확인하세요!')
        
    except Exception as e:
        print(f'❌ 오류: {e}')
    finally:
        await charger.disconnect()

asyncio.run(main())
"
```

**예상 출력:**
```
======================================================================
🚗 Python 충전기 시뮬레이터 - 단일 충전기
======================================================================

[Step 1] 서버 연결 중...
✅ 서버 연결 성공

[Step 2] 충전기 부팅...
✅ 부팅 완료

[Step 3] 사용 대기 중... (30초)

[Step 4] 거래 시작...
✅ 거래 시작

[Step 5] 전력량 전송 중... (10초, 5회)
   ✓ 전력량 전송 #1
   ✓ 전력량 전송 #2
   ✓ 전력량 전송 #3
   ✓ 전력량 전송 #4
   ✓ 전력량 전송 #5

[Step 6] 거래 종료...
✅ 거래 종료

[완료] 시뮬레이션 완료
대시보드에서 충전 기록을 확인하세요!
```

✅ **확인**:
- 터미널에 모든 Step이 성공 메시지 표시
- T1 (OCPP 서버)에 연결 메시지 표시
- 브라우저 대시보드에 새로운 충전기 데이터 표시

---

### 옵션 2: 여러 충전기 동시 시뮬레이션

**Terminal 3에서 실행:**

```powershell
python charger_simulator.py
```

또는 다중 충전기 테스트:

```powershell
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

python -c "
import asyncio
from charger_simulator import ChargerSimulator

async def simulate_charger(charger_id, duration=30):
    print(f'🚗 [{charger_id}] 시뮬레이션 시작')
    
    charger = ChargerSimulator(
        charger_id=charger_id,
        server_url='ws://localhost:9000'
    )
    
    try:
        await charger.connect()
        print(f'✅ [{charger_id}] 연결 완료')
        
        await charger.boot()
        await asyncio.sleep(2)
        
        await charger.start_transaction()
        print(f'⚡ [{charger_id}] 충전 시작')
        
        for i in range(5):
            await asyncio.sleep(4)
            await charger.send_meter_values()
        
        await charger.stop_transaction()
        print(f'✅ [{charger_id}] 완료')
        
    except Exception as e:
        print(f'❌ [{charger_id}] 오류: {e}')
    finally:
        await charger.disconnect()

async def main():
    print('='*70)
    print('🚗 Python 충전기 시뮬레이터 - 다중 충전기')
    print('='*70)
    print()
    
    # 3개 충전기 동시 실행
    chargers = [
        'CHARGER_PYTHON_001',
        'CHARGER_PYTHON_002',
        'CHARGER_PYTHON_003',
    ]
    
    tasks = [simulate_charger(cid) for cid in chargers]
    await asyncio.gather(*tasks)
    
    print()
    print('✅ 모든 충전기 시뮬레이션 완료')
    print('대시보드에서 결과를 확인하세요!')

asyncio.run(main())
"
```

---

## 🔷 Step 4-B: C# 클라이언트 실행

### 선택지 1: 기본 C# 클라이언트 (추천)

**Terminal 3에서 실행 (또는 별도 터미널):**

```powershell
# C# 프로젝트 디렉토리로 이동
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

# C# 클라이언트 빌드 및 실행
dotnet run -- --charger-id CHARGER_CSHARP_001 --server ws://localhost:9000

# 또는
dotnet run
```

**예상 출력:**
```
Starting OCPP 2.0.1 Charger Simulator...

Configuration:
  Charger ID: CHARGER_CSHARP_001
  Server URL: ws://localhost:9000
  Protocol: OCPP 2.0.1

[Step 1] Connecting to server...
✅ Connected

[Step 2] Sending BootNotification...
✅ Boot notification sent

[Step 3] Waiting for authorization...
✅ Authorized

[Step 4] Starting transaction...
✅ Transaction started

[Step 5] Sending meter values...
  ✓ Meter value sent #1
  ✓ Meter value sent #2
  ✓ Meter value sent #3

[Step 6] Stopping transaction...
✅ Transaction stopped

[Complete] Simulation completed successfully!
Check the dashboard for charging records!
```

---

### 선택지 2: Advanced C# 클라이언트 (다중 충전기)

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

# 다중 충전기 시뮬레이션
dotnet run -- --chargers 3 --duration 60

# 또는 설정 파일로 실행
dotnet run -- --config appsettings.json
```

---

## 📊 Step 5: 실시간 모니터링

### 방법 1: 터미널에서 로그 모니터링 (T4)

```powershell
# 로그 파일 실시간 모니터링
Get-Content -Path "ocpp_protocol_debug.log" -Wait -Tail 20
```

### 방법 2: 데이터베이스에서 실시간 조회 (T4)

```powershell
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

python -c "
import time
from database.models_postgresql import DatabaseManager
from database.services import ChargerService
from sqlalchemy import func

db = DatabaseManager()

print('='*70)
print('📊 실시간 데이터 모니터링')
print('='*70)
print()

last_count = 0
while True:
    session = db.get_session()
    try:
        # 충전기 목록 조회
        chargers = ChargerService.get_all_chargers(session)
        current_count = len(chargers)
        
        if current_count != last_count:
            print(f'⏰ {time.strftime(\"%H:%M:%S\")} - 충전기 수: {current_count}')
            for charger in chargers[-3:]:  # 최근 3개
                print(f'   • {charger.charger_id}: {charger.status}')
            last_count = current_count
        
        time.sleep(2)
    except KeyboardInterrupt:
        print('\\n⛔ 모니터링 중단')
        break
    except Exception as e:
        print(f'❌ 오류: {e}')
    finally:
        session.close()
"
```

### 방법 3: 브라우저 대시보드 실시간 확인

1. `http://localhost:8000` 열기
2. F5 키를 눌러 새로고침 (또는 자동 새로고침 설정)
3. 다음 정보를 실시간으로 확인:
   - 등록된 충전기 목록
   - 현재 충전 상태
   - 전력 소비량
   - 통계 정보

---

## ✅ 체크리스트 - 각 단계별 확인

### ✓ 서버 실행 완료 확인

- [ ] T1 터미널: `WebSocket listening on ws://0.0.0.0:9000`
- [ ] T2 터미널: `Uvicorn running on http://0.0.0.0:8000`
- [ ] 포트 확인: 9000, 8000 LISTENING
- [ ] 브라우저: `http://localhost:8000` 접속 가능

### ✓ Python 클라이언트 실행 확인

- [ ] T3 터미널: `[Step 1] 서버 연결 중...` 시작
- [ ] T3 터미널: `✅ 서버 연결 성공` 메시지
- [ ] T3 터미널: `[Step 2] 충전기 부팅...` 진행
- [ ] T3 터미널: `✅ 부팅 완료` 메시지
- [ ] T3 터미널: 모든 Step 완료 후 `[완료] 시뮬레이션 완료`

### ✓ 대시보드 데이터 확인

- [ ] 새 충전기 `CHARGER_PYTHON_001` 추가됨
- [ ] 충전기 상태: `in_use` 또는 `charging`
- [ ] 거래 기록에 새 항목 추가됨
- [ ] 통계 데이터 업데이트됨

### ✓ C# 클라이언트 실행 확인 (선택)

- [ ] T3 터미널: `Connecting to server...` 시작
- [ ] T3 터미널: `✅ Connected` 메시지
- [ ] T3 터미널: 모든 단계 완료
- [ ] 대시보드: `CHARGER_CSHARP_001` 추가 확인

---

## 🔍 문제 해결

### 문제 1: 포트가 이미 사용 중입니다

```
❌ OSError: [Errno 48] Address already in use
```

**해결:**
```powershell
# 포트를 사용 중인 프로세스 확인
Get-Process | Where-Object { $_.Handles -gt 100 } | ForEach-Object {
    $proc = $_
    Get-NetTCPConnection | Where-Object {
        $_.OwningProcess -eq $proc.Id -and ($_.LocalPort -eq 9000 -or $_.LocalPort -eq 8000)
    } | ForEach-Object {
        "프로세스: $($proc.ProcessName) (PID: $($proc.Id)) - 포트: $($_.LocalPort)"
    }
}

# 프로세스 종료
Stop-Process -Name "python" -Force
```

---

### 문제 2: 데이터베이스 연결 실패

```
❌ psycopg2.OperationalError: could not connect to server
```

**해결:**
```powershell
# PostgreSQL 서비스 시작
Start-Service postgresql-x64-15

# 데이터베이스 확인
psql -U postgres -c "\l charger_db"

# 필요시 다시 생성
createdb -U postgres charger_db
```

---

### 문제 3: 클라이언트 연결 실패

```
❌ TimeoutError: WebSocket connection timeout
```

**해결:**
1. T1 서버가 실행 중인지 확인
2. 방화벽 설정 확인
3. 포트 9000이 LISTENING 상태인지 확인
4. 클라이언트 URL 확인: `ws://localhost:9000`

---

## 📚 참고 자료

### 로그 파일
- `ocpp_protocol_debug.log` - OCPP 프로토콜 로그
- 각 터미널의 콘솔 출력

### API 엔드포인트
- `http://localhost:8000/api/stations` - 충전소 목록
- `http://localhost:8000/api/chargers` - 충전기 목록
- `http://localhost:8000/api/statistics` - 통계

### 관련 파일
- `ocpp_server.py` - OCPP WebSocket 서버
- `gis_dashboard_api.py` - REST API & GIS 대시보드
- `charger_simulator.py` - Python 클라이언트
- `OCPPSimulator/` - C# 클라이언트

---

## 🎯 다음 단계

### 테스트 완료 후:

1. **로그 분석**
   - 서버 로그에서 메시지 흐름 확인
   - 오류가 있는지 검토

2. **성능 테스트**
   - 여러 충전기 동시 실행
   - 대시보드 로딩 시간 측정

3. **문제 해결**
   - 실패한 항목 수정
   - MANUAL_TEST_GUIDE.md 참고

4. **배포 준비**
   - 프로덕션 설정 확인
   - 데이터베이스 백업

---

**이제 준비 완료! Step 1부터 시작하세요!** 🚀
