# OCPP 프로토콜 디버그 로깅 사용 가이드

## 개요

OCPP 2.0.1 시스템의 모든 메시지 송수신을 상세히 로깅할 수 있습니다. 이 기능은 프로토콜 디버깅, 문제 해결, 성능 분석에 유용합니다.

## 빠른 시작

### 1️⃣ 가장 간단한 방법 - 전용 데모 실행

```bash
python demo_protocol_debug.py
```

**자동으로:**
- 프로토콜 디버그 활성화
- 로그 파일 생성 (`ocpp_protocol_debug.log`)
- 상세 메시지 출력

### 2️⃣ 환경변수로 활성화 (권장)

#### Windows (PowerShell)
```powershell
$env:OCPP_PROTOCOL_DEBUG = 'true'
python demo.py
```

#### Windows (Command Prompt)
```cmd
set OCPP_PROTOCOL_DEBUG=true
python demo.py
```

#### Linux/macOS
```bash
export OCPP_PROTOCOL_DEBUG=true
python demo.py
```

### 3️⃣ Python 코드에서 활성화

```python
import os
from logging_config import setup_logging
from demo import main
import asyncio

# 프로토콜 디버그 활성화
setup_logging(
    level='DEBUG',
    enable_protocol_debug=True,
    log_file='ocpp_debug.log'
)

# 애플리케이션 실행
asyncio.run(main())
```

## 로그 태그 설명

### 📤 전송 메시지 (SEND)

| 태그 | 설명 |
|------|------|
| `[OCPP-CALL-SEND]` | Call 메시지 생성 (요청) |
| `[OCPP-PAYLOAD-SEND]` | 요청 페이로드 (JSON) |
| `[OCPP-CALLRESULT-SEND]` | CallResult 생성 (응답) |
| `[OCPP-RESPONSE-SEND]` | 응답 페이로드 (JSON) |
| `[OCPP-CALLERROR-SEND]` | CallError 생성 (오류) |
| `[OCPP-ERROR-SEND]` | 오류 코드 및 메시지 |
| `[CHARGER-SEND]` | 충전기 원본 메시지 |
| `[SERVER-SEND]` | 서버 원본 메시지 |

### 📥 수신 메시지 (RECV)

| 태그 | 설명 |
|------|------|
| `[OCPP-CALL-RECV]` | Call 메시지 수신 |
| `[OCPP-PAYLOAD-RECV]` | 수신 페이로드 (JSON) |
| `[OCPP-CALLRESULT-RECV]` | CallResult 수신 |
| `[OCPP-RESPONSE-RECV]` | 수신 응답 (JSON) |
| `[OCPP-CALLERROR-RECV]` | CallError 수신 |
| `[OCPP-ERROR-RECV]` | 수신 오류 정보 |
| `[OCPP-RAW-RECV]` | 원본 JSON 메시지 |
| `[CHARGER-RECV]` | 충전기 원본 메시지 |
| `[SERVER-RECV]` | 서버 원본 메시지 |

## 예제 로그 출력

### BootNotification 메시지 예

```
2026-01-19 16:01:23 - ocpp_messages - DEBUG - [OCPP-CALL-SEND] Action: BootNotification, ID: 3094b700-89c2-419b
2026-01-19 16:01:23 - ocpp_messages - DEBUG - [OCPP-PAYLOAD-SEND] {
  "reason": "PowerUp",
  "chargingStation": {
    "model": "Debug Charger",
    "vendorName": "TestVendor",
    "serialNumber": "charger_debug_001",
    "firmwareVersion": "1.0.0"
  }
}
2026-01-19 16:01:23 - charger_simulator - DEBUG - [CHARGER-SEND] charger_debug_001: [2,"3094b700-89c2-419b","BootNotification",...
2026-01-19 16:01:23 - ocpp_server - DEBUG - [SERVER-RECV] charger_debug_001: [2,"3094b700-89c2-419b","BootNotification",...
2026-01-19 16:01:23 - ocpp_messages - DEBUG - [OCPP-CALL-RECV] Action: BootNotification, ID: 3094b700-89c2-419b
2026-01-19 16:01:23 - ocpp_messages - DEBUG - [OCPP-PAYLOAD-RECV] {
  "reason": "PowerUp",
  "chargingStation": {...}
}
```

### TransactionEvent 메시지 예

```
2026-01-19 16:01:25 - ocpp_messages - DEBUG - [OCPP-CALL-SEND] Action: TransactionEvent, ID: d7334ce9-c497-460c
2026-01-19 16:01:25 - ocpp_messages - DEBUG - [OCPP-PAYLOAD-SEND] {
  "eventType": "Started",
  "timestamp": "2026-01-19T16:01:25.000000Z",
  "transactionInfo": {
    "transactionId": "0d183dd1-c01f-4ae1-a864-493d5b601a00",
    "chargingState": "Charging"
  },
  "evseId": 1,
  "connectorId": 1,
  "meterValue": [{
    "timestamp": "2026-01-19T16:01:25.000000Z",
    "sampledValue": [
      {"value": 0.0, "context": "Sample.Periodic", "measurand": "Energy.Active.Import.Register", "unit": "kWh"},
      {"value": 400.0, "measurand": "Voltage", "unit": "V"},
      {"value": 0.0, "measurand": "Current.Import", "unit": "A"}
    ]
  }]
}
```

## 로그 레벨 설정

### 환경변수로 설정

```powershell
# DEBUG: 모든 로그 표시 (매우 상세함)
$env:OCPP_LOG_LEVEL = 'DEBUG'

# INFO: 일반 정보 + 프로토콜 메시지 (권장)
$env:OCPP_LOG_LEVEL = 'INFO'

# WARNING: 경고 및 오류만 표시
$env:OCPP_LOG_LEVEL = 'WARNING'

# ERROR: 오류만 표시
$env:OCPP_LOG_LEVEL = 'ERROR'
```

## 로그 파일에 저장

### 환경변수로 지정

```powershell
$env:OCPP_PROTOCOL_DEBUG = 'true'
$env:OCPP_LOG_FILE = 'my_ocpp_log.log'
python demo.py
```

### Python 코드에서 지정

```python
from logging_config import setup_logging

setup_logging(
    level='DEBUG',
    enable_protocol_debug=True,
    log_file='ocpp_messages.log'  # 로그 파일 경로
)
```

## 로그 필터링

### 특정 메시지 유형만 보기 (PowerShell)

```powershell
# BootNotification만
Select-String "BootNotification" ocpp_protocol_debug.log

# TransactionEvent만
Select-String "TransactionEvent" ocpp_protocol_debug.log

# 모든 요청 메시지
Select-String "OCPP-CALL" ocpp_protocol_debug.log

# 모든 응답 메시지
Select-String "OCPP-CALLRESULT" ocpp_protocol_debug.log

# 오류 메시지만
Select-String "ERROR|CALLERROR" ocpp_protocol_debug.log

# 특정 충전기만
Select-String "charger_001" ocpp_protocol_debug.log
```

### 특정 메시지 유형만 보기 (Linux/Mac)

```bash
# BootNotification만
grep "BootNotification" ocpp_protocol_debug.log

# TransactionEvent만
grep "TransactionEvent" ocpp_protocol_debug.log

# 모든 요청 메시지
grep "OCPP-CALL" ocpp_protocol_debug.log

# 모든 응답 메시지
grep "OCPP-CALLRESULT" ocpp_protocol_debug.log

# 오류 메시지만
grep -E "ERROR|CALLERROR" ocpp_protocol_debug.log

# 특정 충전기만
grep "charger_001" ocpp_protocol_debug.log
```

## 고급 사용법

### 로그 파일 크기 제한

로그 파일이 너무 커지는 것을 방지하려면, 여러 파일로 분할할 수 있습니다:

```python
from logging_config import setup_logging
from logging.handlers import RotatingFileHandler
import logging

# RotatingFileHandler로 자동 분할
logging.basicConfig(
    handlers=[
        RotatingFileHandler(
            'ocpp.log',
            maxBytes=10485760,  # 10MB
            backupCount=5       # 최대 5개 파일
        )
    ],
    level=logging.DEBUG
)
```

### 콘솔과 파일 동시 로깅

```python
from logging_config import setup_logging

# 콘솔에 출력하고 파일에도 저장
setup_logging(
    level='INFO',
    enable_protocol_debug=True,
    log_file='ocpp_complete.log'  # 파일에 저장
)
# 콘솔에는 INFO 레벨 이상만 출력
# 파일에는 모든 로그 저장
```

### 실시간 로그 모니터링

```bash
# Windows PowerShell (실시간 모니터링)
Get-Content ocpp_protocol_debug.log -Wait

# Linux/Mac (실시간 모니터링)
tail -f ocpp_protocol_debug.log
```

## 성능 고려사항

### 프로토콜 디버그 활성화 시

- **CPU**: 약 5-10% 증가
- **메모리**: 약 10-20MB 추가 (로그 버퍼)
- **디스크**: 메시지당 약 500-2000 바이트 (메시지 크기에 따라)

### 권장 설정

- **개발/테스트**: `DEBUG` 레벨, 파일 저장 활성화
- **운영 환경**: `INFO` 레벨, 문제 발생 시에만 디버그 활성화
- **성능 최적화**: 프로토콜 디버그 비활성화 (`OCPP_PROTOCOL_DEBUG=false`)

## 문제 해결

### Q: 로그가 저장되지 않음
A: 파일 경로가 올바른지, 쓰기 권한이 있는지 확인하세요.

```python
import os
os.chmod('ocpp.log', 0o666)  # 권한 설정
```

### Q: 로그 파일이 너무 큼
A: 로그 레벨을 `WARNING`으로 낮추거나, 로그 파일 분할을 설정하세요.

### Q: 프로토콜 메시지가 보이지 않음
A: `OCPP_PROTOCOL_DEBUG` 환경변수가 `'true'`로 설정되어 있는지 확인하세요.

```powershell
$env:OCPP_PROTOCOL_DEBUG
# 출력이 'true'여야 함
```

## 참고

- 모든 로그는 UTF-8로 인코딩됩니다 (한글 지원)
- 타임스탬프는 현지 시간대를 따릅니다
- JSON 페이로드는 자동으로 정렬되어 보기 좋게 포맷됩니다
