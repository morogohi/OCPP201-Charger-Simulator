# 🧪 OCPP 2.0.1 (P2M) - 수작업 테스트 가이드

**작성일**: 2026년 1월 26일  
**환경**: Windows PowerShell + Python 3.13.5 venv

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [환경 설정](#환경-설정)
3. [단계별 테스트](#단계별-테스트)
4. [실제 실행 시나리오](#실제-실행-시나리오)
5. [문제 해결](#문제-해결)

---

## 사전 준비

### 필수 설치 항목

```bash
# 1. PostgreSQL 설치 (이미 설치되어 있으면 스킵)
# Windows: https://www.postgresql.org/download/windows/
# 설정: 
#   - 포트: 5432
#   - 사용자: charger_user
#   - 비밀번호: admin
#   - 데이터베이스: charger_db

# 2. Python 가상환경 확인 (이미 구성됨)
```

### 요구사항 확인

```powershell
# PowerShell에서 실행
cd "c:\Project\OCPP201(P2M)"

# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 필수 패키지 확인
pip list | grep -E "websockets|fastapi|sqlalchemy|psycopg2"
```

---

## 환경 설정

### 1단계: 가상환경 활성화

```powershell
# PowerShell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1

# 프롬프트가 다음과 같이 변경됨:
# (.venv) PS c:\Project\OCPP201(P2M)>
```

### 2단계: 환경 변수 설정

```powershell
# PostgreSQL 데이터베이스 연결 설정
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 확인
echo $env:DATABASE_URL
```

### 3단계: 데이터베이스 준비

```powershell
# 데이터베이스 초기화 (PostgreSQL 실행 필수)
python database/models_postgresql.py

# 또는 수동으로:
python -c "
from database.models_postgresql import DatabaseManager, Base
db = DatabaseManager()
db.initialize()
print('✅ 데이터베이스 초기화 완료')
"
```

---

## 단계별 테스트

### [Test 1] 모듈 임포트 테스트

**목적**: 모든 핵심 모듈이 정상 작동하는지 확인

```powershell
python -c "
print('='*70)
print('Test 1: 모듈 임포트 테스트')
print('='*70)

import sys
sys.path.insert(0, '.')

# 1. 기본 모듈
print('[1] 기본 모듈 임포트...')
try:
    from ocpp_server import OCPPServer
    print('  ✅ OCPP 서버 임포트 성공')
except Exception as e:
    print(f'  ❌ OCPP 서버: {e}')

try:
    from charger_simulator import ChargerSimulator
    print('  ✅ 충전기 시뮬레이터 임포트 성공')
except Exception as e:
    print(f'  ❌ 충전기 시뮬레이터: {e}')

# 2. 데이터베이스 모듈
print()
print('[2] 데이터베이스 모듈 임포트...')
try:
    from database.models_postgresql import DatabaseManager
    print('  ✅ DatabaseManager 임포트 성공')
except Exception as e:
    print(f'  ❌ DatabaseManager: {e}')

try:
    from database.services import StationService, ChargerService
    print('  ✅ 서비스 모듈 임포트 성공')
except Exception as e:
    print(f'  ❌ 서비스 모듈: {e}')

# 3. OCPP 모델
print()
print('[3] OCPP 데이터 모델 임포트...')
try:
    from ocpp_models import BootNotificationRequest
    print('  ✅ OCPP 메시지 모델 임포트 성공')
except Exception as e:
    print(f'  ❌ OCPP 모델: {e}')

print()
print('='*70)
print('✅ Test 1 완료')
print('='*70)
"
```

**예상 결과**:
```
✅ OCPP 서버 임포트 성공
✅ 충전기 시뮬레이터 임포트 성공
✅ DatabaseManager 임포트 성공
✅ 서비스 모듈 임포트 성공
✅ OCPP 메시지 모델 임포트 성공
```

---

### [Test 2] 데이터베이스 연결 테스트

**목적**: PostgreSQL 데이터베이스 연결 및 테이블 확인

```powershell
python -c "
print('='*70)
print('Test 2: 데이터베이스 연결 테스트')
print('='*70)
print()

from database.models_postgresql import DatabaseManager
import os

# 1. 환경변수 확인
print('[1] 환경 설정 확인')
db_url = os.getenv('DATABASE_URL', '미설정')
print(f'  DATABASE_URL: {db_url}')
print()

# 2. 데이터베이스 연결
print('[2] 데이터베이스 연결 시도...')
try:
    db = DatabaseManager()
    session = db.get_session()
    print('  ✅ 데이터베이스 연결 성공')
    
    # 3. 테이블 목록 조회
    from sqlalchemy import text
    print()
    print('[3] 테이블 확인:')
    result = session.execute(text('''
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' ORDER BY table_name
    '''))
    
    tables = [row[0] for row in result]
    print(f'  생성된 테이블: {len(tables)}개')
    for table in tables:
        print(f'    - {table}')
    
    session.close()
    
except Exception as e:
    print(f'  ❌ 연결 실패: {e}')
    print()
    print('  💡 해결 방법:')
    print('     1. PostgreSQL이 실행 중인지 확인하세요')
    print('     2. 데이터베이스 charger_db가 생성되어 있는지 확인하세요')
    print('     3. 사용자 charger_user와 비밀번호가 맞는지 확인하세요')

print()
print('='*70)
print('✅ Test 2 완료')
print('='*70)
"
```

**예상 결과**:
```
✅ 데이터베이스 연결 성공
생성된 테이블: 6개
  - station_info
  - charger_info
  - power_consumption
  - charger_usage_log
  - daily_charger_stats
  - hourly_charger_stats
```

---

### [Test 3] 데이터 모델 테스트

**목적**: OCPP 메시지 모델 생성 및 검증

```powershell
python -c "
print('='*70)
print('Test 3: OCPP 메시지 모델 테스트')
print('='*70)
print()

from ocpp_models import BootNotificationRequest, HeartbeatRequest
from pydantic import ValidationError

# 1. BootNotification 생성
print('[1] BootNotificationRequest 생성')
try:
    boot_req = BootNotificationRequest(
        chargingStation={
            'model': 'Tesla Model 3',
            'vendorName': 'Tesla Inc',
            'serialNumber': 'SN-2024-001',
            'firmwareVersion': '1.0.0'
        },
        reason='PowerUp'
    )
    print(f'  ✅ 메시지 생성 성공')
    print(f'     - Model: {boot_req.chargingStation[\"model\"]}')
    print(f'     - Vendor: {boot_req.chargingStation[\"vendorName\"]}')
    print(f'     - Reason: {boot_req.reason}')
except ValidationError as e:
    print(f'  ❌ 검증 오류: {e}')
except Exception as e:
    print(f'  ❌ 생성 실패: {e}')

# 2. 데이터 유효성 검사
print()
print('[2] 데이터 유효성 검사')
try:
    # 필수 필드 누락 시도
    invalid_req = BootNotificationRequest(
        chargingStation={},  # 필수 필드 누락
        reason='PowerUp'
    )
    print('  ❌ 유효성 검사 실패 (오류가 발생해야 함)')
except ValidationError as e:
    print('  ✅ 유효성 검사 동작 확인됨')
    print(f'     오류: 필수 필드가 누락되었습니다')
except Exception as e:
    print(f'  ⚠️  예상치 못한 오류: {e}')

# 3. JSON 직렬화
print()
print('[3] JSON 직렬화')
try:
    boot_req = BootNotificationRequest(
        chargingStation={
            'model': 'ChargerX',
            'vendorName': 'PowerCorp'
        },
        reason='PowerUp'
    )
    json_data = boot_req.model_dump_json(indent=2)
    print('  ✅ JSON 직렬화 성공')
    print(f'     크기: {len(json_data)} bytes')
except Exception as e:
    print(f'  ❌ 직렬화 실패: {e}')

print()
print('='*70)
print('✅ Test 3 완료')
print('='*70)
"
```

**예상 결과**:
```
✅ 메시지 생성 성공
  - Model: Tesla Model 3
  - Vendor: Tesla Inc
  - Reason: PowerUp

✅ 유효성 검사 동작 확인됨
  오류: 필수 필드가 누락되었습니다

✅ JSON 직렬화 성공
  크기: 175 bytes
```

---

### [Test 4] 데이터베이스 서비스 테스트

**목적**: 충전소/충전기 데이터 CRUD 작업 테스트

```powershell
python -c "
print('='*70)
print('Test 4: 데이터베이스 서비스 테스트')
print('='*70)
print()

from database.models_postgresql import DatabaseManager
from database.services import StationService, ChargerService
from datetime import datetime

db = DatabaseManager()

# 1. 충전소 생성
print('[1] 충전소 생성 (CREATE)')
try:
    session = db.get_session()
    station = StationService.create_station(
        session,
        station_id='STATION_001',
        station_name='테스트 충전소 A',
        address='서울시 강남구',
        longitude=127.0276,
        latitude=37.4979,
        operator_name='테스트 운영사',
        operator_phone='010-1234-5678',
        operator_email='test@example.com'
    )
    print(f'  ✅ 충전소 생성 성공')
    print(f'     ID: {station.station_id}')
    print(f'     이름: {station.station_name}')
    session.close()
except Exception as e:
    print(f'  ⚠️  오류: {e}')

# 2. 충전소 조회
print()
print('[2] 충전소 조회 (READ)')
try:
    session = db.get_session()
    stations = StationService.get_all_stations(session)
    print(f'  ✅ 충전소 조회 성공')
    print(f'     총 충전소: {len(stations)}개')
    for station in stations[:3]:
        print(f'       - {station.station_name} ({station.location})')
    session.close()
except Exception as e:
    print(f'  ⚠️  오류: {e}')

# 3. 충전기 생성
print()
print('[3] 충전기 생성 (CREATE)')
try:
    session = db.get_session()
    charger = ChargerService.create_charger(
        session,
        charger_id='CHARGER_001',
        station_id='STATION_001',
        connector_id='CONN_001',
        charger_type='fast',
        power_type='AC',
        max_power=350,
        model='ChargerX 350',
        serial_number='SN-2024-001'
    )
    print(f'  ✅ 충전기 생성 성공')
    print(f'     ID: {charger.charger_id}')
    print(f'     타입: {charger.charger_type}')
    print(f'     최대 전력: {charger.max_power} kW')
    session.close()
except Exception as e:
    print(f'  ⚠️  오류: {e}')

# 4. 충전기 상태 업데이트
print()
print('[4] 충전기 상태 업데이트 (UPDATE)')
try:
    session = db.get_session()
    charger = ChargerService.update_charger_status(
        session,
        'CHARGER_001',
        'in_use'
    )
    if charger:
        print(f'  ✅ 상태 업데이트 성공')
        print(f'     현재 상태: {charger.status}')
    session.close()
except Exception as e:
    print(f'  ⚠️  오류: {e}')

print()
print('='*70)
print('✅ Test 4 완료')
print('='*70)
"
```

**예상 결과**:
```
✅ 충전소 생성 성공
  ID: STATION_001
  이름: 테스트 충전소 A

✅ 충전소 조회 성공
  총 충전소: 1개

✅ 충전기 생성 성공
  ID: CHARGER_001
  타입: fast
  최대 전력: 350 kW

✅ 상태 업데이트 성공
  현재 상태: in_use
```

---

### [Test 5] 시뮬레이터 인스턴스 생성 테스트

**목적**: 충전기 시뮬레이터 객체 생성 및 메서드 확인

```powershell
python -c "
print('='*70)
print('Test 5: 시뮬레이터 인스턴스 테스트')
print('='*70)
print()

from charger_simulator import ChargerSimulator
import inspect

# 1. 시뮬레이터 인스턴스 생성
print('[1] ChargerSimulator 인스턴스 생성')
try:
    sim = ChargerSimulator(
        charger_id='charger_001',
        server_url='ws://localhost:9000'
    )
    print(f'  ✅ 인스턴스 생성 성공')
    print(f'     Charger ID: {sim.charger_id}')
    print(f'     Server URL: {sim.server_url}')
except Exception as e:
    print(f'  ❌ 생성 실패: {e}')

# 2. 가용 메서드 확인
print()
print('[2] 가용 메서드 확인')
try:
    methods = [m for m in dir(sim) if not m.startswith('_')]
    print(f'  ✅ {len(methods)}개의 메서드/속성 발견:')
    
    important_methods = ['connect', 'boot', 'start_transaction', 
                        'send_meter_values', 'stop_transaction']
    for method_name in important_methods:
        if method_name in methods:
            method = getattr(sim, method_name)
            if callable(method):
                print(f'    ✓ {method_name}()')
            else:
                print(f'    ✓ {method_name} (속성)')
except Exception as e:
    print(f'  ❌ 오류: {e}')

# 3. 메서드 서명 확인
print()
print('[3] 주요 메서드 서명')
try:
    for method_name in ['connect', 'boot', 'start_transaction']:
        if hasattr(sim, method_name):
            method = getattr(sim, method_name)
            if callable(method):
                sig = inspect.signature(method)
                print(f'  {method_name}{sig}')
except Exception as e:
    print(f'  ❌ 오류: {e}')

print()
print('='*70)
print('✅ Test 5 완료')
print('='*70)
"
```

**예상 결과**:
```
✅ 인스턴스 생성 성공
  Charger ID: charger_001
  Server URL: ws://localhost:9000

✅ 13개의 메서드/속성 발견:
  ✓ connect()
  ✓ boot()
  ✓ start_transaction()
  ✓ send_meter_values()
  ✓ stop_transaction()
```

---

### [Test 6] API 엔드포인트 테스트 (선택사항)

**목적**: REST API 서버 엔드포인트 확인 (서버 실행 필요)

```powershell
# 터미널 1: API 서버 시작
python gis_dashboard_api.py

# 터미널 2: API 테스트
python -c "
import requests
import time

print('='*70)
print('Test 6: REST API 엔드포인트 테스트')
print('='*70)
print()

time.sleep(2)  # 서버 시작 대기

base_url = 'http://localhost:8000'

endpoints = [
    ('GET', '/'),
    ('GET', '/api/stations'),
    ('GET', '/api/chargers'),
    ('GET', '/api/statistics'),
]

print('[1] API 엔드포인트 확인')
for method, endpoint in endpoints:
    try:
        if method == 'GET':
            resp = requests.get(f'{base_url}{endpoint}', timeout=2)
        
        status = '✅' if resp.status_code == 200 else '⚠️'
        print(f'  {status} {method} {endpoint} ({resp.status_code})')
    except requests.exceptions.ConnectionError:
        print(f'  ❌ {method} {endpoint} (서버 미실행)')
    except Exception as e:
        print(f'  ⚠️  {method} {endpoint} ({str(e)[:30]})')

print()
print('='*70)
"
```

---

## 실제 실행 시나리오

### 시나리오 1: 완벽한 시스템 테스트 (30분)

```powershell
# 1. 환경 설정 (2분)
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 2. Test 1-3 실행 (5분)
python -c "... Test 1 코드 ..."
python -c "... Test 2 코드 ..."
python -c "... Test 3 코드 ..."

# 3. Test 4 실행 (5분)
python -c "... Test 4 코드 ..."

# 4. Test 5 실행 (3분)
python -c "... Test 5 코드 ..."

# 5. 전체 테스트 실행 (15분)
python test_system.py
```

### 시나리오 2: 빠른 검증 (10분)

```powershell
# 기본 모듈과 DB 연결만 테스트
.\.venv\Scripts\Activate.ps1
python -c "... Test 1 + Test 2 코드 ..."
```

---

## 문제 해결

### 문제 1: PostgreSQL 연결 안 됨

```
❌ psycopg2 오류 또는 연결 거부
```

**해결 방법**:
```powershell
# 1. PostgreSQL 서비스 상태 확인
Get-Service postgresql-x64-15  # 버전은 다를 수 있음

# 2. 서비스 시작 (중지된 경우)
Start-Service postgresql-x64-15

# 3. 데이터베이스 생성 확인 (psql 또는 pgAdmin)
psql -U postgres -d charger_db -c "SELECT 1"

# 4. 사용자 확인
psql -U postgres -c "SELECT * FROM pg_user WHERE usename='charger_user'"

# 5. 비밀번호 재설정 필요 시
psql -U postgres -c "ALTER USER charger_user WITH PASSWORD 'admin'"
```

### 문제 2: 모듈 임포트 오류

```
❌ ModuleNotFoundError: No module named 'XXX'
```

**해결 방법**:
```powershell
# 1. 가상환경 활성화 확인
.\.venv\Scripts\Activate.ps1

# 2. 패키지 재설치
pip install --upgrade -r requirements.txt

# 3. 경로 확인
python -c "import sys; print(sys.path)"
```

### 문제 3: 데이터베이스 초기화 실패

```
❌ SQLAlchemy 오류 또는 테이블 생성 실패
```

**해결 방법**:
```powershell
# 1. 기존 테이블 삭제
python -c "
from database.models_postgresql import Base, DatabaseManager
db = DatabaseManager()
Base.metadata.drop_all(db.engine)
print('✅ 기존 테이블 삭제 완료')
"

# 2. 테이블 재생성
python -c "
from database.models_postgresql import Base, DatabaseManager
db = DatabaseManager()
Base.metadata.create_all(db.engine)
print('✅ 테이블 생성 완료')
"
```

---

## 체크리스트

아래 항목들을 완료하면 수작업 테스트 완료입니다.

- [ ] Test 1: 모든 모듈 임포트 성공
- [ ] Test 2: 데이터베이스 연결 성공 및 테이블 6개 확인
- [ ] Test 3: OCPP 메시지 모델 생성 및 유효성 검사 성공
- [ ] Test 4: 데이터베이스 CRUD 작업 성공
- [ ] Test 5: 시뮬레이터 인스턴스 생성 및 메서드 확인
- [ ] (선택) Test 6: API 엔드포인트 응답 확인

---

## 추가 정보

### 로그 확인

```powershell
# 로그 파일 확인
Get-Content "ocpp_protocol_debug.log" -Tail 50

# 실시간 로그 모니터링
Get-Content "ocpp_protocol_debug.log" -Wait
```

### 데이터베이스 조회

```powershell
python -c "
from database.models_postgresql import DatabaseManager
from database.services import StationService

db = DatabaseManager()
session = db.get_session()

# 충전소 목록
stations = StationService.get_all_stations(session)
print(f'총 충전소: {len(stations)}')

# 마지막 기록 확인
from sqlalchemy import text
result = session.execute(text('SELECT * FROM station_info LIMIT 5'))
for row in result:
    print(row)

session.close()
"
```

---

**다음 단계**: 모든 테스트가 성공하면 `test_*.py` 파일들을 실행하여 
더욱 상세한 통합 테스트를 수행할 수 있습니다.
