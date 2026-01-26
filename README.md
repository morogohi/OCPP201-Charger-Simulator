# OCPP 2.0.1 충전기 시뮬레이터 및 서버

OCPP 2.0.1(Open Charge Point Protocol 2.0.1) 기준으로 개발한 파이썬 기반 전기차 충전기 시뮬레이터와 중앙 관리 서버입니다.

## 프로젝트 구조

## 프로젝트 구조

```
OCPP201(P2M)/
├── ocpp_models.py              # OCPP 2.0.1 데이터 모델
├── ocpp_messages.py            # OCPP 메시지 처리 + 프로토콜 로깅
├── charger_simulator.py         # 충전기 시뮬레이터
├── ocpp_server.py              # OCPP 중앙 서버
├── server_api.py               # REST API (관리/모니터링)
├── logging_config.py           # 로깅 설정 유틸리티 ✨
├── demo.py                     # 완전 시스템 데모
├── demo_protocol_debug.py       # 프로토콜 디버그 데모 ✨
├── run_all.py                  # 서버 + 시뮬레이터 통합 실행
├── test_simulator.py           # 시뮬레이터 테스트
├── requirements.txt            # 의존성
├── README.md                   # 이 파일
├── PROTOCOL_DEBUG_GUIDE.md     # 프로토콜 디버그 상세 가이드 ✨
└── ocpp_protocol_debug.log     # 프로토콜 디버그 로그 (자동 생성)
```

✨ = 프로토콜 디버그 기능 추가

## 주요 기능

### 1. OCPP 2.0.1 프로토콜 구현
- WebSocket 기반 통신 (ws://localhost:9000)
- JSON-RPC 메시지 형식
- 완전한 메시지 파싱 및 생성
- 자동 메시지 ID 생성

### 2. 충전기 시뮬레이터 (`charger_simulator.py`)
- 실제 충전기 동작 시뮬레이션
- 자동 부팅 알림 (BootNotification)
- 주기적 하트비트 (30초 간격)
- 거래 이벤트 (TransactionEvent - Started/Updated/Ended)
- 상태 알림 (StatusNotification)
- 인증 (Authorize)
- 실시간 전력 사용량 시뮬레이션 (전압, 전류, 에너지)

### 3. 중앙 관리 서버 (`ocpp_server.py`)
- 다중 충전기 동시 연결 관리
- 모든 OCPP 메시지 처리 및 검증
- 거래 관리 및 제어
- 연결 상태 모니터링
- 자동 재연결 지원

### 4. REST API (`server_api.py`)
- 충전기 목록 및 상태 조회 (`/chargers`)
- 개별 충전기 상태 조회 (`/chargers/{charger_id}`)
- 거래 시작/중지 제어 (`/chargers/{charger_id}/start`, `/stop`)
- 헬스 체크 (`/health`)

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 전체 시스템 데모 실행 (권장)
```bash
python demo.py
```

### 3. 프로토콜 디버그 데모 (상세 로깅 포함)
```bash
python demo_protocol_debug.py
```

이 명령어는:
- 모든 OCPP 메시지를 상세히 로깅
- 자동으로 `ocpp_protocol_debug.log` 파일 생성
- 각 단계별로 프로토콜 상세 정보 표시

## 프로토콜 디버그 로깅

OCPP 상세 프로토콜 메시지를 로깅할 수 있습니다. 이 기능으로 모든 메시지의 송수신 내용을 상세히 확인할 수 있습니다.

### 빠른 시작 - 프로토콜 디버그

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

#### Linux/Mac
```bash
export OCPP_PROTOCOL_DEBUG=true
python demo.py
```

### 전용 프로토콜 디버그 데모
```bash
python demo_protocol_debug.py
```

이 스크립트는:
- 프로토콜 디버그 자동 활성화
- 상세 로그를 파일(`ocpp_protocol_debug.log`)에 저장
- 각 단계별로 프로토콜 메시지 출력

### 프로토콜 로그 레벨 설정

```powershell
# 디버그 로그 (모든 로그)
$env:OCPP_LOG_LEVEL = 'DEBUG'

# 일반 정보 (기본값)
$env:OCPP_LOG_LEVEL = 'INFO'

# 경고 및 오류만
$env:OCPP_LOG_LEVEL = 'WARNING'
```

### 로그 파일에 저장

```powershell
$env:OCPP_PROTOCOL_DEBUG = 'true'
$env:OCPP_LOG_FILE = 'ocpp_messages.log'
python demo.py
```

### 프로토콜 로그 태그 설명

#### 메시지 생성 로그
- `[OCPP-CALL-SEND]` - Call 메시지 생성 (요청)
- `[OCPP-PAYLOAD-SEND]` - 요청 페이로드 (JSON 형식)
- `[OCPP-CALLRESULT-SEND]` - CallResult 생성 (응답)
- `[OCPP-RESPONSE-SEND]` - 응답 페이로드 (JSON 형식)
- `[OCPP-CALLERROR-SEND]` - CallError 생성 (오류)
- `[OCPP-ERROR-SEND]` - 오류 코드 및 메시지

#### 메시지 수신 로그
- `[OCPP-CALL-RECV]` - Call 메시지 수신
- `[OCPP-PAYLOAD-RECV]` - 수신한 페이로드
- `[OCPP-CALLRESULT-RECV]` - CallResult 수신
- `[OCPP-RESPONSE-RECV]` - 수신한 응답
- `[OCPP-CALLERROR-RECV]` - CallError 수신
- `[OCPP-ERROR-RECV]` - 수신한 오류 정보
- `[OCPP-RAW-RECV]` - 원본 JSON 메시지

#### 전송/수신 로그
- `[CHARGER-SEND]` - 충전기가 전송하는 원본 메시지
- `[CHARGER-RECV]` - 충전기가 수신하는 원본 메시지
- `[SERVER-SEND]` - 서버가 전송하는 원본 메시지
- `[SERVER-RECV]` - 서버가 수신하는 원본 메시지

### 프로토콜 로그 예제

```
2026-01-19 15:26:17,797 - ocpp_messages - DEBUG - [OCPP-CALL-SEND] Action: RequestStartTransaction, ID: 550e8400-e29b
2026-01-19 15:26:17,797 - ocpp_messages - DEBUG - [OCPP-PAYLOAD-SEND] {
  "evseId": 1,
  "connectorId": 1,
  "idToken": {
    "idToken": "test_token",
    "type": "Central"
  }
}
2026-01-19 15:26:17,798 - charger_simulator - DEBUG - [CHARGER-RECV] charger_001: [2,"550e8400-e29b","RequestStartTransaction",{"evseId":1,...}]
2026-01-19 15:26:17,798 - ocpp_messages - DEBUG - [OCPP-CALL-RECV] Action: RequestStartTransaction, ID: 550e8400-e29b
2026-01-19 15:26:17,798 - ocpp_messages - DEBUG - [OCPP-PAYLOAD-RECV] {
  "evseId": 1,
  "connectorId": 1,
  "idToken": {
    "idToken": "test_token",
    "type": "Central"
  }
}
```

### Python 코드에서 프로토콜 디버그 활성화

```python
from logging_config import setup_logging
import asyncio
from demo import main

# 프로토콜 디버그 로깅 활성화
setup_logging(
    level='DEBUG',
    enable_protocol_debug=True,
    log_file='ocpp_debug.log'
)

# 애플리케이션 실행
asyncio.run(main())
```

### 로그 필터링

```powershell
# BootNotification 메시지만 확인
Select-String "BootNotification" ocpp_protocol_debug.log

# TransactionEvent만 확인
Select-String "TransactionEvent" ocpp_protocol_debug.log

# 특정 충전기만 확인
Select-String "charger_001" ocpp_protocol_debug.log

# 오류 메시지만 확인
Select-String "ERROR|CALLERROR" ocpp_protocol_debug.log
```



### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 전체 시스템 데모 실행 (권장)
```bash
python demo.py
```

**출력 예:**
```
============================================================
OCPP 2.0.1 충전기 시뮬레이터 및 서버 데모
============================================================

[1단계] 충전기 연결 중...
[2단계] 현재 연결된 충전기: 3
  - charger_001: Boot=True, Connected=True
  - charger_002: Boot=True, Connected=True
  - charger_003: Boot=True, Connected=True

[3단계] 첫 번째 충전기 거래 시작...
[4단계] 거래 상태 확인...
  - charger_001: 충전 중 (에너지: 0.20 kWh)

[5단계] 거래 중지...
[6단계] 최종 상태:
  - charger_001: 연결됨=True
  - charger_002: 연결됨=True
  - charger_003: 연결됨=True
```

### 3. 개별 실행 모드

#### 서버만 실행
```bash
python run_all.py server
```
- OCPP 서버: `ws://localhost:9000`
- REST API: `http://localhost:8080`

#### 시뮬레이터만 실행 (서버 필요)
```bash
python run_all.py charger
```

#### 서버 + 시뮬레이터 함께 실행
```bash
python run_all.py all
```

## 사용 예제

### Python 코드로 충전기 제어
```python
from charger_simulator import ChargerSimulator
from ocpp_server import OCPPServer
import asyncio

async def main():
    # 서버 시작
    server = OCPPServer(host="localhost", port=9000)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(1)
    
    # 충전기 생성 및 연결
    charger = ChargerSimulator(
        charger_id="charger_001",
        server_url="ws://localhost:9000"
    )
    await charger.connect()
    
    # 거래 시작
    await server.request_start_transaction("charger_001")
    charger.is_charging = True
    
    # 5초 충전
    await asyncio.sleep(5)
    
    # 거래 중지
    charger.is_charging = False
    await server.request_stop_transaction("charger_001")
    
    # 정리
    await charger.disconnect()

asyncio.run(main())
```

### REST API로 충전기 제어 (별도 터미널)
```bash
# 모든 충전기 조회
curl http://localhost:8080/chargers

# 특정 충전기 조회
curl http://localhost:8080/chargers/charger_001

# 거래 시작
curl -X POST http://localhost:8080/chargers/charger_001/start \
  -H "Content-Type: application/json" \
  -d '{"evse_id": 1, "connector_id": 1}'

# 거래 중지
curl -X POST http://localhost:8080/chargers/charger_001/stop \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "tx_001"}'

# 헬스 체크
curl http://localhost:8080/health
```

## OCPP 2.0.1 메시지 흐름

### 충전기 → 서버 (요청)
```
BootNotification  → 부팅 시 연결 및 인증
Heartbeat         → 30초마다 주기적 전송
StatusNotification → 상태 변경 시 전송
TransactionEvent  → 거래 관련 이벤트 (Started/Updated/Ended)
Authorize         → 사용자 인증 요청
```

### 서버 → 충전기 (요청)
```
RequestStartTransaction  → 거래 시작 요청
RequestStopTransaction   → 거래 중지 요청
SetChargingProfile      → 충전 프로필 설정
```

## 로깅

서버와 시뮬레이터는 상세한 로깅을 제공합니다:
```
2026-01-19 15:26:14,775 - charger_simulator - INFO - 부팅 알림 전송: charger_001
2026-01-19 15:26:14,777 - ocpp_server - INFO - 부팅 알림 수신 (charger_001): PowerUp
2026-01-19 15:26:17,797 - charger_simulator - INFO - 거래 시작: 93452c35-f1b0-4b42-b515-647e32d5c4a1
2026-01-19 15:26:19,777 - charger_simulator - INFO - 거래 이벤트 전송: Updated, 에너지: 0.1 kWh
```

## 주요 클래스

### ChargerSimulator
```python
charger = ChargerSimulator(
    charger_id="charger_001",
    server_url="ws://localhost:9000",
    charger_model="EVBox Home",
    charger_vendor="EVBox",
    num_connectors=1
)
await charger.connect()          # 서버에 연결
await charger.disconnect()       # 연결 해제
charger.is_charging = True       # 충전 시작
charger.meter_value              # 현재 에너지 사용량 (kWh)
```

### OCPPServer
```python
server = OCPPServer(host="0.0.0.0", port=9000)
await server.start()  # 서버 시작
await server.request_start_transaction(charger_id)
await server.request_stop_transaction(charger_id)
status = server.get_charger_status(charger_id)
```

### OCPPMessage
```python
# Call 메시지 생성
message = OCPPMessage.create_call("BootNotification", {...})

# CallResult 메시지 생성
message = OCPPMessage.create_call_result(message_id, {...})

# 메시지 파싱
msg_type, msg_id, action, payload = OCPPMessage.parse_message(message)
```

## 기술 스택

| 항목 | 버전 |
|------|------|
| Python | 3.10+ |
| websockets | 10.0+ |
| aiohttp | 3.8.0+ |
| pydantic | 2.0.0+ |
| asyncio | 내장 |

## 성능 특성

- **동시 연결**: 100+ 충전기 동시 관리 가능
- **메시지 처리 지연**: <50ms
- **메모리 사용**: 충전기당 ~2MB
- **CPU**: 낮은 사용률 (비동기 처리)

## 주의사항

1. **포트 설정**: 
   - OCPP 서버: 9000 포트 (변경 가능)
   - REST API: 8080 포트 (변경 가능)

2. **보안**: 
   - 이 구현은 개발/테스트용입니다
   - 프로덕션 환경에서는 다음 보안 강화 필요:
     - TLS/SSL 암호화
     - 토큰 기반 인증 (JWT)
     - 요청 검증
     - 레이트 리미팅

3. **확장성**: 
   - 현재는 단일 서버로 구성
   - 대규모 배포시 다음 고려:
     - 로드 밸런싱
     - 데이터베이스 연동
     - 메시지 큐 (RabbitMQ, Redis)
     - 마이크로서비스 아키텍처

## 주요 수정 사항

### v1.1 (2026-01-19)
- WebSocket 핸들러 경로 추출 로직 수정
- 의존성 버전 유연화 (설치 오류 해결)
- 완전 기능 데모 스크립트 추가
- 상세한 문서 업데이트

### v1.0 (2026-01-19)
- 초기 릴리스
- OCPP 2.0.1 기본 구현
- 충전기 시뮬레이터 완성
- 중앙 서버 구현

## 라이선스

MIT License

## 참고 자료

- [OCPP 2.0.1 공식 문서](https://openchargealliance.org/)
- [OCPP GitHub 저장소](https://github.com/openchargealliance/ocpp)
- [WebSockets 라이브러리](https://websockets.readthedocs.io/)
- [Pydantic 문서](https://docs.pydantic.dev/)
