# ⚡ 서버+대시보드 3분 빠른 시작

**목표**: 3분 안에 서버 실행 → 대시보드 확인

---

## 📍 3분 빠른 시작

### 1️⃣ Terminal 1 - OCPP 서버 실행 (30초)

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python ocpp_server.py
```

**확인**: 이 메시지가 나올 때까지 기다리기
```
WebSocket listening on ws://0.0.0.0:9000
```

---

### 2️⃣ Terminal 2 - REST API 서버 실행 (30초)

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python gis_dashboard_api.py
```

**확인**: 이 메시지가 나올 때까지 기다리기
```
Uvicorn running on http://0.0.0.0:8000
```

---

### 3️⃣ 브라우저 - 대시보드 열기 (15초)

```
http://localhost:8000
```

✅ **확인**: 지도가 표시되면 성공!

---

### 4️⃣ Terminal 3 - Python 클라이언트 실행 (2분)

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

python -c "
import asyncio
from charger_simulator import ChargerSimulator

async def main():
    charger = ChargerSimulator('TEST_CHARGER_001', 'ws://localhost:9000')
    try:
        print('연결 중...')
        await charger.connect()
        print('✅ 연결됨')
        
        print('부팅 중...')
        await charger.boot()
        print('✅ 부팅됨')
        
        print('거래 시작...')
        await charger.start_transaction()
        print('✅ 거래 시작됨')
        
        for i in range(3):
            await asyncio.sleep(2)
            await charger.send_meter_values()
            print(f'✓ 데이터 전송 #{i+1}')
        
        await charger.stop_transaction()
        print('✅ 완료!')
    finally:
        await charger.disconnect()

asyncio.run(main())
"
```

---

## 🔍 확인 포인트

| 단계 | 확인 | 예상 결과 |
|------|------|---------|
| 1 | T1 메시지 | `WebSocket listening on ws://0.0.0.0:9000` |
| 2 | T2 메시지 | `Uvicorn running on http://0.0.0.0:8000` |
| 3 | 브라우저 | 지도 + 충전소 표시 |
| 4 | T3 메시지 | `✅ 완료!` |
| 5 | 브라우저 새로고침 | 새 충전기 `TEST_CHARGER_001` 표시 |

---

## 🎬 실시간 보기

**모두 준비되면:**

1. **Terminal 1** (T1): 서버 로그 보기
2. **Terminal 3** (T3): 클라이언트 메시지 보기
3. **브라우저**: 대시보드 새로고침 (F5)

**결과:**
- T1에 연결 메시지 표시
- T3에 진행 메시지 표시
- 브라우저에 새 데이터 표시

---

## ⚠️ 빠른 문제 해결

### ❌ T1에서 "포트 이미 사용"

```powershell
Stop-Process -Name python -Force
# T1, T2, T3 다시 실행
```

### ❌ T2에서 데이터베이스 오류

```powershell
# PostgreSQL 시작
Start-Service postgresql-x64-15
# T2 다시 실행
```

### ❌ 브라우저에 아무것도 안 보임

```
1. Ctrl+Shift+Delete로 캐시 삭제
2. http://localhost:8000 다시 방문
3. 브라우저 콘솔에서 오류 확인 (F12)
```

---

**이제 시작하세요! Terminal 1부터!** 🚀
