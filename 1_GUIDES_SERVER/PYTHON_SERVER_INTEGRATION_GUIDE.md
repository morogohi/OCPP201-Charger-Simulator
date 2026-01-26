# Python OCPP 서버 - C# 시뮬레이터 연동 가이드

## 📋 개요

이 가이드는 Python 기반 OCPP 2.0.1 서버가 C# 시뮬레이터와 상호 작동하도록 설정하는 방법을 설명합니다.

---

## 🔧 서버 설정

### 1. 필수 패키지 설치

```bash
pip install python-socketio
pip install websockets
pip install aiohttp
pip install asyncio
```

### 2. WebSocket 서버 포트 설정

기본 포트는 `9000`입니다. (`ocpp_server.py` 확인)

```python
async def main():
    server = OCPPServer(host="0.0.0.0", port=9000)  # ← 이 포트
    await server.start()
```

### 3. 방화벽 설정

```bash
# Windows Firewall에서 9000 포트 허용
netsh advfirewall firewall add rule name="OCPP Server" dir=in action=allow protocol=tcp localport=9000
```

---

## 📡 메시지 처리 흐름

### BootNotification 처리

```python
async def on_boot_notification(charger_id, message):
    """
    C# 시뮬레이터로부터 BootNotification 수신
    
    수신 메시지 예:
    [2, "msg_id", "BootNotification", {
        "chargingStation": {
            "model": "ABB Terra 53",
            "vendorName": "ABB",
            "serialNumber": "SN-emart_jeju_01-001"
        },
        "reason": "PowerUp"
    }]
    """
    
    print(f"✅ BootNotification 수신: {charger_id}")
    
    # 데이터베이스에 부팅 기록
    log_boot_event(
        charger_id=charger_id,
        vendor=message.get("chargingStation", {}).get("vendorName"),
        model=message.get("chargingStation", {}).get("model"),
        reason=message.get("reason")
    )
    
    # CALLRESULT 응답 (필수)
    response = {
        "currentTime": datetime.utcnow().isoformat(),
        "interval": 30,  # Heartbeat 간격 (초)
        "status": "Accepted"
    }
    
    return response
```

### Heartbeat 처리

```python
async def on_heartbeat(charger_id, message):
    """
    C# 시뮬레이터로부터 Heartbeat 수신 (30초마다)
    """
    
    print(f"💓 Heartbeat 수신: {charger_id}")
    
    # 충전기 상태를 "온라인"으로 표시
    update_charger_status(charger_id, "online", datetime.utcnow())
    
    # CALLRESULT 응답
    response = {
        "currentTime": datetime.utcnow().isoformat()
    }
    
    return response
```

### TransactionEvent 처리

```python
async def on_transaction_event(charger_id, message):
    """
    C# 시뮬레이터로부터 TransactionEvent 수신 (시작, 진행, 종료)
    """
    
    event_type = message.get("eventType")  # Started, Updated, Ended
    transaction_data = message.get("transactionData", {})
    
    print(f"💸 TransactionEvent 수신: {charger_id} - {event_type}")
    
    if event_type == "Started":
        # 충전 세션 시작
        create_charging_session(
            charger_id=charger_id,
            transaction_id=transaction_data.get("transactionId"),
            start_time=message.get("timestamp"),
            id_token="user_token"
        )
    
    elif event_type == "Updated":
        # 진행 중 업데이트
        charging_periods = transaction_data.get("chargingPeriods", [])
        
        if charging_periods:
            dimensions = charging_periods[0].get("dimensions", [])
            
            for dimension in dimensions:
                if dimension.get("name") == "Energy.Active.Import.Register":
                    energy_wh = dimension.get("value", 0)
                    energy_kwh = energy_wh / 1000
                
                elif dimension.get("name") == "Power.Active.Import":
                    power_w = dimension.get("value", 0)
                    power_kw = power_w / 1000
            
            # 거래 기록 업데이트
            update_charging_session(
                charger_id=charger_id,
                transaction_id=transaction_data.get("transactionId"),
                energy_consumed=energy_kwh,
                current_power=power_kw,
                cost=transaction_data.get("totalCost")
            )
    
    elif event_type == "Ended":
        # 충전 세션 종료
        finalize_charging_session(
            charger_id=charger_id,
            transaction_id=transaction_data.get("transactionId"),
            end_time=message.get("timestamp"),
            energy_consumed=transaction_data.get("chargingPeriods", [{}])[0]
                .get("dimensions", [{}])[0].get("value", 0) / 1000,
            cost=transaction_data.get("totalCost"),
            stop_reason=transaction_data.get("stoppedReason")
        )
    
    # CALLRESULT 응답
    response = {
        "eventType": event_type,
        "transactionId": transaction_data.get("transactionId")
    }
    
    return response
```

### StatusNotification 처리

```python
async def on_status_notification(charger_id, message):
    """
    C# 시뮬레이터로부터 StatusNotification 수신
    """
    
    status = message.get("connectorStatus")  # Available, Occupied, Unavailable, etc.
    
    print(f"📊 StatusNotification 수신: {charger_id} - {status}")
    
    # 충전기 상태 업데이트
    update_charger_status(charger_id, status)
    
    # CALLRESULT 응답
    response = {
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return response
```

---

## 🎮 서버에서 충전기 제어

### RequestStartTransaction

```python
async def request_start_transaction(charger_id, id_token, evse_id=1, connector_id=1):
    """
    충전기에 충전 시작을 요청합니다.
    C# 시뮬레이터가 RequestStartTransaction을 수신하면 자동으로 충전을 시작합니다.
    """
    
    message_id = str(uuid.uuid4())[:12]
    
    payload = {
        "idToken": {
            "idToken": id_token,
            "type": "Central"
        },
        "evseId": evse_id,
        "connectorId": connector_id,
        "requestedPower": 100  # kW
    }
    
    # CALL 메시지 전송
    message = [
        2,  # CALL
        message_id,
        "RequestStartTransaction",
        payload
    ]
    
    await send_to_charger(charger_id, json.dumps(message))
    
    # CALLRESULT 대기 (타임아웃: 30초)
    result = await wait_for_response(message_id, timeout=30)
    
    return result.get("status") == "Accepted"
```

### RequestStopTransaction

```python
async def request_stop_transaction(charger_id, transaction_id):
    """
    충전기에 충전 중지를 요청합니다.
    """
    
    message_id = str(uuid.uuid4())[:12]
    
    payload = {
        "transactionId": transaction_id
    }
    
    # CALL 메시지 전송
    message = [
        2,
        message_id,
        "RequestStopTransaction",
        payload
    ]
    
    await send_to_charger(charger_id, json.dumps(message))
    
    # CALLRESULT 대기
    result = await wait_for_response(message_id, timeout=30)
    
    return result.get("status") == "Accepted"
```

### SetChargingProfile

```python
async def set_charging_profile(charger_id, max_power_kw):
    """
    충전기의 최대 전력을 제한합니다.
    """
    
    message_id = str(uuid.uuid4())[:12]
    
    payload = {
        "chargingProfile": {
            "chargingProfileId": 1,
            "stackLevel": 0,
            "chargingProfileKind": "Absolute",
            "chargingProfilePurpose": "ChargingStationExternalConstraints",
            "chargingSchedule": {
                "duration": 3600,  # 1시간
                "chargingRateUnit": "W",
                "chargingSchedulePeriod": [
                    {
                        "startPeriod": 0,
                        "limit": max_power_kw * 1000  # W로 변환
                    }
                ]
            }
        }
    }
    
    message = [
        2,
        message_id,
        "SetChargingProfile",
        payload
    ]
    
    await send_to_charger(charger_id, json.dumps(message))
    
    result = await wait_for_response(message_id, timeout=30)
    
    return result.get("status") == "Accepted"
```

---

## 📊 REST API 엔드포인트 (제어용)

### 충전 시작

```bash
curl -X POST http://localhost:8080/chargers/emart_jeju_01/start \
  -H "Content-Type: application/json" \
  -d '{
    "id_token": "user_123",
    "evse_id": 1,
    "connector_id": 1
  }'

# 응답
{
  "status": "success",
  "transaction_id": "abc12345",
  "charger_id": "emart_jeju_01"
}
```

### 충전 중지

```bash
curl -X POST http://localhost:8080/chargers/emart_jeju_01/stop \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "abc12345"
  }'

# 응답
{
  "status": "success",
  "energy_consumed": 25.5,
  "cost": 3825
}
```

### 출력 제한 설정

```bash
curl -X PATCH http://localhost:8080/chargers/emart_jeju_01/power \
  -H "Content-Type: application/json" \
  -d '{
    "max_power_kw": 50
  }'

# 응답
{
  "status": "success",
  "current_power": 50.0
}
```

### 충전기 상태 조회

```bash
curl http://localhost:8080/chargers/emart_jeju_01

# 응답
{
  "charger_id": "emart_jeju_01",
  "status": "Charging",
  "current_power": 95.0,
  "energy_accumulated": 8.5,
  "transaction_id": "abc12345",
  "connected": true
}
```

---

## 📈 데이터베이스 통합

### 거래 기록 저장

```sql
-- 거래 시작 기록
INSERT INTO charger_usage_log (
    charger_id, station_id, transaction_id, start_time,
    energy_consumed, cost, user_id, created_at
) VALUES (
    'emart_jeju_01', 'emart_jeju_main', 'abc12345',
    NOW(), 0, 0, 'user_123', NOW()
);

-- 거래 진행 중 업데이트
UPDATE charger_usage_log
SET energy_consumed = 8.5, cost = 1275
WHERE transaction_id = 'abc12345';

-- 거래 종료 기록
UPDATE charger_usage_log
SET end_time = NOW(), energy_consumed = 25.5, cost = 3825
WHERE transaction_id = 'abc12345';
```

### 통계 계산

```sql
-- 일일 통계 업데이트
INSERT INTO daily_charger_stats (
    charger_id, date, sessions, total_energy, total_revenue
) VALUES (
    'emart_jeju_01', CURRENT_DATE,
    (SELECT COUNT(*) FROM charger_usage_log 
     WHERE charger_id = 'emart_jeju_01' 
     AND DATE(start_time) = CURRENT_DATE),
    (SELECT SUM(energy_consumed) FROM charger_usage_log 
     WHERE charger_id = 'emart_jeju_01' 
     AND DATE(start_time) = CURRENT_DATE),
    (SELECT SUM(cost) FROM charger_usage_log 
     WHERE charger_id = 'emart_jeju_01' 
     AND DATE(start_time) = CURRENT_DATE)
)
ON CONFLICT (charger_id, date) DO UPDATE SET
    sessions = EXCLUDED.sessions,
    total_energy = EXCLUDED.total_energy,
    total_revenue = EXCLUDED.total_revenue;
```

---

## 🔍 모니터링 및 디버깅

### 로깅 레벨 설정

```python
import logging

# DEBUG: 모든 메시지 출력
logging.basicConfig(level=logging.DEBUG)

# INFO: 주요 이벤트만 출력
logging.basicConfig(level=logging.INFO)
```

### 메시지 덤프

```python
async def on_any_message(charger_id, message):
    """모든 OCPP 메시지를 로그 파일에 저장"""
    
    with open(f"logs/ocpp_{charger_id}.log", "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {json.dumps(message, indent=2)}\n")
```

### 성능 모니터링

```python
import time
from collections import defaultdict

message_times = defaultdict(list)

async def measure_message_time(charger_id, action, duration):
    """메시지 처리 시간 측정"""
    
    message_times[action].append(duration)
    
    avg_time = sum(message_times[action]) / len(message_times[action])
    
    print(f"[{action}] 평균 처리 시간: {avg_time*1000:.2f}ms")
```

---

## ⚠️ 문제 해결

### 연결 거부

```
오류: Connection refused from 127.0.0.1:12345
원인: 서버가 실행 중이 아님
해결: python ocpp_server.py 실행
```

### 메시지 타임아웃

```
오류: RequestStartTransaction timeout
원인: C# 충전기가 응답하지 않음
해결: 
1. 충전기 연결 상태 확인
2. 충전기 로그에서 CALL 수신 여부 확인
3. Heartbeat 신호 확인
```

### 트랜잭션 ID 불일치

```
오류: Unknown transaction ID abc12345
원인: TransactionEvent에서 받은 ID와 CALL에서 전송한 ID 불일치
해결: 
1. C# 시뮬레이터의 TransactionId 생성 로직 확인
2. 메시지 로그에서 ID 추적
3. UUID 형식 확인
```

---

## ✅ 통합 테스트 체크리스트

- [ ] 서버 포트 9000이 열려있음
- [ ] C# 충전기가 BootNotification을 전송
- [ ] 서버가 CALLRESULT로 응답
- [ ] Heartbeat가 30초 간격으로 수신됨
- [ ] TransactionEvent가 시작/진행/종료 단계에서 수신됨
- [ ] RequestStartTransaction이 C#에서 처리됨
- [ ] RequestStopTransaction이 C#에서 처리됨
- [ ] 데이터베이스에 모든 거래가 기록됨
- [ ] GIS 대시보드에 실시간 데이터가 표시됨
- [ ] 다중 충전기 동시 처리 가능

---

## 🎓 추가 자료

- [OCPP 2.0.1 사양](https://openchargealliance.org/)
- [JSON-RPC 2.0 명세](https://www.jsonrpc.org/)
- [WebSocket RFC 6455](https://tools.ietf.org/html/rfc6455)

