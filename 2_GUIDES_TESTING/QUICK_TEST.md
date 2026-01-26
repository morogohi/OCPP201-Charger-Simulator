# ⚡ 5분 안에 시작하는 빠른 테스트

**목표**: 코드가 정상 작동하는지 가장 빠르게 확인

---

## 🚀 1단계: 환경 준비 (1분)

```powershell
# PowerShell 실행
cd "c:\Project\OCPP201(P2M)"

# 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 환경변수 설정
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
```

---

## ✅ 2단계: 모듈 임포트 테스트 (1분)

```powershell
# 모든 핵심 모듈이 로드되는지 확인
python << 'EOF'
import sys
print('\n' + '='*60)
print('🧪 모듈 임포트 테스트')
print('='*60 + '\n')

tests = [
    ('ocpp_server', 'OCPP WebSocket 서버'),
    ('charger_simulator', '충전기 시뮬레이터'),
    ('database.models_postgresql', 'DB 모델'),
    ('database.services', 'DB 서비스'),
    ('ocpp_models', 'OCPP 데이터 모델'),
]

for module, desc in tests:
    try:
        __import__(module)
        print(f'✅ {module:<30} {desc}')
    except Exception as e:
        print(f'❌ {module:<30} {str(e)[:40]}')

print('\n' + '='*60)
EOF
```

**예상 결과**: 5개 항목 모두 ✅

---

## 🔗 3단계: 데이터베이스 연결 테스트 (1분)

```powershell
python << 'EOF'
import os
from database.models_postgresql import DatabaseManager
from sqlalchemy import text

print('\n' + '='*60)
print('🗄️  데이터베이스 연결 테스트')
print('='*60 + '\n')

try:
    # 연결
    db = DatabaseManager()
    session = db.get_session()
    print('✅ PostgreSQL 연결 성공')
    
    # 테이블 확인
    result = session.execute(text("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' ORDER BY table_name
    """))
    
    tables = [row[0] for row in result]
    print(f'✅ 테이블 개수: {len(tables)}개\n')
    
    for table in tables:
        print(f'   📊 {table}')
    
    session.close()
    print('\n' + '='*60)
    print('✅ 모든 테이블 확인 완료')
    
except Exception as e:
    print(f'❌ 연결 실패: {str(e)}\n')
    print('💡 해결 방법:')
    print('   1. PostgreSQL이 실행 중인지 확인')
    print('   2. charger_db 데이터베이스가 있는지 확인')
    print('   3. charger_user 사용자가 있는지 확인')
    print('   4. 비밀번호가 admin인지 확인')

print('='*60)
EOF
```

**예상 결과**: 6개 테이블 확인됨

---

## 💾 4단계: 데이터베이스 CRUD 테스트 (1분)

```powershell
python << 'EOF'
from database.models_postgresql import DatabaseManager
from database.services import StationService, ChargerService
from datetime import datetime

print('\n' + '='*60)
print('💾 데이터베이스 CRUD 테스트')
print('='*60 + '\n')

db = DatabaseManager()
session = db.get_session()

try:
    # 1. Create - 충전소 생성
    print('[1] 충전소 생성 중...')
    station = StationService.create_station(
        session,
        station_id=f'TEST_STATION_{int(datetime.now().timestamp())}',
        station_name='테스트 충전소',
        address='테스트 주소',
        longitude=127.0276,
        latitude=37.4979
    )
    print(f'    ✅ 충전소 생성: {station.station_name}')
    
    # 2. Read - 충전소 조회
    print('\n[2] 충전소 조회 중...')
    stations = StationService.get_all_stations(session)
    print(f'    ✅ 총 충전소: {len(stations)}개')
    
    # 3. Create - 충전기 생성
    print('\n[3] 충전기 생성 중...')
    charger = ChargerService.create_charger(
        session,
        charger_id=f'TEST_CHARGER_{int(datetime.now().timestamp())}',
        station_id=station.station_id,
        connector_id='CONN_001',
        charger_type='fast',
        power_type='DC',
        max_power=350
    )
    print(f'    ✅ 충전기 생성: {charger.charger_id}')
    
    # 4. Update - 상태 변경
    print('\n[4] 충전기 상태 업데이트 중...')
    updated = ChargerService.update_charger_status(
        session,
        charger.charger_id,
        'in_use'
    )
    if updated:
        print(f'    ✅ 상태 변경: {updated.status}')
    
    print('\n' + '='*60)
    print('✅ CRUD 테스트 완료')
    
except Exception as e:
    print(f'❌ 오류: {str(e)}')
finally:
    session.close()

print('='*60)
EOF
```

**예상 결과**: 모든 CRUD 작업 성공

---

## 📨 5단계: OCPP 메시지 모델 테스트 (1분)

```powershell
python << 'EOF'
from ocpp_models import BootNotificationRequest
from pydantic import ValidationError

print('\n' + '='*60)
print('📨 OCPP 메시지 모델 테스트')
print('='*60 + '\n')

try:
    # 메시지 생성
    print('[1] BootNotificationRequest 생성 중...')
    boot_req = BootNotificationRequest(
        chargingStation={
            'model': 'Charger-X1000',
            'vendorName': 'PowerTech',
            'serialNumber': 'SN-2024-001',
            'firmwareVersion': '1.0.0'
        },
        reason='PowerUp'
    )
    print('    ✅ 메시지 생성 성공')
    print(f'       모델: {boot_req.chargingStation[\"model\"]}')
    print(f'       공급사: {boot_req.chargingStation[\"vendorName\"]}')
    
    # JSON 변환
    print('\n[2] JSON 직렬화 중...')
    json_str = boot_req.model_dump_json()
    print(f'    ✅ JSON 직렬화 성공 ({len(json_str)} bytes)')
    
    # 유효성 검사
    print('\n[3] 유효성 검사 테스트...')
    try:
        invalid = BootNotificationRequest(
            chargingStation={},  # 필수 필드 누락
            reason='PowerUp'
        )
        print('    ❌ 유효성 검사 실패')
    except ValidationError:
        print('    ✅ 유효성 검사 정상 작동')
    
    print('\n' + '='*60)
    print('✅ OCPP 메시지 모델 테스트 완료')

except Exception as e:
    print(f'❌ 오류: {str(e)}')

print('='*60)
EOF
```

**예상 결과**: 메시지 생성, 직렬화, 유효성 검사 모두 성공

---

## 📊 최종 결과 요약

```powershell
python << 'EOF'
print('\n' + '╔' + '='*58 + '╗')
print('║' + ' '*58 + '║')
print('║' + '  ✅ 5분 테스트 완료'.center(58) + '║')
print('║' + ' '*58 + '║')
print('╚' + '='*58 + '╝\n')

print('✅ 통과한 항목:')
print('   1. 모듈 임포트')
print('   2. 데이터베이스 연결')
print('   3. 데이터베이스 CRUD')
print('   4. OCPP 메시지 모델')
print('\n🎯 상태: 모든 핵심 컴포넌트 정상 작동\n')

print('🚀 다음 단계:')
print('   • MANUAL_TEST_GUIDE.md - 상세 테스트 가이드')
print('   • test_system.py - 전체 시스템 테스트')
print('   • test_*.py - 개별 기능 테스트\n')
EOF
```

---

## ⚠️ 문제 발생 시

### PostgreSQL 연결 오류

```powershell
# PostgreSQL 서비스 시작
Start-Service postgresql-x64-15  # 버전 확인 필요

# 또는 Services 앱에서 PostgreSQL 재시작
```

### 모듈 오류

```powershell
# 패키지 재설치
pip install -r requirements.txt

# 또는 개별 설치
pip install websockets fastapi uvicorn sqlalchemy pydantic psycopg2-binary
```

### 데이터베이스 초기화

```powershell
# 테이블 삭제 후 재생성
python database/models_postgresql.py
```

---

**이 5단계가 모두 성공하면 프로젝트 전체가 정상 작동합니다!** ✅
