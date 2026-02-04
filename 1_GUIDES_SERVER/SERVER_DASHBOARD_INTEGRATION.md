# 🎯 실시간 서버+대시보드 통합 가이드

**최종 목표**: 서버 실행 → 클라이언트 연결 → 대시보드 실시간 모니터링

**전체 시간**: 20-30분

---

## 📖 이 문서를 읽기 전에

이 가이드는 다음을 단계별로 설명합니다:

1. ✅ **OCPP WebSocket 서버** 실행
2. ✅ **REST API/GIS 대시보드** 실행
3. ✅ **Python 클라이언트** 연결 및 테스트
4. ✅ **C# 클라이언트** 연결 및 테스트 (선택)
5. ✅ **대시보드에서** 실시간 모니터링

---

## 🚀 빠른 시작 (3분)

### 너무 길다면 이것부터!

👉 [QUICK_START_SERVER.md](QUICK_START_SERVER.md)

**포함 내용:**
- Terminal 4개 준비
- 3줄 명령어로 서버 실행
- 대시보드 접속
- Python 클라이언트 실행

---

## 📚 전체 가이드 선택

### 옵션 1: 상세 가이드 (20분) ⭐ 추천

👉 [RUN_SERVER_DASHBOARD.md](RUN_SERVER_DASHBOARD.md)

**포함 내용:**
- Step 1-5 상세 설명
- 각 단계별 예상 출력
- 실시간 모니터링 방법
- 문제 해결 가이드

### 옵션 2: Python 클라이언트만 (10분)

👉 [QUICK_START_SERVER.md](QUICK_START_SERVER.md) +  
[RUN_SERVER_DASHBOARD.md](RUN_SERVER_DASHBOARD.md)의 Step 4-A

### 옵션 3: C# 클라이언트 (15분)

👉 [CSHARP_CLIENT_RUN.md](CSHARP_CLIENT_RUN.md)

### 옵션 4: Python vs C# 비교 (25분)

👉 [PYTHON_VS_CSHARP_TEST.md](PYTHON_VS_CSHARP_TEST.md)

---

## 🎯 5단계 실행 흐름

```
┌─────────────────────────────────────────┐
│ Step 1: 환경 확인                        │
│ (PostgreSQL, 포트 확인)                  │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ Step 2: 서버 실행                        │
│ (T1: OCPP서버 + T2: API서버)           │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ Step 3: 대시보드 접속                    │
│ (http://localhost:8000 확인)           │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ Step 4: 클라이언트 실행                  │
│ (T3: Python 또는 C#)                   │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ Step 5: 실시간 모니터링                  │
│ (터미널 + 대시보드 + 데이터베이스)       │
└─────────────────────────────────────────┘
```

---

## 🔧 Terminal 준비

### 필요한 Terminal 개수: 4개

| Terminal | 용도 | 명령어 |
|----------|------|--------|
| **T1** | OCPP 서버 | `python ocpp_server.py` |
| **T2** | API/대시보드 서버 | `python gis_dashboard_api.py` |
| **T3** | 클라이언트 | `python charger_simulator.py` 또는 `dotnet run` |
| **T4** | 모니터링 (선택) | 로그 모니터링 또는 DB 쿼리 |

---

## ✅ 준비 체크리스트

```powershell
# 1. PostgreSQL 확인
Get-Service postgresql* | Where-Object { $_.Status -eq 'Running' }
# 결과: State Running

# 2. 포트 확인
netstat -ano | findstr "LISTENING" | findstr "9000\|8000"
# 결과: 비어있어야 함 (사용 중이면 중단)

# 3. 디렉토리 확인
cd "c:\Project\OCPP201(P2M)"
ls ocpp_server.py
ls gis_dashboard_api.py
# 모두 있어야 함
```

---

## 🚀 실행 순서 (권장)

### 1️⃣ **T1: OCPP 서버** 시작 (30초)

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python ocpp_server.py
```

**확인:**
```
WebSocket listening on ws://0.0.0.0:9000
```

---

### 2️⃣ **T2: API 서버** 시작 (30초)

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python gis_dashboard_api.py
```

**확인:**
```
Uvicorn running on http://0.0.0.0:8000
```

---

### 3️⃣ **브라우저**: 대시보드 열기 (15초)

```
http://localhost:8000
```

**확인:**
- 지도 표시
- 충전소 마커 표시
- 초기 데이터 표시

---

### 4️⃣ **T3: 클라이언트** 선택 (2분)

#### **옵션 A: Python 클라이언트**

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

python -c "
import asyncio
from charger_simulator import ChargerSimulator

async def main():
    charger = ChargerSimulator('TEST_001', 'ws://localhost:9000')
    try:
        await charger.connect()
        print('✅ 연결됨')
        await charger.boot()
        print('✅ 부팅됨')
        await charger.start_transaction()
        print('✅ 거래 시작됨')
        for i in range(3):
            await asyncio.sleep(2)
            await charger.send_meter_values()
            print(f'✓ 데이터 #{i+1}')
        await charger.stop_transaction()
        print('✅ 완료!')
    finally:
        await charger.disconnect()

asyncio.run(main())
"
```

#### **옵션 B: C# 클라이언트**

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"
dotnet run -- --charger-id CSHARP_001 --transaction
```

---

### 5️⃣ **대시보드** 확인 (30초)

```
http://localhost:8000 새로고침 (F5)
```

**확인할 항목:**
- 새 충전기 `TEST_001` 또는 `CSHARP_001` 추가
- 충전기 상태 `in_use` 또는 `charging`
- 거래 기록 표시
- 전력량 데이터 업데이트

---

## 📊 실시간 모니터링 방법

### 방법 1: T1 (OCPP 서버) 로그 보기

```
[INFO] New connection: charger_id=TEST_001
[INFO] BootNotification received
[INFO] StartTransaction received
[INFO] MeterValues received (5 values)
[INFO] StopTransaction received
```

### 방법 2: T4 (Database 모니터링)

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1

python -c "
import time
from database.models_postgresql import DatabaseManager
from database.services import ChargerService

db = DatabaseManager()
while True:
    session = db.get_session()
    chargers = ChargerService.get_all_chargers(session)
    print(f'[{time.strftime(\"%H:%M:%S\")}] 충전기: {len(chargers)}')
    for c in chargers[-1:]:
        print(f'  - {c.charger_id}: {c.status}')
    session.close()
    time.sleep(5)
"
```

### 방법 3: 브라우저 대시보드

```
http://localhost:8000
```

**자동 새로고침 설정:**
- F12 (개발자 도구)
- Console 탭에서:
```javascript
setInterval(() => location.reload(), 5000)
```

---

## 🎬 성공적인 실행 예시

### Python 클라이언트 성공 시나리오

```
[T1 - OCPP 서버]
2026-01-26 10:00:00 | INFO | New charger connected: TEST_001
2026-01-26 10:00:01 | INFO | BootNotification from TEST_001
2026-01-26 10:00:02 | INFO | StartTransaction from TEST_001
2026-01-26 10:00:03 | INFO | MeterValues received x3
2026-01-26 10:00:06 | INFO | StopTransaction from TEST_001

[T3 - Python 클라이언트]
✅ 연결됨
✅ 부팅됨
✅ 거래 시작됨
✓ 데이터 #1
✓ 데이터 #2
✓ 데이터 #3
✅ 완료!

[브라우저 - 대시보드]
충전기 목록: TEST_001 추가됨
상태: in_use → charging
거래: 1개 기록됨
전력량: 3개 데이터 표시
```

---

## ⚠️ 흔한 오류 해결

### T1에서 "포트 이미 사용"

```powershell
# 기존 프로세스 종료
Stop-Process -Name python -Force

# T1 다시 실행
python ocpp_server.py
```

### T2에서 "데이터베이스 오류"

```powershell
# PostgreSQL 서비스 시작
Start-Service postgresql-x64-15

# T2 다시 실행
python gis_dashboard_api.py
```

### T3에서 "연결 거부"

```powershell
# T1이 실행 중인지 확인
netstat -ano | findstr ":9000"

# 없으면 T1 시작
# 있으면 클라이언트 URL 확인: ws://localhost:9000
```

### 브라우저에서 아무것도 안 보임

```
1. http://localhost:8000 다시 방문
2. Ctrl+Shift+Delete로 캐시 삭제
3. F12 콘솔에서 오류 확인
4. T2에서 API 서버 오류 확인
```

---

## 📋 전체 흐름 체크리스트

### 사전 준비
- [ ] PostgreSQL 실행
- [ ] 포트 9000, 8000 비어있음
- [ ] Python 가상환경 준비

### 서버 실행
- [ ] T1: OCPP 서버 실행 (`WebSocket listening...`)
- [ ] T2: API 서버 실행 (`Uvicorn running...`)
- [ ] 포트 9000, 8000 LISTENING 확인

### 대시보드 확인
- [ ] http://localhost:8000 접속 가능
- [ ] 지도 표시됨
- [ ] 충전소 마커 표시됨

### 클라이언트 실행
- [ ] T3: Python 또는 C# 클라이언트 실행
- [ ] 클라이언트 메시지 출력됨

### 실시간 모니터링
- [ ] T1: 연결 메시지 표시
- [ ] T3: 완료 메시지 표시
- [ ] 브라우저: 새 충전기 추가됨
- [ ] 브라우저: 거래 기록 표시됨

---

## 🎯 다음 단계

### 테스트 완료 후

1. **로그 분석**
   - T1 서버 로그 검토
   - 오류 확인

2. **대시보드 분석**
   - 데이터 정확성 확인
   - 통계 데이터 검증

3. **Python vs C# 비교** (선택)
   - 두 클라이언트 동시 실행
   - 결과 비교: [PYTHON_VS_CSHARP_TEST.md](PYTHON_VS_CSHARP_TEST.md)

4. **추가 테스트** (선택)
   - 다중 충전기 동시 실행
   - 장시간 부하 테스트
   - API 엔드포인트 테스트

---

## 📁 관련 문서

| 문서 | 목적 | 소요시간 |
|------|------|---------|
| [QUICK_START_SERVER.md](QUICK_START_SERVER.md) | 3분 빠른 시작 | 3분 |
| [RUN_SERVER_DASHBOARD.md](RUN_SERVER_DASHBOARD.md) | 상세 가이드 | 20분 |
| [CSHARP_CLIENT_RUN.md](CSHARP_CLIENT_RUN.md) | C# 클라이언트 | 15분 |
| [PYTHON_VS_CSHARP_TEST.md](PYTHON_VS_CSHARP_TEST.md) | 비교 테스트 | 25분 |

---

## 🚀 지금 바로 시작하세요!

1. Terminal 4개 준비
2. Step 1-5 순서대로 진행
3. 각 단계에서 확인 사항 체크
4. 대시보드에서 실시간 모니터링

**모든 준비가 완료되었습니다!** ✨

🎯 **최종 목표**: 서버와 클라이언트가 OCPP 프로토콜로 통신하고,  
대시보드에서 실시간으로 충전기 정보를 모니터링하는 것입니다.

**이제 시작하세요!** 🚀
