# OCPP 2.0.1 C# 시뮬레이터 - 연동 테스트 시나리오 및 가이드

## 📋 개요

이 문서는 OCPP 2.0.1 기반 C# 시뮬레이터를 Python 기반 OCPP 서버와 연동하여 테스트하기 위한 상세한 시나리오와 방법을 제공합니다.

---

## 🎯 테스트 목표

1. **기본 연결 테스트**: WebSocket 기반 OCPP 통신 확인
2. **메시지 흐름 테스트**: BootNotification → Heartbeat → TransactionEvent
3. **제어 명령 테스트**: 서버에서 충전기 제어 가능 확인
4. **통계 데이터 검증**: 실제 충전 데이터가 올바르게 기록되는지 확인
5. **다중 충전기 관리**: 동시에 여러 충전기 관리 가능 확인

---

## 📦 필수 설정

### C# 프로젝트 준비

```bash
# Visual Studio 또는 dotnet CLI에서
dotnet new console -n OCPP201ChargerSimulator
cd OCPP201ChargerSimulator

# WebSocketSharp NuGet 패키지 설치
dotnet add package WebSocketSharp
```

### Python 서버 준비

```bash
# Python OCPP 서버 설정
cd c:\Project\OCPP201(P2M)
pip install websockets python-socketio

# 기존 서버 또는 새 서버 실행
python ocpp_server.py
```

---

## 🔄 테스트 시나리오

### **시나리오 1: 기본 연결 및 BootNotification**

#### 목표
충전기가 서버에 성공적으로 연결되고 BootNotification을 전송한다.

#### 시간
약 5초

#### 단계별 진행

```
1. [C#] 충전기 시뮬레이터 실행
   └─> WebSocket 연결 시도 (ws://localhost:9000/charger_001)

2. [Python] 서버 연결 수락
   └─> 연결 로그 출력
   └─> 충전기 등록

3. [C#] BootNotification 메시지 전송
   message = [
       2,  // CALL
       "msg_id_001",
       "BootNotification",
       {
           "chargingStation": {
               "model": "ABB Terra 53",
               "vendorName": "ABB",
               "serialNumber": "SN-emart_jeju_01-001",
               "firmwareVersion": "1.0.0"
           },
           "reason": "PowerUp"
       }
   ]

4. [Python] BootNotification 수신 및 처리
   └─> CALLRESULT 응답 전송
   └─> 데이터베이스에 부팅 기록

5. [C#] CALLRESULT 수신 및 Heartbeat 시작
   └─> 30초 간격 Heartbeat 전송 시작
```

#### 예상 결과

```
✅ [emart_jeju_01] 서버 연결 성공
📤 [emart_jeju_01] BootNotification 전송
📥 [emart_jeju_01] 메시지 수신: [3, "msg_id_001", {...}]
✅ [emart_jeju_01] CALLRESULT 수신: msg_id_001
💓 [emart_jeju_01] Heartbeat 전송 (HH:mm:ss)
```

#### 검증

```sql
-- Python 서버 데이터베이스에서 확인
SELECT * FROM charger_usage_log 
WHERE charger_id = 'emart_jeju_01' 
ORDER BY created_at DESC 
LIMIT 5;

-- 결과: BootNotification, Heartbeat 기록 확인
```

---

### **시나리오 2: 충전 세션 (Start → Charging → Stop)**

#### 목표
완전한 충전 세션 생명 주기를 테스트한다.
- 충전 시작
- 진행 중 전력 소비 및 에너지 누적
- 충전 중지

#### 시간
약 30초 (가속 시뮬레이션)

#### 단계별 진행

```
1. [C#] StartChargingAsync("token_user_001") 호출
   ├─ 상태: Available → Preparing
   └─ TransactionId 생성

2. [C#] TransactionEvent (Started) 전송
   message = [
       2,
       "msg_id_002",
       "TransactionEvent",
       {
           "eventType": "Started",
           "timestamp": "2026-01-21T...",
           "transactionData": {
               "transactionId": "abc12345",
               "chargingState": "Preparing",
               "totalCost": 0
           }
       }
   ]

3. [Python] TransactionEvent 수신
   └─> 거래 기록 시작
   └─> 세션 ID 생성

4. [C#] 상태: Preparing → Charging
   └─ 전력: 0kW → 100kW 설정
   └─ 에너지 누적 시작

5. [C#] 5초 간격으로 TransactionEvent (Updated) 전송
   ├─ _energyAccumulated 증가
   ├─ _currentPower 변경 (80% 이후 감소)
   └─ 메시지 반복

   message = [
       2,
       "msg_id_003",
       "TransactionEvent",
       {
           "eventType": "Updated",
           "timestamp": "2026-01-21T...",
           "transactionData": {
               "transactionId": "abc12345",
               "chargingState": "Charging",
               "totalCost": 3000,  // (kWh × ₩150)
               "chargingPeriods": [{
                   "dimensions": [
                       {"name": "Energy.Active.Import.Register", "value": 8500},
                       {"name": "Power.Active.Import", "value": 95000}
                   ]
               }]
           }
       }
   ]

6. [C#] StopChargingAsync() 호출
   ├─ 상태: Charging → Finishing
   └─ TransactionEvent (Updated) 전송

7. [C#] TransactionEvent (Ended) 전송
   message = [
       2,
       "msg_id_004",
       "TransactionEvent",
       {
           "eventType": "Ended",
           "timestamp": "2026-01-21T...",
           "transactionData": {
               "transactionId": "abc12345",
               "chargingState": "Finishing",
               "totalCost": 6000,
               "stoppedReason": "Local",
               "chargingPeriods": [{...}]
           }
       }
   ]

8. [C#] 상태: Finishing → Available
   └─ 전력: 100kW → 0kW
```

#### 예상 결과

```
🔌 [emart_jeju_01] 충전 시작: abc12345
💸 [emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
💸 [emart_jeju_01] TransactionEvent 전송 (Updated): 0.50 kWh
💸 [emart_jeju_01] TransactionEvent 전송 (Updated): 1.00 kWh
💸 [emart_jeju_01] TransactionEvent 전송 (Updated): 1.50 kWh
...
⏹️ [emart_jeju_01] 충전 중지: abc12345 (누적: 20.15 kWh)
```

#### 검증

```sql
-- 거래 기록 확인
SELECT * FROM charger_usage_log 
WHERE charger_id = 'emart_jeju_01' 
AND transaction_id = 'abc12345'
ORDER BY created_at;

-- 예상 칼럼:
-- - charger_id: emart_jeju_01
-- - station_id: emart_jeju_main
-- - start_time: 2026-01-21 14:30:00
-- - end_time: 2026-01-21 14:30:30
-- - energy_consumed: 20.15 kWh
-- - cost: 3000 (또는 6000)

-- 통계 확인
SELECT * FROM charger_info 
WHERE charger_id = 'emart_jeju_01';
```

---

### **시나리오 3: 서버에서 충전 제어**

#### 목표
Python 서버에서 C# 충전기에 RequestStartTransaction, RequestStopTransaction 명령을 전송하고 충전기가 올바르게 응답한다.

#### 시간
약 20초

#### 단계별 진행

```
1. [C#] 충전기 대기 상태 (Available)

2. [Python] RequestStartTransaction 전송
   message = [
       2,
       "msg_id_server_001",
       "RequestStartTransaction",
       {
           "idToken": {
               "idToken": "token_user_003",
               "type": "Central"
           },
           "evseId": 1,
           "connectorId": 1
       }
   ]

3. [C#] RequestStartTransaction 수신
   └─ HandleRequestStartTransaction() 메서드 호출

4. [C#] CALLRESULT 응답
   message = [
       3,
       "msg_id_server_001",
       {"status": "Accepted"}
   ]

5. [C#] 자동으로 충전 시작
   ├─ StartChargingAsync("token_user_003") 호출
   └─ TransactionEvent (Started) 전송

6. [C#] 충전 중 (약 10초 진행)

7. [Python] RequestStopTransaction 전송
   message = [
       2,
       "msg_id_server_002",
       "RequestStopTransaction",
       {
           "transactionId": "def67890"
       }
   ]

8. [C#] RequestStopTransaction 수신
   └─ HandleRequestStopTransaction() 메서드 호출

9. [C#] CALLRESULT 응답
   message = [
       3,
       "msg_id_server_002",
       {"status": "Accepted"}
   ]

10. [C#] 충전 중지
    └─ StopChargingAsync() 호출
    └─ TransactionEvent (Ended) 전송
```

#### 예상 결과

```
🔔 [emart_jeju_01] CALL 수신: RequestStartTransaction
🔑 [emart_jeju_01] RequestStartTransaction: token_user_003
📤 [emart_jeju_01] CALLRESULT 전송: msg_id_server_001
🔌 [emart_jeju_01] 충전 시작: def67890
💸 [emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
💓 [emart_jeju_01] Heartbeat 전송
💸 [emart_jeju_01] TransactionEvent 전송 (Updated): 0.50 kWh
🔔 [emart_jeju_01] CALL 수신: RequestStopTransaction
⏹️ [emart_jeju_01] RequestStopTransaction
📤 [emart_jeju_01] CALLRESULT 전송: msg_id_server_002
⏹️ [emart_jeju_01] 충전 중지: def67890 (누적: 5.00 kWh)
```

#### 검증

```bash
# Python 서버에서 명령 실행
curl -X POST http://localhost:8080/chargers/emart_jeju_01/start \
  -H "Content-Type: application/json" \
  -d '{"evse_id": 1, "connector_id": 1}'

# 응답: {"status": "success"}

curl -X POST http://localhost:8080/chargers/emart_jeju_01/stop \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "def67890"}'

# 응답: {"status": "success"}
```

---

### **시나리오 4: 다중 충전기 동시 운영**

#### 목표
여러 충전기가 동시에 서버에 연결되고 각각 독립적으로 충전 세션을 진행한다.

#### 시간
약 45초

#### 배경

```
이마트 제주점:
  - emart_jeju_01 (100kW)
  - emart_jeju_02 (100kW)
  - emart_jeju_03 (100kW)

이마트 신제주점:
  - emart_shinjeju_01 (50kW)
  - emart_shinjeju_02 (50kW)
```

#### 단계별 진행

```
1. [C#] 5개 충전기 생성 및 연결
   await charger1.ConnectAsync();  // emart_jeju_01
   await charger2.ConnectAsync();  // emart_jeju_02
   await charger3.ConnectAsync();  // emart_jeju_03
   await charger4.ConnectAsync();  // emart_shinjeju_01
   await charger5.ConnectAsync();  // emart_shinjeju_02

   [각 충전기별로 병렬로 BootNotification 전송]

2. [C#] 제주점의 3개 충전기 충전 시작
   await charger1.StartChargingAsync("user_001");  // 100kW
   await charger2.StartChargingAsync("user_002");  // 100kW
   await charger3.StartChargingAsync("user_003");  // 100kW

   [총 300kW 동시 충전]

3. [C#] 신제주점의 2개 충전기 충전 시작
   await charger4.StartChargingAsync("user_004");  // 50kW
   await charger5.StartChargingAsync("user_005");  // 50kW

   [총 350kW 동시 충전]

4. [C#] 모든 충전기가 약 15초 동안 충전
   ├─ 각 충전기가 5초 간격으로 TransactionEvent 전송
   ├─ 30초 간격으로 Heartbeat 전송
   └─ 모든 메시지가 서버에 기록됨

5. [C#] 제주점의 3개 충전기 충전 중지
   await charger1.StopChargingAsync();
   await charger2.StopChargingAsync();
   await charger3.StopChargingAsync();

   [각 충전기별로 TransactionEvent (Ended) 전송]

6. [C#] 신제주점의 2개 충전기 충전 중지
   await charger4.StopChargingAsync();
   await charger5.StopChargingAsync();

   [각 충전기별로 TransactionEvent (Ended) 전송]

7. [C#] 모든 충전기 상태 확인
   └─ 모두 Available 상태로 복귀
```

#### 예상 결과

```
✅ [emart_jeju_01] 서버 연결 성공
✅ [emart_jeju_02] 서버 연결 성공
✅ [emart_jeju_03] 서버 연결 성공
✅ [emart_shinjeju_01] 서버 연결 성공
✅ [emart_shinjeju_02] 서버 연결 성공

🔌 [emart_jeju_01] 충전 시작: tx_001
🔌 [emart_jeju_02] 충전 시작: tx_002
🔌 [emart_jeju_03] 충전 시작: tx_003
🔌 [emart_shinjeju_01] 충전 시작: tx_004
🔌 [emart_shinjeju_02] 충전 시작: tx_005

💸 [emart_jeju_01] TransactionEvent 전송 (Updated): 8.50 kWh
💸 [emart_jeju_02] TransactionEvent 전송 (Updated): 8.50 kWh
💸 [emart_jeju_03] TransactionEvent 전송 (Updated): 8.50 kWh
💸 [emart_shinjeju_01] TransactionEvent 전송 (Updated): 4.25 kWh
💸 [emart_shinjeju_02] TransactionEvent 전송 (Updated): 4.25 kWh

⏹️ [emart_jeju_01] 충전 중지: tx_001 (누적: 25.50 kWh)
⏹️ [emart_jeju_02] 충전 중지: tx_002 (누적: 25.50 kWh)
⏹️ [emart_jeju_03] 충전 중지: tx_003 (누적: 25.50 kWh)
⏹️ [emart_shinjeju_01] 충전 중지: tx_004 (누적: 12.75 kWh)
⏹️ [emart_shinjeju_02] 충전 중지: tx_005 (누적: 12.75 kWh)

✅ 모든 테스트 완료!
```

#### 검증

```sql
-- 모든 거래 기록 확인
SELECT 
    charger_id,
    COUNT(*) as session_count,
    SUM(CASE WHEN energy_consumed > 0 THEN energy_consumed ELSE 0 END) as total_energy,
    COUNT(DISTINCT DATE(start_time)) as distinct_days
FROM charger_usage_log
WHERE charger_id LIKE 'emart_%'
AND start_time >= NOW() - INTERVAL 1 HOUR
GROUP BY charger_id
ORDER BY charger_id;

-- 예상 결과:
-- emart_jeju_01 | 1 | 25.50 | 1
-- emart_jeju_02 | 1 | 25.50 | 1
-- emart_jeju_03 | 1 | 25.50 | 1
-- emart_shinjeju_01 | 1 | 12.75 | 1
-- emart_shinjeju_02 | 1 | 12.75 | 1

-- 시간별 전력 사용량
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    SUM(power_reading) as total_power_w
FROM power_consumption
WHERE timestamp >= NOW() - INTERVAL 1 HOUR
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

-- 예상: 350,000W (350kW) 정점
```

---

### **시나리오 5: 에러 처리 및 재연결**

#### 목표
네트워크 오류, 타임아웃, 예외 상황을 처리한다.

#### 시간
약 30초

#### 단계별 진행

```
1. [C#] 충전기 연결 및 정상 작동

2. [Python] 서버 강제 종료
   └─ WebSocket 연결 끊김

3. [C#] OnWebSocketClose 이벤트 감지
   └─ _isConnected = false
   └─ 로그: "🔌 [emart_jeju_01] 연결 종료"

4. [C#] 자동 재연결 시도 (구현 시)
   └─ 지수 백오프 (1초, 2초, 4초...)
   └─ 최대 5회 재시도

5. [Python] 서버 재시작

6. [C#] 재연결 성공
   └─ WebSocket 다시 연결
   └─ BootNotification 재전송

7. [C#] 정상 작동 재개
   └─ Heartbeat 재시작
   └─ 거래 재개
```

#### 예상 결과

```
❌ [emart_jeju_01] WebSocket 오류: Connection closed normally
🔌 [emart_jeju_01] 연결 종료: 1000

🔄 [emart_jeju_01] 재연결 시도 1/5...
🔄 [emart_jeju_01] 재연결 시도 2/5...

✅ [emart_jeju_01] 서버 연결 성공
📤 [emart_jeju_01] BootNotification 전송
💓 [emart_jeju_01] Heartbeat 전송

[정상 작동 재개]
```

---

## 🔧 실행 방법

### 방법 1: Visual Studio에서 실행

```
1. OCPP201ChargerSimulator.sln 열기
2. Main() 메서드에서 테스트할 시나리오 선택
3. Ctrl+F5로 실행
```

### 방법 2: dotnet CLI에서 실행

```bash
# 빌드
dotnet build

# 실행
dotnet run
```

### 방법 3: 컴파일된 EXE 실행

```bash
cd bin\Release\net6.0
OCPP201ChargerSimulator.exe
```

---

## 📊 모니터링 및 로깅

### C# 시뮬레이터 로그

```
✅ [충전기_ID] 서버 연결 성공
📤 [충전기_ID] 메시지 유형 전송
📥 [충전기_ID] 메시지 수신
💸 [충전기_ID] TransactionEvent 전송
💓 [충전기_ID] Heartbeat 전송
🔌 [충전기_ID] 상태: [상태명]
❌ [충전기_ID] 오류: [오류 메시지]
```

### Python 서버 로그

```
INFO: Charger emart_jeju_01 connected
INFO: BootNotification received from emart_jeju_01
INFO: TransactionEvent started - tx_001
INFO: TransactionEvent updated - tx_001 (8.5 kWh)
INFO: TransactionEvent ended - tx_001 (25.5 kWh)
DEBUG: RequestStartTransaction sent to emart_jeju_01
```

### 데이터베이스 확인

```bash
# PostgreSQL 접속
psql -U charger_user -d charger_db -h localhost

# 최근 거래 확인
SELECT charger_id, transaction_id, start_time, end_time, energy_consumed 
FROM charger_usage_log 
ORDER BY created_at DESC 
LIMIT 10;

# 충전기별 통계
SELECT charger_id, COUNT(*) as sessions, SUM(energy_consumed) as total_energy
FROM charger_usage_log
GROUP BY charger_id;
```

---

## ✅ 테스트 체크리스트

- [ ] 시나리오 1: 기본 연결 및 BootNotification 완료
- [ ] 시나리오 2: 충전 세션 (Start → Charging → Stop) 완료
- [ ] 시나리오 3: 서버에서 충전 제어 완료
- [ ] 시나리오 4: 다중 충전기 동시 운영 완료
- [ ] 시나리오 5: 에러 처리 및 재연결 완료
- [ ] 데이터베이스에 모든 거래 기록 확인
- [ ] GIS 대시보드에서 실시간 상태 업데이트 확인
- [ ] 통계 데이터 정확성 검증
- [ ] 성능 테스트 (최대 동시 충전기 수 확인)

---

## 📝 문제 해결

### Q: C# 충전기가 서버에 연결되지 않음
**A:** 
1. 서버가 실행 중인지 확인: `python ocpp_server.py`
2. 포트 9000이 열려있는지 확인: `netstat -an | findstr 9000`
3. 방화벽 설정 확인

### Q: TransactionEvent가 서버에 기록되지 않음
**A:**
1. BootNotification이 먼저 전송되어야 함
2. TransactionId가 고유한지 확인
3. 서버 로그에서 오류 메시지 확인

### Q: Heartbeat가 전송되지 않음
**A:**
1. BootNotification이 성공했는지 확인 (_isBootNotificationSent)
2. StartHeartbeat()이 호출되었는지 확인
3. 연결 상태 확인 (_isConnected)

---

## 🎓 추가 학습 자료

- [OCPP 2.0.1 공식 문서](https://openchargealliance.org/)
- [WebSocket 프로토콜](https://tools.ietf.org/html/rfc6455)
- [JSON-RPC 2.0 사양](https://www.jsonrpc.org/specification)

