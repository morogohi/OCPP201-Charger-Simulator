#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCPP 2.0.1 - 수작업 테스트 스크립트
이 스크립트는 CODE_TEST_REPORT.md의 모든 테스트를 자동으로 실행합니다.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Windows 환경에서 UTF-8 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 경로 설정
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '8_DATABASE'))
sys.path.insert(0, str(Path(__file__).parent.parent / '4_PYTHON_SOURCE'))

# 환경변수 설정
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'


def print_header(title):
    """헤더 출력"""
    width = 70
    print(f'\n{"╔" + "═"*68 + "╗"}')
    print(f'║ {title.center(66)} ║')
    print(f'{"╚" + "═"*68 + "╝"}\n')


def print_section(number, title):
    """섹션 헤더 출력"""
    print(f'\n[{number}] {title}')
    print('─' * 70)


def print_success(message, indent=0):
    """성공 메시지"""
    prefix = '  ' * indent
    print(f'{prefix}✅ {message}')


def print_error(message, indent=0):
    """오류 메시지"""
    prefix = '  ' * indent
    print(f'{prefix}❌ {message}')


def print_warning(message, indent=0):
    """경고 메시지"""
    prefix = '  ' * indent
    print(f'{prefix}⚠️  {message}')


def test_module_imports():
    """Test 1: 모듈 임포트 테스트"""
    print_section(1, '📦 모듈 임포트 테스트')
    
    modules = [
        ('ocpp_server', 'OCPP WebSocket 서버'),
        ('charger_simulator', '충전기 시뮬레이터'),
        ('database.models_postgresql', 'PostgreSQL ORM 모델'),
        ('database.services', 'DB 서비스 계층'),
        ('ocpp_models', 'Pydantic 데이터 모델'),
        ('ocpp_messages', 'OCPP 메시지 처리'),
        ('logging_config', '로깅 설정'),
    ]
    
    results = []
    for module_name, description in modules:
        try:
            __import__(module_name)
            print_success(f'{module_name:<30} {description}')
            results.append(True)
        except Exception as e:
            print_error(f'{module_name:<30} {str(e)[:40]}')
            results.append(False)
    
    return all(results)


def test_database_connection():
    """Test 2: 데이터베이스 연결 테스트"""
    print_section(2, '🗄️  데이터베이스 연결 테스트')
    
    try:
        from database.models_postgresql import DatabaseManager
        from sqlalchemy import text
        
        db = DatabaseManager()
        session = db.get_session()
        print_success('PostgreSQL 연결 성공')
        
        # 테이블 조회
        result = session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='public' ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        print_success(f'생성된 테이블: {len(tables)}개')
        
        for table in tables:
            print(f'    📊 {table}')
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f'데이터베이스 연결 실패: {str(e)}')
        print_warning('PostgreSQL이 실행 중인지 확인하세요', indent=1)
        return False


def test_ocpp_messages():
    """Test 3: OCPP 메시지 모델 테스트"""
    print_section(3, '📨 OCPP 메시지 모델 테스트')
    
    try:
        from ocpp_models import (
            BootNotificationRequest, HeartbeatRequest,
            TransactionEventRequest, StatusNotificationRequest
        )
        from pydantic import ValidationError
        
        # BootNotification 생성
        boot_req = BootNotificationRequest(
            chargingStation={
                'model': 'Test Charger',
                'vendorName': 'Test Vendor',
                'serialNumber': 'SN-2024-001',
                'firmwareVersion': '1.0.0'
            },
            reason='PowerUp'
        )
        print_success('BootNotificationRequest 생성 성공')
        print(f'    Model: {boot_req.chargingStation["model"]}')
        
        # 유효성 검사
        try:
            invalid = BootNotificationRequest(
                chargingStation={},
                reason='PowerUp'
            )
            print_error('유효성 검사 실패')
            return False
        except ValidationError:
            print_success('유효성 검사 정상 작동')
        
        # JSON 직렬화
        json_data = boot_req.model_dump_json()
        print_success(f'JSON 직렬화 성공 ({len(json_data)} bytes)')
        
        return True
        
    except Exception as e:
        print_error(f'메시지 모델 테스트 실패: {str(e)}')
        return False


def test_database_crud():
    """Test 4: 데이터베이스 CRUD 테스트"""
    print_section(4, '💾 데이터베이스 CRUD 테스트')
    
    try:
        from database.models_postgresql import DatabaseManager
        from database.services import StationService, ChargerService
        from datetime import datetime
        
        db = DatabaseManager()
        session = db.get_session()
        
        # Create - 충전소
        test_id = str(int(datetime.now().timestamp()))
        station = StationService.create_station(
            session,
            station_id=f'TEST_STATION_{test_id}',
            station_name='테스트 충전소',
            address='테스트 주소',
            longitude=127.0276,
            latitude=37.4979
        )
        print_success(f'충전소 생성: {station.station_name} ({station.station_id})')
        
        # Read - 충전소 조회
        stations = StationService.get_all_stations(session)
        print_success(f'충전소 조회: {len(stations)}개')
        
        # Create - 충전기
        charger = ChargerService.create_charger(
            session,
            charger_id=f'TEST_CHARGER_{test_id}',
            station_id=station.station_id,
            connector_id='CONN_001',
            charger_type='fast',
            power_type='DC',
            max_power=350
        )
        print_success(f'충전기 생성: {charger.charger_id}')
        
        # Update - 상태 변경
        updated = ChargerService.update_charger_status(
            session,
            charger.charger_id,
            'in_use'
        )
        if updated:
            print_success(f'상태 업데이트: {updated.status}')
        
        session.close()
        return True
        
    except Exception as e:
        print_error(f'CRUD 테스트 실패: {str(e)}')
        return False


def test_simulator():
    """Test 5: 충전기 시뮬레이터 테스트"""
    print_section(5, '🚗 충전기 시뮬레이터 테스트')
    
    try:
        from charger_simulator import ChargerSimulator
        import inspect
        
        # 인스턴스 생성
        sim = ChargerSimulator('charger_001', 'ws://localhost:9000')
        print_success('ChargerSimulator 인스턴스 생성')
        print(f'    ID: {sim.charger_id}')
        print(f'    URL: {sim.server_url}')
        
        # 메서드 확인
        methods = [m for m in dir(sim) if not m.startswith('_')]
        print_success(f'{len(methods)}개 메서드/속성 발견')
        
        important = ['connect', 'boot', 'start_transaction', 'send_meter_values']
        for method_name in important:
            if method_name in methods:
                print(f'    ✓ {method_name}')
        
        return True
        
    except Exception as e:
        print_error(f'시뮬레이터 테스트 실패: {str(e)}')
        return False


def test_classes_and_methods():
    """Test 6: 클래스 및 메서드 검증"""
    print_section(6, '🔧 클래스 및 메서드 검증')
    
    try:
        from database.services import (
            StationService, ChargerService, StatisticsService
        )
        import inspect
        
        services = [
            ('StationService', StationService),
            ('ChargerService', ChargerService),
            ('StatisticsService', StatisticsService),
        ]
        
        for name, service_class in services:
            methods = [m for m in dir(service_class) 
                      if not m.startswith('_') and callable(getattr(service_class, m))]
            print_success(f'{name}: {len(methods)}개 메서드')
        
        return True
        
    except Exception as e:
        print_error(f'클래스 검증 실패: {str(e)}')
        return False


def test_data_models():
    """Test 7: 데이터 모델 검증"""
    print_section(7, '📋 데이터 모델 검증')
    
    try:
        from database.models_postgresql import (
            StationInfo, ChargerInfo, PowerConsumption,
            ChargerUsageLog, DailyChargerStats, HourlyChargerStats
        )
        
        models = {
            'StationInfo': StationInfo,
            'ChargerInfo': ChargerInfo,
            'PowerConsumption': PowerConsumption,
            'ChargerUsageLog': ChargerUsageLog,
            'DailyChargerStats': DailyChargerStats,
            'HourlyChargerStats': HourlyChargerStats,
        }
        
        for name, model_class in models.items():
            if hasattr(model_class, '__table__'):
                cols = len(model_class.__table__.columns)
                print_success(f'{name}: {cols}개 컬럼')
            else:
                print_success(f'{name}')
        
        return True
        
    except Exception as e:
        print_error(f'데이터 모델 검증 실패: {str(e)}')
        return False


def test_dependencies():
    """Test 8: 의존성 검사"""
    print_section(8, '📚 필수 라이브러리 의존성')
    
    dependencies = [
        ('websockets', 'WebSocket 지원'),
        ('fastapi', 'REST API 프레임워크'),
        ('uvicorn', 'ASGI 서버'),
        ('sqlalchemy', 'ORM'),
        ('pydantic', '데이터 검증'),
        ('aiohttp', '비동기 HTTP'),
        ('psycopg2', 'PostgreSQL 드라이버'),
        ('requests', 'HTTP 클라이언트'),
    ]
    
    results = []
    for pkg_name, description in dependencies:
        try:
            mod = __import__(pkg_name)
            version = getattr(mod, '__version__', 'unknown')
            print_success(f'{pkg_name:<20} v{version:<10} ({description})')
            results.append(True)
        except ImportError:
            print_error(f'{pkg_name:<20} (미설치)')
            results.append(False)
    
    return all(results)


def main():
    """메인 테스트 함수"""
    print_header('🎯 OCPP 2.0.1 (P2M) - 수작업 테스트 실행')
    
    print(f'시작 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Python 버전: {sys.version.split()[0]}')
    print(f'DATABASE_URL: {os.environ.get("DATABASE_URL", "미설정")}')
    
    # 모든 테스트 실행
    test_functions = [
        ('모듈 임포트', test_module_imports),
        ('DB 연결', test_database_connection),
        ('OCPP 메시지', test_ocpp_messages),
        ('DB CRUD', test_database_crud),
        ('시뮬레이터', test_simulator),
        ('클래스/메서드', test_classes_and_methods),
        ('데이터 모델', test_data_models),
        ('라이브러리', test_dependencies),
    ]
    
    results = {}
    for test_name, test_func in test_functions:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print_error(f'테스트 실행 오류: {str(e)}')
            results[test_name] = False
    
    # 최종 결과 출력
    print_header('📋 테스트 결과 요약')
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = '✅' if result else '❌'
        print(f'{status} {test_name:<30} [{("PASS" if result else "FAIL")}]')
    
    print(f'\n결과: {passed}/{total} 테스트 성공')
    
    if passed == total:
        print('\n' + '='*70)
        print('🎉 모든 테스트 성공! 시스템이 정상 작동합니다.')
        print('='*70)
        return 0
    else:
        print('\n' + '='*70)
        print(f'⚠️  {total - passed}개 테스트 실패. MANUAL_TEST_GUIDE.md를 참고하세요.')
        print('='*70)
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('\n\n⛔ 테스트가 사용자에 의해 중단되었습니다.')
        sys.exit(1)
    except Exception as e:
        print(f'\n\n❌ 예기치 않은 오류: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
