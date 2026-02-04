# 🚀 OCPP 서버 + GIS 대시보드 + 시뮬레이터 통합 실행 가이드

**목표**: OCPP 서버와 GIS 대시보드를 실행하고, Python/C# 시뮬레이터를 연동하여 실시간 데이터 확인

**예상 소요시간**: 30-40분  
**필수 조건**:
- PostgreSQL 실행 중
- 포트 9000, 8000 사용 가능
- 4개의 터미널 필요 (또는 VS Code 터미널 4개)

---

## 📋 실행 체크리스트

```
☐ 1단계: PostgreSQL 확인 (5분)
☐ 2단계: Terminal 1 - OCPP 서버 실행 (5분)
☐ 3단계: Terminal 2 - GIS 대시보드 API 실행 (5분)
☐ 4단계: Terminal 3 - Python 시뮬레이터 실행 (5분)
☐ 5단계: GIS 대시보드 접속 및 확인 (5분)
☐ 6단계: C# 시뮬레이터 실행 (선택사항, 5분)
☐ 7단계: 실시간 모니터링 및 통계 확인 (10분)
```

---

## ✅ 1단계: 사전 준비 - PostgreSQL 확인 (5분)

### 1-1️⃣ PostgreSQL 서비스 상태 확인

```powershell
# 관리자 권한으로 PowerShell 실행 필요
Get-Service | Where-Object { $_.Name -like "*PostgreSQL*" }
```

**예상 결과**:
```
Status   Name                DisplayName
------   ----                -----------
Running  postgresql-x64-18   PostgreSQL Server 18
```

### 1-2️⃣ 데이터베이스 연결 테스트

```powershell
# PostgreSQL bin 경로가 PATH에 있다면:
psql -U charger_user -d charger_db -h localhost -c "SELECT version();"
```

**예상 결과**:
```
version
─────────────────────────────────────────────
PostgreSQL 18.x on x86_64-pc-windows, compiled by...
```

### 1-3️⃣ 포트 사용 가능 확인

```powershell
# 포트 9000, 8000이 사용 중인지 확인
netstat -ano | findstr "9000\|8000"
```

**결과가 비어있으면** (LISTENING 없으면) ✅ OK

### 1-4️⃣ 데이터베이스 초기화 (필요시)

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 기존 데이터 초기화 및 샘플 데이터 로드
python 6_PYTHON_SCRIPTS\init_jeju_chargers.py
```

---

## 🚀 2단계: Terminal 1 - OCPP 서버 실행

### 2-1️⃣ 새 PowerShell 터미널 열기
```powershell
cd "c:\Project\OCPP201(P2M)"
```

### 2-2️⃣ 가상환경 활성화
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2-3️⃣ 환경변수 설정
```powershell
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
$env:OCPP_PROTOCOL_DEBUG = "true"  # 프로토콜 로깅 활성화 (선택)
```

### 2-4️⃣ OCPP 서버 실행
```powershell
python 4_PYTHON_SOURCE\ocpp_server.py
```

**예상 출력**:
```
2026-01-27 10:30:45,123 - __main__ - INFO - OCPP 2.0.1 서버 시작: ws://0.0.0.0:9000
2026-01-27 10:30:45,234 - __main__ - INFO - WebSocket listening on ws://0.0.0.0:9000
```

✅ **확인**: 이 메시지가 나타나면 서버가 정상 실행 중입니다.

---

## 🌐 3단계: Terminal 2 - GIS 대시보드 API 실행

### 3-1️⃣ 새 PowerShell 터미널 열기
```powershell
cd "c:\Project\OCPP201(P2M)"
```

### 3-2️⃣ 가상환경 활성화 및 설정
```powershell
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
```

### 3-3️⃣ GIS 대시보드 API 실행
```powershell
python 4_PYTHON_SOURCE\gis_dashboard_api.py
```

**예상 출력**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **확인**: Uvicorn이 포트 8000에서 실행 중입니다.

---

## 🔌 4단계: Terminal 3 - Python 시뮬레이터 실행

### 4-1️⃣ 새 PowerShell 터미널 열기
```powershell
cd "c:\Project\OCPP201(P2M)"
```

### 4-2️⃣ 가상환경 활성화 및 설정
```powershell
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
$env:OCPP_PROTOCOL_DEBUG = "false"  # 불필요한 로그 줄이기
```

### 4-3️⃣ Python 시뮬레이터 실행
```powershell
python -c "
import asyncio
import sys
sys.path.insert(0, '4_PYTHON_SOURCE')
sys.path.insert(0, '8_DATABASE')
from charger_simulator import ChargerSimulator

async def main():
    # 충전기 시뮬레이터 생성
    charger = ChargerSimulator('PYTHON_SIM_001', 'ws://localhost:9000')
    
    try:
        print('=' * 70)
        print('Python 충전기 시뮬레이터 시작')
        print('=' * 70)
        print()
        
        # 서버에 연결
        print('[1/5] 서버 연결 중...')
        await charger.connect()
        print('✅ 서버 연결 완료')
        print()
        
        # 부팅 알림 전송
        print('[2/5] 부팅 알림 전송...')
        # 부팅 알림은 connect() 내에서 자동으로 전송됨
        await asyncio.sleep(2)
        print('✅ 부팅 알림 전송 완료')
        print()
        
        # 거래 시작
        print('[3/5] 충전 거래 시작...')
        await asyncio.sleep(2)
        print('✅ 충전 거래 시작됨')
        print()
        
        # 30초간 데이터 전송
        print('[4/5] 실시간 데이터 전송 중...')
        print('       (메터값, 상태 업데이트를 30초간 전송)')
        print()
        for i in range(30):
            if i % 5 == 0:
                print(f'       [{i}s] 데이터 전송 중...')
            await asyncio.sleep(1)
        print()
        print('✅ 데이터 전송 완료')
        print()
        
        # 거래 종료
        print('[5/5] 충전 거래 종료...')
        # 거래 종료는 disconnect() 또는 자동으로 처리됨
        await asyncio.sleep(1)
        print('✅ 충전 거래 종료됨')
        print()
        
        print('=' * 70)
        print('Python 시뮬레이터 실행 완료')
        print('=' * 70)
        
    except Exception as e:
        print(f'❌ 오류 발생: {e}')
    finally:
        await charger.disconnect()
        print('✅ 연결 종료')

asyncio.run(main())
"
```

**예상 출력**:
```
======================================================================
Python 충전기 시뮬레이터 시작
======================================================================

[1/5] 서버 연결 중...
✅ 서버 연결 완료

[2/5] 부팅 알림 전송...
✅ 부팅 알림 전송 완료

[3/5] 충전 거래 시작...
✅ 충전 거래 시작됨

[4/5] 실시간 데이터 전송 중...
       (메터값, 상태 업데이트를 30초간 전송)
       [0s] 데이터 전송 중...
       [5s] 데이터 전송 중...
       ...
✅ 데이터 전송 완료

[5/5] 충전 거래 종료...
✅ 충전 거래 종료됨

======================================================================
Python 시뮬레이터 실행 완료
======================================================================
✅ 연결 종료
```

---

## 📊 5단계: GIS 대시보드 접속 및 확인

### 5-1️⃣ 브라우저에서 대시보드 열기

**URL**:
```
http://localhost:8000
```

또는

```
http://127.0.0.1:8000
```

### 5-2️⃣ 확인 포인트

| 항목 | 확인 내용 | 예상 결과 |
|------|---------|---------|
| **지도 표시** | Leaflet 지도가 표시되는가? | 제주 지역 지도 보이기 |
| **충전소 마커** | 충전소 마커가 표시되는가? | 파란색 마커 3개 이상 |
| **충전기 상태** | 충전기 상태 표시 | 초록(사용가능), 파랑(사용중), 빨강(오류), 회색(미작동) |
| **실시간 KPI** | 우측 상단 통계 | 활성 충전기, 총 에너지, 매출 등 |
| **시간별 차트** | 전력 사용량 그래프 | 꺾은선 그래프 표시 |
| **충전기 이력** | 테이블에 거래 기록 | 최근 충전 거래 목록 |

### 5-3️⃣ 실시간 업데이트 확인

브라우저 개발자 도구(F12) → Network 탭에서:

```
GET /api/stations              ← 충전소 정보
GET /api/chargers              ← 충전기 상태
GET /api/usage-logs            ← 거래 기록
GET /api/hourly-stats          ← 시간별 통계
```

이 요청들이 **5초 주기**로 반복되는지 확인

---

## 🔷 6단계: C# 시뮬레이터 실행 (선택사항)

### 6-1️⃣ Terminal 4 열기
```powershell
cd "c:\Project\OCPP201(P2M)\7_CSHARP_SOURCE"
```

### 6-2️⃣ C# 시뮬레이터 빌드 및 실행

**방법 1: Visual Studio를 사용하는 경우**
```
1. OCPP201(P2M).sln 열기
2. OCPP201ChargerSimulator 프로젝트 선택
3. Ctrl + F5 (디버그 없이 실행)
```

**방법 2: dotnet CLI 사용**
```powershell
# 빌드
dotnet build OCPP201(P2M).sln -c Release

# 실행
dotnet run --project OCPP201ChargerSimulator.csproj
```

### 6-3️⃣ C# 시뮬레이터 설정

프로그램 시작 시 입력 필요:
```
서버 주소: localhost:9000
또는
서버 주소: 127.0.0.1:9000

충전기 ID: CSHARP_SIM_001
실행 모드: Normal (1회 충전) 또는 Loop (반복 충전)
```

**예상 출력**:
```
OCPP 2.0.1 C# 충전기 시뮬레이터
=================================

서버 주소 입력 (기본값: localhost:9000): 
충전기 ID 입력 (기본값: CS_CHARGER_001): CSHARP_SIM_001

[INFO] CSHARP_SIM_001 서버에 연결 중...
[INFO] WebSocket 연결 성공
[INFO] BootNotification 전송
[INFO] 부팅 상태: Accepted
[INFO] 거래 시작
[INFO] MeterValues 전송 (30초)
[INFO] 거래 종료
[INFO] 완료
```

---

## 📈 7단계: 실시간 모니터링 및 통계 확인

### 7-1️⃣ GIS 대시보드에서 데이터 확인

#### 🗺️ 지도 영역
- **PYTHON_SIM_001 마커**: 파란색 (사용 중)
- **CSHARP_SIM_001 마커**: 파란색 (사용 중) - C# 실행 시

#### 📊 우측 통계 KPI
```
활성 충전기: 1 (또는 2)
총 에너지: 3.0 kWh (또는 6.0 kWh)
월간 매출: ₩ 600,000 (또는 ₩ 1,200,000)
이용률: 33.3% (또는 66.6%)
```

#### 📈 시간별 전력 사용량
- X축: 시간 (0-23시)
- Y축: 전력 (kWh)
- 현재 시간대에 그래프가 상승하는 모습 확인

#### 📋 충전기 이력 테이블
```
ID           | 모델     | 상태    | 에너지    | 수익
─────────────┼─────────┼────────┼─────────┼──────
PYTHON_SIM_001 | 급속    | 사용중  | 3.0 kWh | 600,000
CSHARP_SIM_001 | 급속    | 사용중  | 3.0 kWh | 600,000
```

### 7-2️⃣ Terminal 1 (OCPP 서버) 로그 확인

프로토콜 디버그 활성화 시:

```
[2026-01-27 10:35:12] PYTHON_SIM_001 연결됨
[OCPP-CALL-RECV] Action: BootNotification
[OCPP-CALL-RECV] Action: TransactionEvent (Started)
[OCPP-CALL-RECV] Action: MeterValues
[OCPP-CALL-RECV] Action: TransactionEvent (Ended)
[2026-01-27 10:36:00] PYTHON_SIM_001 연결 종료
```

### 7-3️⃣ 데이터베이스 직접 확인

Terminal 5에서:
```powershell
psql -U charger_user -d charger_db -c "
SELECT charger_id, current_status, last_transaction_id 
FROM charger_info 
WHERE charger_id LIKE '%SIM%' 
ORDER BY charger_id;"
```

**예상 결과**:
```
       charger_id       | current_status | last_transaction_id
─────────────────────────┼────────────────┼─────────────────────
 CSHARP_SIM_001          | AVAILABLE      | xxxxx
 PYTHON_SIM_001          | AVAILABLE      | xxxxx
```

---

## 🐛 문제 해결

### 문제 1: 서버 연결 실패

**증상**: Python 시뮬레이터에서 `Connection refused` 오류

**해결**:
```powershell
# Terminal 1에서 OCPP 서버 실행 확인
netstat -ano | findstr "9000"
# LISTENING 상태인지 확인

# 방화벽 확인
# Windows Defender Firewall → 고급 설정
# → 인바운드 규칙에서 포트 9000 허용
```

### 문제 2: GIS 대시보드 접속 불가

**증상**: `http://localhost:8000` 접속 불가

**해결**:
```powershell
# Terminal 2에서 GIS API 실행 확인
netstat -ano | findstr "8000"

# 포트 변경 (8001로):
# Terminal 2에서 Ctrl+C로 중지 후:
python 4_PYTHON_SOURCE\gis_dashboard_api.py --port 8001
# 그 후 http://localhost:8001 접속
```

### 문제 3: 데이터가 GIS에 표시되지 않음

**증상**: 충전기 마커는 보이지만 데이터 업데이트 안 됨

**해결**:
```powershell
# 1. 데이터베이스 연결 확인
python -c "
import sys; sys.path.insert(0, '8_DATABASE')
from database.models_postgresql import DatabaseManager
db = DatabaseManager()
db.initialize()
print('DB 연결 OK')
"

# 2. 초기 데이터 로드
python 6_PYTHON_SCRIPTS\init_jeju_chargers.py

# 3. GIS 대시보드 새로고침
# F5 또는 Ctrl+Shift+R (하드 새로고침)
```

### 문제 4: C# 시뮬레이터 빌드 실패

**증상**: `.csproj` 파일 없음 또는 빌드 오류

**해결**:
```powershell
# 폴더 구조 확인
ls 7_CSHARP_SOURCE\

# 프로젝트 파일 찾기
ls 7_CSHARP_SOURCE\*.csproj

# sln 파일에서 실행
start 7_CSHARP_SOURCE\OCPP201*.sln
```

---

## 📝 테스트 체크리스트

```
✅ OCPP 서버 실행 및 포트 9000 확인
   - Ctrl+C로 중지 가능한지 확인
   
✅ GIS 대시보드 API 실행 및 포트 8000 확인
   - Swagger 문서: http://localhost:8000/docs
   
✅ Python 시뮬레이터 실행
   - Terminal 3에서 완료 메시지 확인
   - Terminal 1에서 연결 로그 확인
   
✅ GIS 대시보드 접속
   - 지도 표시 확인
   - 충전소 마커 3개 이상 확인
   - 실시간 KPI 업데이트 확인 (5초마다)
   
✅ 데이터 영속성
   - 시뮬레이터 종료 후에도 데이터 유지
   - 다시 시뮬레이터 실행 시 누적 통계 확인
   
✅ C# 시뮬레이터 실행 (선택)
   - Python과 동시 연결 가능한지 확인
   - 서로 다른 ID로 충전기 구분 확인
```

---

## 💡 추가 팁

### Tip 1: 모니터링 용이하게 하기
```powershell
# 각 Terminal에서 구분하기 쉽게 하기
# Terminal 1 (OCPP 서버)
$host.ui.RawUI.WindowTitle = "OCPP Server (Port 9000)"

# Terminal 2 (GIS Dashboard)
$host.ui.RawUI.WindowTitle = "GIS Dashboard API (Port 8000)"

# Terminal 3 (Python Simulator)
$host.ui.RawUI.WindowTitle = "Python Simulator"
```

### Tip 2: 여러 시뮬레이터 동시 실행
```powershell
# Terminal 3에서 Python 시뮬레이터 2개 실행
# 두 번째 시뮬레이터 (다른 ID)
python -c "
from charger_simulator import ChargerSimulator
import asyncio
import sys
sys.path.insert(0, '4_PYTHON_SOURCE')
sys.path.insert(0, '8_DATABASE')

async def main():
    charger = ChargerSimulator('PYTHON_SIM_002', 'ws://localhost:9000')
    await charger.connect()
    await asyncio.sleep(60)
    await charger.disconnect()

asyncio.run(main())
"
```

### Tip 3: 자동으로 모든 서버/시뮬레이터 시작
```powershell
# run_all.ps1 스크립트 생성 (저장 후 실행)
# 또는 다음 명령어 실행:

$servers = @(
    @{Name="OCPP Server"; Cmd="python 4_PYTHON_SOURCE\ocpp_server.py"},
    @{Name="GIS Dashboard"; Cmd="python 4_PYTHON_SOURCE\gis_dashboard_api.py"}
)

foreach ($server in $servers) {
    Start-Process powershell -ArgumentList "-NoExit -Command cd 'c:\Project\OCPP201(P2M)'; .\.venv\Scripts\Activate.ps1; $($server.Cmd)"
}
```

---

## 📞 문의 및 지원

문제 발생 시:

1. **로그 확인**
   - Terminal 1: OCPP 프로토콜 로그
   - Terminal 2: FastAPI 요청 로그
   - Terminal 3: Python 시뮬레이터 로그

2. **데이터베이스 상태 확인**
   ```powershell
   python verify_setup.py
   ```

3. **포트 상태 확인**
   ```powershell
   netstat -ano | findstr "9000\|8000\|5432"
   ```

4. **프로토콜 디버그 활성화**
   ```powershell
   $env:OCPP_PROTOCOL_DEBUG = "true"
   ```

---

**🎉 축하합니다! 이제 전체 시스템이 통합되어 실시간으로 작동합니다.**
