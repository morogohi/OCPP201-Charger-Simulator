# ⚡ OCPP 2.0.1 C# 시뮬레이터 - 5분 빠른 시작

> **시간 소요**: 5분  
> **난이도**: 초급  
> **목표**: Python 서버와 C# 시뮬레이터 완벽 연동

---

## 🚀 Step 1: 환경 확인 (1분)

### Windows PowerShell (관리자 모드)

```powershell
# 1. Python 확인
python --version
# 출력: Python 3.8.0 이상

# 2. .NET SDK 확인
dotnet --version
# 출력: 6.0 이상

# 3. PostgreSQL 확인 (psql 명령어)
psql -U charger_user -d charger_db -c "SELECT COUNT(*) as charger_count FROM charger_info;"
# 출력: 34 (Emart 충전기 개수)
```

✅ 모두 설치되어 있으면 다음 단계로 진행

---

## 🚀 Step 2: Python 의존성 설치 (2분)

```powershell
cd C:\Project\OCPP201(P2M)

# 모든 필수 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install websockets psycopg2-binary tabulate

# 설치 확인
python -c "import websockets; print('✅ websockets OK')"
```

✅ 설치 완료

---

## 🚀 Step 3: Python 서버 시작 (30초)

### 터미널 1 (새로 열기)

```powershell
cd C:\Project\OCPP201(P2M)
python ocpp_server.py

# 기대 출력:
# 🌐 OCPP 2.0.1 서버 시작: ws://localhost:9000
# 📊 REST API 서버: http://localhost:8080
# ✅ 데이터베이스 연결: charger_db@localhost:5432
# 
# [서버 대기 중...]
```

⚠️ **이 터미널은 열린 상태로 유지하세요!**

---

## 🚀 Step 4: 테스트 실행 (2분)

### 터미널 2 (새로 열기)

```powershell
cd C:\Project\OCPP201(P2M)

# 방법 A: 자동 메뉴 (권장)
run_tests.bat

# 메뉴에서 선택:
# 5. Python 테스트 클라이언트 (Scenario 1)
# 6. Python 테스트 클라이언트 (Scenario 2)
# 7. Python 테스트 클라이언트 (Scenario 3)
```

**또는**

```powershell
# 방법 B: 직접 실행
python test_csharp_integration.py

# 또는 특정 시나리오만
python test_csharp_integration.py 1  # 시나리오 1
python test_csharp_integration.py 2  # 시나리오 2
python test_csharp_integration.py 3  # 시나리오 3
```

### 기대되는 출력

```
════════════════════════════════════════════════════════════════════════════════
  OCPP 2.0.1 Python 테스트 클라이언트
════════════════════════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════════════════════════
[시나리오 1] 기본 연결 및 BootNotification
════════════════════════════════════════════════════════════════════════════════

[emart_jeju_01] 서버 연결 중... (ws://localhost:9000)
✅ [emart_jeju_01] 서버 연결 성공
📤 [emart_jeju_01] BootNotification 전송
📥 [emart_jeju_01] 메시지 수신: [3,"message-id",...
✅ [emart_jeju_01] CALLRESULT 수신: message-id
💓 [emart_jeju_01] Heartbeat 전송

[emart_jeju_01] 상태: Available, 전력: 0kW, 누적: 0.00kWh

👋 [emart_jeju_01] 연결 해제

✅ 모든 테스트 완료!
```

---

## ✅ Step 5: 결과 검증 (30초)

```powershell
# 새 터미널 3 (또는 위의 터미널 2에서)
cd C:\Project\OCPP201(P2M)

python verify_test_results.py

# 출력 예:
# ✅ 데이터베이스 연결 성공
# ✅ PASS - scenario_1
# ✅ PASS - scenario_2
# ✅ PASS - scenario_3
# 🎉 모든 테스트 검증 완료!
```

---

## 📊 결과 확인 위치

### 1️⃣ 터미널 로그

```
✅ [emart_jeju_01] 서버 연결 성공
📤 [emart_jeju_01] BootNotification 전송
💓 [emart_jeju_01] Heartbeat 전송
💸 [emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
```

### 2️⃣ 데이터베이스

```powershell
# PowerShell에서 SQL 쿼리
psql -U charger_user -d charger_db -c "
SELECT charger_id, energy_consumed, cost, duration_seconds 
FROM charger_usage_log 
WHERE start_time > NOW() - INTERVAL '5 minutes' 
ORDER BY start_time DESC 
LIMIT 5;"

# 출력:
# emart_jeju_01 | 1.67 | 250.5 | 30
# emart_jeju_01 | 1.67 | 250.5 | 30
# ...
```

### 3️⃣ GIS 대시보드

```
브라우저에서 열기:
http://localhost:8080/advanced_dashboard.html

✅ Emart 3개 위치의 충전기가 지도에 표시됨
✅ 충전 중인 충전기는 녹색으로 표시
✅ 실시간 전력 및 에너지 표시
```

---

## 🎯 주요 확인 포인트

### ✅ 시나리오 1: 기본 연결 (5초)

```
기대 결과:
├─ ✅ WebSocket 연결 성공
├─ ✅ BootNotification 전송
├─ ✅ CALLRESULT (interval=30) 수신
└─ ✅ Heartbeat 시작

데이터베이스 확인:
SELECT * FROM charger_connection_log 
WHERE charger_id = 'emart_jeju_01' 
AND logged_at > NOW() - INTERVAL '5 minutes';

출력: connected 상태 기록
```

### ✅ 시나리오 2: 충전 세션 (30초)

```
기대 결과:
├─ ✅ TransactionEvent (Started)
├─ ✅ 에너지 누적: 0 → 1.67 kWh
├─ ✅ 비용 계산: ₩250
└─ ✅ TransactionEvent (Ended)

데이터베이스 확인:
SELECT energy_consumed, cost, duration_seconds 
FROM charger_usage_log 
WHERE transaction_id = 'TX-001' 
AND start_time > NOW() - INTERVAL '5 minutes';

출력:
1.67 | 250.5 | 30
```

### ✅ 시나리오 3: 다중 충전기 (45초)

```
기대 결과:
├─ ✅ 3개 충전기 동시 연결
├─ ✅ 각각 독립적인 TransactionId
├─ ✅ 총 전력: 250kW
└─ ✅ 각 충전기 에너지 누적

데이터베이스 확인:
SELECT charger_id, COUNT(*) as count, SUM(energy_consumed) as total 
FROM charger_usage_log 
WHERE start_time > NOW() - INTERVAL '45 seconds' 
GROUP BY charger_id;

출력:
emart_jeju_01      | 1 | 0.83
emart_jeju_02      | 1 | 0.83
emart_shinjeju_01  | 1 | 0.42
```

---

## 🆘 문제 해결 (Quick Fix)

### "Connection refused" 포트 9000

```powershell
# 1. 서버 실행 확인
netstat -ano | findstr ":9000"

# 2. 없으면 Python 서버 시작
python ocpp_server.py

# 3. 여전히 실패하면 포트 강제 해제 (선택사항)
taskkill /F /PID <PID>  # 기존 프로세스 종료
```

### "ModuleNotFoundError: No module named 'websockets'"

```powershell
pip install websockets psycopg2-binary tabulate
```

### 데이터베이스 연결 오류

```powershell
# PostgreSQL 실행 확인
pg_ctl status -D "C:\Program Files\PostgreSQL\data"

# 또는 Services에서 PostgreSQL 재시작
services.msc  # PostgreSQL14 서비스 확인
```

---

## 📈 성공 기준

| 항목 | 기준 | 확인 |
|------|------|------|
| **연결** | 모든 충전기 ws://localhost:9000 접속 | ✅ 로그 메시지 |
| **메시지** | BootNotification 전송 및 응답 | ✅ CALLRESULT 수신 |
| **에너지** | 1.67 ± 0.2 kWh | ✅ DB 쿼리 |
| **비용** | ₩250 ± 10 | ✅ DB 쿼리 |
| **다중** | 3개 이상 동시 연결 | ✅ netstat 확인 |

모두 ✅이면 **테스트 성공!** 🎉

---

## 🔗 더 알아보기

| 문서 | 내용 | 위치 |
|------|------|------|
| **상세 가이드** | 5개 시나리오 완전 설명 | `INTEGRATION_TEST_GUIDE.md` |
| **C# 시뮬레이터** | 소스 코드 | `OCPP201ChargerSimulator.cs` |
| **Python 서버** | OCPP 메시지 처리 | `ocpp_server.py` |
| **검증 스크립트** | 자동 결과 검증 | `verify_test_results.py` |

---

## 📞 빠른 참고

```powershell
# 현재 디렉토리 구조
C:\Project\OCPP201(P2M)\
├── ocpp_server.py                          # Python 서버 (9000, 8080)
├── test_csharp_integration.py               # 테스트 클라이언트
├── verify_test_results.py                   # 결과 검증
├── run_tests.bat                            # 배치 메뉴
├── OCPP201ChargerSimulator.cs               # C# 시뮬레이터 (선택사항)
├── INTEGRATION_TEST_GUIDE.md                # 상세 가이드
└── requirements.txt                         # Python 의존성

# 포트 정보
Python OCPP 서버:  ws://localhost:9000
REST API 서버:     http://localhost:8080
PostgreSQL DB:     localhost:5432 (charger_db)
GIS 대시보드:      http://localhost:8080/advanced_dashboard.html

# 데이터베이스 자격증명
User:     charger_user
Password: admin
Database: charger_db
```

---

**⏱️ 총 소요시간: 5분**  
**📊 테스트 대상: 34 EV 충전기 (Emart 3개 점포)**  
**✅ 상태: 즉시 실행 가능**
