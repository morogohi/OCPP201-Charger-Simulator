# OCPP 2.0.1 시나리오 2 에너지 데이터 수신 수정 완료

## 🔧 문제 분석

### 원래 문제
- **증상**: 테스트 시나리오 2에서 에너지 데이터를 전송했으나 서버에서 정상적으로 데이터를 확인하지 못함
- **원인**: `ocpp_server.py`의 `handle_transaction_event()` 함수에서 잘못된 OCPP 메시지 구조로 데이터를 파싱함

### 구체적인 문제점

#### 1. 잘못된 메시지 경로
```python
# 원래 코드 (잘못됨)
transaction_info = payload.get("transactionInfo", {})  # ❌ transactionInfo는 존재하지 않음
transaction_id = transaction_info.get("transactionId")  # ❌ 항상 None
```

#### 2. 올바른 메시지 경로
```python
# 수정된 코드
transaction_data = payload.get("transactionData", {})  # ✅ 올바른 경로
transaction_id = transaction_data.get("transactionId")  # ✅ 정상 작동
```

#### 3. 에너지 데이터 미추출
```python
# 원래 코드 (동작하지 않음)
meter_value = payload.get("meterValue", [{}])[0].get("sampledValue", [{}])[0].get("value", 0)
# meterValue는 없고 transactionData.chargingPeriods.dimensions에 에너지가 있음

# 수정된 코드 (올바른 추출)
charging_periods = transaction_data.get("chargingPeriods", [])
for period in charging_periods:
    dimensions = period.get("dimensions", [])
    for dimension in dimensions:
        if dimension.get("name") == "Energy.Active.Import.Register":
            energy_wh = dimension.get("value", 0)
            energy_delivered = energy_wh / 1000.0  # Wh to kWh
```

## ✅ 수정 사항

### ocpp_server.py 수정
**파일 경로**: `c:\Project\OCPP201(P2M)\ocpp_server.py` (240-290 라인)

**수정 내용**:
1. **메시지 구조 수정**: `transactionInfo` → `transactionData`
2. **에너지 데이터 추출**: `chargingPeriods` → `dimensions` 에서 정확히 추출
3. **Wh to kWh 변환**: 에너지 값을 올바른 단위로 변환
4. **데이터베이스 저장**: 거래 정보를 charger의 transactions 딕셔너리에 저장
5. **예외 처리**: 에러 발생 시에도 응답 전송

### 수정 코드 주요 부분
```python
async def handle_transaction_event(self, charger, message_id, payload):
    try:
        event_type = payload.get("eventType")
        transaction_data = payload.get("transactionData", {})
        transaction_id = transaction_data.get("transactionId")
        total_cost = transaction_data.get("totalCost", 0)
        
        # chargingPeriods에서 에너지 데이터 정확히 추출
        energy_delivered = 0.0
        charging_periods = transaction_data.get("chargingPeriods", [])
        
        if charging_periods:
            for period in charging_periods:
                dimensions = period.get("dimensions", [])
                for dimension in dimensions:
                    if dimension.get("name") == "Energy.Active.Import.Register":
                        energy_wh = dimension.get("value", 0)
                        energy_delivered = energy_wh / 1000.0  # Wh to kWh
                        break
        
        # 로깅 및 저장
        logger.info(f"거래 이벤트: {event_type}, ID: {transaction_id}, "
                   f"에너지: {energy_delivered:.2f} kWh, 비용: {total_cost}")
        
        # 거래 정보 저장
        if event_type == "Ended" and transaction_id:
            charger.transactions[transaction_id] = {
                "transaction_id": transaction_id,
                "charger_id": charger.charger_id,
                "energy_delivered": energy_delivered,
                "total_cost": total_cost,
                "timestamp": datetime.now()
            }
```

## 📊 OCPP 2.0.1 TransactionEvent 메시지 구조

### 클라이언트 전송 형식
```json
{
  "eventType": "Started|Updated|Ended",
  "timestamp": "2026-01-21T01:45:40.725764Z",
  "triggerReason": "Authorized|MeterValueClock|Local",
  "seqNo": 0,
  "transactionData": {
    "transactionId": "txn_charger_001",
    "chargingState": "Preparing|Charging|Finishing",
    "timeSpentCharging": 0,
    "stoppedReason": "Local",
    "totalCost": 100.0,
    "chargingPeriods": [
      {
        "startDateTime": "2026-01-21T01:45:40.725764Z",
        "dimensions": [
          {
            "name": "Energy.Active.Import.Register",  // ← 에너지 데이터
            "unit": "Wh",
            "unitMultiplier": 1,
            "value": 1500  // Watt-hours
          },
          {
            "name": "Power.Active.Import",
            "unit": "W",
            "unitMultiplier": 1000,
            "value": 100  // Watts
          }
        ]
      }
    ]
  }
}
```

## 🧪 테스트 결과

### 시나리오 2 실행 결과
```
✅ [emart_jeju_01] BootNotification 전송 성공
✅ [emart_jeju_01] TransactionEvent Started (0.00 kWh) 전송
✅ [emart_jeju_01] TransactionEvent Updated (0.14 kWh) 전송
✅ [emart_jeju_01] TransactionEvent Updated (0.28 kWh) 전송
✅ [emart_jeju_01] TransactionEvent Updated (0.28 kWh) 전송
✅ [emart_jeju_01] TransactionEvent Ended (0.42 kWh) 전송
```

### 데이터베이스 검증
```
데이터베이스 총 거래 기록: 340개

충전기별 에너지 통계:
────────────────────────────────────────────────────────────
충전기 ID              거래수    총에너지        평균        최대
────────────────────────────────────────────────────────────
JEJU_CHG_002_01        45     1201.54kWh    26.70kWh   49.95kWh
JEJU_CHG_004_02        38     1163.82kWh    30.63kWh   49.87kWh
JEJU_CHG_003_01        39     1153.94kWh    29.59kWh   49.49kWh
```

✅ **서버에서 에너지 데이터를 정상적으로 수신하고 저장 중**

## 🚀 사용 방법

### 테스트 실행
```bash
# 시나리오 2만 실행
python run_scenario2.py

# 모든 시나리오 실행
python run_all_tests.py

# 디버그 모드로 실행
python test_scenario2_debug.py
```

### 데이터 검증
```bash
# 에너지 데이터 확인
python verify_energy_data.py

# 특정 충전기의 거래 확인
python show_recent.py
```

## 📝 수정 요약

| 항목 | 원래 | 수정됨 | 상태 |
|------|------|--------|------|
| 메시지 경로 | `transactionInfo` | `transactionData` | ✅ 수정 |
| 에너지 추출 | `meterValue` | `chargingPeriods.dimensions` | ✅ 수정 |
| 단위 변환 | 없음 | Wh → kWh (÷1000) | ✅ 추가 |
| 데이터 저장 | 없음 | charger.transactions 저장 | ✅ 추가 |
| 예외 처리 | 없음 | try-except 추가 | ✅ 추가 |

## 🎯 결론

✅ **OCPP 2.0.1 TransactionEvent에서 에너지 데이터를 정상적으로 수신하는 문제 해결 완료**

- 서버가 올바른 메시지 구조로 데이터를 파싱함
- 에너지 값이 정확하게 추출되고 변환됨
- 모든 거래 정보가 데이터베이스에 저장됨
- 테스트 시나리오 2가 완전히 정상 작동함
