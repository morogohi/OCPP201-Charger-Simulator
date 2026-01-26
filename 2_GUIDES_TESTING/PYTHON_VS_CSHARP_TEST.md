# 🔄 Python vs C# 클라이언트 비교 테스트

**목표**: Python 클라이언트와 C# 클라이언트를 차례대로 실행하여 결과 비교

---

## 📊 비교 테이블

| 항목 | Python | C# |
|------|--------|-----|
| **파일** | charger_simulator.py | OCPPSimulator/Program.cs |
| **실행 명령** | `python charger_simulator.py` | `dotnet run` |
| **소요 시간** | ~10초 빌드 | ~5초 빌드 |
| **비동기 처리** | asyncio | async/await |
| **메시지 형식** | Pydantic | Classes |
| **오류 처리** | Try-Except | Try-Catch |

---

## 🚀 Step 1: 서버 준비

### Terminal 1: OCPP 서버 실행

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python ocpp_server.py
```

### Terminal 2: API 서버 실행

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python gis_dashboard_api.py
```

### 확인

```powershell
netstat -ano | findstr "9000\|8000"
# ✅ 포트 9000, 8000 모두 LISTENING
```

---

## 🐍 Step 2: Python 클라이언트 테스트

### Terminal 3: Python 클라이언트 실행

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

python charger_simulator.py
```

**또는 단일 거래 버전:**

```powershell
python -c "
import asyncio
from charger_simulator import ChargerSimulator

async def main():
    print('='*70)
    print('🐍 Python 클라이언트 테스트')
    print('='*70)
    print()
    
    charger = ChargerSimulator('PYTHON_001', 'ws://localhost:9000')
    
    try:
        print('[1/5] 연결 중...')
        await charger.connect()
        print('✅ 연결 완료')
        print()
        
        print('[2/5] 부팅 중...')
        await charger.boot()
        print('✅ 부팅 완료')
        print()
        
        print('[3/5] 거래 시작 중...')
        await charger.start_transaction()
        print('✅ 거래 시작')
        print()
        
        print('[4/5] 전력량 전송 중...')
        for i in range(5):
            await asyncio.sleep(1)
            await charger.send_meter_values()
            print(f'   ✓ 데이터 #{i+1}')
        print()
        
        print('[5/5] 거래 종료 중...')
        await charger.stop_transaction()
        print('✅ 거래 종료')
        print()
        
        print('='*70)
        print('✅ Python 클라이언트 테스트 완료')
        print('='*70)
        
    except Exception as e:
        print(f'❌ 오류: {e}')
    finally:
        await charger.disconnect()

asyncio.run(main())
"
```

### 예상 출력

```
======================================================================
🐍 Python 클라이언트 테스트
======================================================================

[1/5] 연결 중...
✅ 연결 완료

[2/5] 부팅 중...
✅ 부팅 완료

[3/5] 거래 시작 중...
✅ 거래 시작

[4/5] 전력량 전송 중...
   ✓ 데이터 #1
   ✓ 데이터 #2
   ✓ 데이터 #3
   ✓ 데이터 #4
   ✓ 데이터 #5

[5/5] 거래 종료 중...
✅ 거래 종료

======================================================================
✅ Python 클라이언트 테스트 완료
======================================================================
```

### 확인할 사항

- [ ] T3 (Python): 모든 단계 성공 ✅
- [ ] T1 (서버): 연결 메시지 출력
- [ ] 대시보드: `PYTHON_001` 충전기 추가됨
- [ ] 대시보드: 거래 기록 표시됨

---

## 🔷 Step 3: C# 클라이언트 테스트

### Terminal 3에서 Python 클라이언트 중단

```powershell
Ctrl+C  # Python 프로세스 종료
```

### Terminal 3: C# 클라이언트 실행

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"
dotnet run -- --charger-id CSHARP_001 --transaction --meter-interval 2
```

**또는 자세한 버전:**

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"

echo "Starting C# Charger Simulator..."
echo ""

dotnet run -- `
    --charger-id CSHARP_001 `
    --server ws://localhost:9000 `
    --vendor "CSharp Simulator" `
    --model "V1.0" `
    --duration 60 `
    --transaction `
    --meter-interval 2
```

### 예상 출력

```
Starting OCPP 2.0.1 Charger Simulator...

Configuration:
  Charger ID: CSHARP_001
  Server: ws://localhost:9000
  Vendor: CSharp Simulator
  Model: V1.0

[INFO] Connecting to server...
[INFO] Connected successfully
[SUCCESS] BootNotification accepted

[INFO] Starting transaction...
[SUCCESS] Transaction started

[INFO] Sending meter values...
  ✓ Meter value #1 sent (timestamp: 2026-01-26T10:00:00Z)
  ✓ Meter value #2 sent (timestamp: 2026-01-26T10:00:02Z)
  ✓ Meter value #3 sent (timestamp: 2026-01-26T10:00:04Z)

[INFO] Stopping transaction...
[SUCCESS] Transaction stopped

[INFO] Simulation completed successfully!
```

### 확인할 사항

- [ ] T3 (C#): 모든 단계 성공
- [ ] T1 (서버): C# 연결 메시지 출력
- [ ] 대시보드: `CSHARP_001` 충전기 추가됨
- [ ] 대시보드: 이전 거래와 함께 표시됨

---

## 📊 Step 4: 결과 비교

### 대시보드에서 확인

```
http://localhost:8000
```

**비교할 항목:**

| 항목 | Python | C# | 확인 |
|------|--------|-----|------|
| 충전기 ID | PYTHON_001 | CSHARP_001 | ✓ |
| 연결 상태 | connected | connected | ✓ |
| 마지막 활동 | ~방금전 | ~방금전 | ✓ |
| 거래 기록 | 1개 | 1개 | ✓ |
| 전력량 데이터 | 5개 | 3개 | ✓ |

---

## 🔄 Step 5: 동시 실행 테스트

### Terminal 3: Python 클라이언트

```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
python charger_simulator.py
```

### Terminal 4 (새로 열기): C# 클라이언트

```powershell
cd "c:\Project\OCPP201(P2M)\OCPPSimulator"
dotnet run -- --charger-id CSHARP_002
```

### 결과

**대시보드:**
- PYTHON_001 + CSHARP_002 모두 표시
- 동시에 데이터 수신
- 실시간 업데이트

**서버 로그:**
- 두 클라이언트의 메시지 섞여 있음
- 각각 독립적으로 처리됨

---

## 📋 상세 비교 체크리스트

### 기능 비교

```
Python 클라이언트
├─ [✓] 서버 연결
├─ [✓] BootNotification 전송
├─ [✓] 거래 시작
├─ [✓] 전력량 전송
├─ [✓] 거래 종료
└─ [✓] 상태 보고

C# 클라이언트
├─ [✓] 서버 연결
├─ [✓] BootNotification 전송
├─ [✓] 거래 시작
├─ [✓] 전력량 전송
├─ [✓] 거래 종료
└─ [✓] 상태 보고
```

### 성능 비교

| 지표 | Python | C# |
|------|--------|-----|
| 시작 시간 | ~2초 | ~3초 |
| 연결 시간 | ~0.5초 | ~0.5초 |
| 메시지 처리 | 비동기 | 비동기 |
| CPU 사용률 | 낮음 | 낮음 |
| 메모리 사용 | ~30MB | ~40MB |

### 데이터 비교

**Python에서 생성된 데이터:**
```json
{
  "charger_id": "PYTHON_001",
  "status": "available",
  "timestamp": "2026-01-26T10:00:00Z",
  "power": 250.0,
  "voltage": 400
}
```

**C#에서 생성된 데이터:**
```json
{
  "charger_id": "CSHARP_001",
  "status": "available",
  "timestamp": "2026-01-26T10:00:01Z",
  "power": 245.5,
  "voltage": 400
}
```

---

## 🎯 테스트 결과 기록

### 테스트 1: Python 클라이언트

```
테스트 일시: 2026-01-26 10:00:00
테스트자: [이름]
결과: ✅ PASS

- 연결: 성공
- 부팅: 성공
- 거래: 성공
- 데이터: 5개 전송
- 대시보드: 데이터 표시됨

메모:
```

### 테스트 2: C# 클라이언트

```
테스트 일시: 2026-01-26 10:02:00
테스트자: [이름]
결과: ✅ PASS

- 연결: 성공
- 부팅: 성공
- 거래: 성공
- 데이터: 3개 전송
- 대시보드: 데이터 표시됨

메모:
```

### 테스트 3: 동시 실행

```
테스트 일시: 2026-01-26 10:04:00
테스트자: [이름]
결과: ✅ PASS

- Python + C# 동시 실행: 성공
- 서버 처리: 정상
- 대시보드: 모든 데이터 표시됨

메모:
```

---

## 💡 최적 실행 순서

### 20분 완전 테스트

```
1. 서버 준비 (2분)
   ├─ T1: OCPP 서버
   └─ T2: API 서버

2. Python 테스트 (5분)
   └─ T3: Python 클라이언트 실행

3. 대시보드 확인 (2분)
   └─ http://localhost:8000 접속

4. C# 테스트 (5분)
   └─ T3: C# 클라이언트 실행

5. 결과 비교 (3분)
   └─ 대시보드에서 데이터 비교

6. 동시 실행 테스트 (3분)
   └─ T3, T4: 동시 실행
```

---

## ✅ 최종 체크리스트

- [ ] 서버 실행 확인 (T1, T2)
- [ ] Python 클라이언트 성공 실행
- [ ] 대시보드에 PYTHON_001 표시
- [ ] C# 클라이언트 성공 실행
- [ ] 대시보드에 CSHARP_001 표시
- [ ] 두 충전기의 거래 기록 비교
- [ ] 동시 실행 테스트 완료
- [ ] 대시보드에서 실시간 업데이트 확인

---

**이제 Python과 C# 클라이언트를 모두 테스트할 수 있습니다!** 🚀

더 자세한 정보:
- Python: QUICK_START_SERVER.md
- C#: CSHARP_CLIENT_RUN.md
