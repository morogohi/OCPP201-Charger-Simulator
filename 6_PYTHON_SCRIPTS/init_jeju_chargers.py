"""
제주 EV 충전기 데이터베이스 초기화 및 샘플 데이터 삽입
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
import os
import sys

# 프로젝트 루트 경로 추가 (database 모듈 import를 위함)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '8_DATABASE'))

# PostgreSQL 데이터베이스 사용
try:
    from database.models_postgresql import db_manager, ChargerTypeEnum, ChargerStatusEnum
except ImportError:
    from database.models import db_manager, ChargerTypeEnum, ChargerStatusEnum

from database.services import (
    StationService, ChargerService, UsageLogService, 
    PowerConsumptionService, StatisticsService
)
import random


def init_jeju_chargers():
    """제주 지역 충전기 샘플 데이터 초기화"""
    
    # 데이터베이스 초기화 (PostgreSQL 사용)
    database_url = os.getenv('DATABASE_URL')
    if database_url and 'postgresql' in database_url:
        from database.models_postgresql import DatabaseManager as DBManager
        db_mgr = DBManager(database_url)
    else:
        db_mgr = db_manager
        
    db_mgr.initialize()
    session = db_mgr.get_session()
    
    # 제주 지역 충전소 데이터 (실제 제주 주요 지역 좌표 기반)
    stations_data = [
        {
            'station_id': 'JEJU_STA_001',
            'station_name': '제주시청 충전소',
            'address': '제주특별자치도 제주시 문평로 61',
            'longitude': 126.5307,
            'latitude': 33.4857,
            'operator_name': '제주 EV 충전 네트워크',
            'operator_phone': '064-741-2500',
            'operator_email': 'jeju@evcharger.kr'
        },
        {
            'station_id': 'JEJU_STA_002',
            'station_name': '서귀포 해양관광 충전소',
            'address': '제주특별자치도 서귀포시 중정로 102',
            'longitude': 126.5646,
            'latitude': 33.2525,
            'operator_name': '서귀포 관광 EV 센터',
            'operator_phone': '064-735-3000',
            'operator_email': 'seogwipo@evcharger.kr'
        },
        {
            'station_id': 'JEJU_STA_003',
            'station_name': '제주국제공항 충전소',
            'address': '제주특별자치도 제주시 공항로 2',
            'longitude': 126.4931,
            'latitude': 33.5019,
            'operator_name': '공항 EV 충전소',
            'operator_phone': '064-740-7000',
            'operator_email': 'airport@evcharger.kr'
        },
        {
            'station_id': 'JEJU_STA_004',
            'station_name': '신제주 쇼핑 충전소',
            'address': '제주특별자치도 제주시 중앙로 33',
            'longitude': 126.5833,
            'latitude': 33.5048,
            'operator_name': '신제주 EV 파크',
            'operator_phone': '064-749-5000',
            'operator_email': 'shinjej@evcharger.kr'
        },
        {
            'station_id': 'JEJU_STA_005',
            'station_name': '함덕 해수욕장 충전소',
            'address': '제주특별자치도 제주시 구좌읍 해변로 120',
            'longitude': 126.6765,
            'latitude': 33.5678,
            'operator_name': '북부 해변 EV 센터',
            'operator_phone': '064-784-5000',
            'operator_email': 'hamdeok@evcharger.kr'
        }
    ]
    
    # 충전소 등록
    print("📍 충전소 등록 중...")
    stations = {}
    for station_data in stations_data:
        station = StationService.create_station(session, **station_data)
        stations[station.station_id] = station
        print(f"  ✅ {station.station_name} 등록됨")
    
    # 충전기 데이터 (충전소별 충전기들)
    chargers_config = [
        # JEJU_STA_001: 제주시청
        [
            {
                'charger_id': 'JEJU_CHG_001_01',
                'serial_number': 'SN-2024-0001',
                'charger_type': ChargerTypeEnum.FAST,
                'rated_power': 50.0,
                'max_output': 55.0,
                'min_output': 10.0,
                'longitude': 126.5310,
                'latitude': 33.4860,
                'unit_price_kwh': Decimal('300'),
                'base_fee': Decimal('1000')
            },
            {
                'charger_id': 'JEJU_CHG_001_02',
                'serial_number': 'SN-2024-0002',
                'charger_type': ChargerTypeEnum.SLOW,
                'rated_power': 22.0,
                'max_output': 22.0,
                'min_output': 3.7,
                'longitude': 126.5315,
                'latitude': 33.4858,
                'unit_price_kwh': Decimal('250'),
                'base_fee': Decimal('500')
            }
        ],
        # JEJU_STA_002: 서귀포
        [
            {
                'charger_id': 'JEJU_CHG_002_01',
                'serial_number': 'SN-2024-0003',
                'charger_type': ChargerTypeEnum.FAST,
                'rated_power': 60.0,
                'max_output': 65.0,
                'min_output': 10.0,
                'longitude': 126.5650,
                'latitude': 33.2520,
                'unit_price_kwh': Decimal('320'),
                'base_fee': Decimal('1200')
            },
            {
                'charger_id': 'JEJU_CHG_002_02',
                'serial_number': 'SN-2024-0004',
                'charger_type': ChargerTypeEnum.SLOW,
                'rated_power': 22.0,
                'max_output': 22.0,
                'min_output': 3.7,
                'longitude': 126.5645,
                'latitude': 33.2530,
                'unit_price_kwh': Decimal('250'),
                'base_fee': Decimal('500')
            }
        ],
        # JEJU_STA_003: 공항
        [
            {
                'charger_id': 'JEJU_CHG_003_01',
                'serial_number': 'SN-2024-0005',
                'charger_type': ChargerTypeEnum.ULTRA_FAST,
                'rated_power': 100.0,
                'max_output': 120.0,
                'min_output': 20.0,
                'longitude': 126.4935,
                'latitude': 33.5015,
                'unit_price_kwh': Decimal('400'),
                'base_fee': Decimal('2000')
            },
            {
                'charger_id': 'JEJU_CHG_003_02',
                'serial_number': 'SN-2024-0006',
                'charger_type': ChargerTypeEnum.FAST,
                'rated_power': 50.0,
                'max_output': 55.0,
                'min_output': 10.0,
                'longitude': 126.4930,
                'latitude': 33.5025,
                'unit_price_kwh': Decimal('330'),
                'base_fee': Decimal('1000')
            }
        ],
        # JEJU_STA_004: 신제주
        [
            {
                'charger_id': 'JEJU_CHG_004_01',
                'serial_number': 'SN-2024-0007',
                'charger_type': ChargerTypeEnum.FAST,
                'rated_power': 50.0,
                'max_output': 55.0,
                'min_output': 10.0,
                'longitude': 126.5835,
                'latitude': 33.5050,
                'unit_price_kwh': Decimal('310'),
                'base_fee': Decimal('1000')
            },
            {
                'charger_id': 'JEJU_CHG_004_02',
                'serial_number': 'SN-2024-0008',
                'charger_type': ChargerTypeEnum.SLOW,
                'rated_power': 22.0,
                'max_output': 22.0,
                'min_output': 3.7,
                'longitude': 126.5830,
                'latitude': 33.5045,
                'unit_price_kwh': Decimal('250'),
                'base_fee': Decimal('500')
            }
        ],
        # JEJU_STA_005: 함덕
        [
            {
                'charger_id': 'JEJU_CHG_005_01',
                'serial_number': 'SN-2024-0009',
                'charger_type': ChargerTypeEnum.FAST,
                'rated_power': 50.0,
                'max_output': 55.0,
                'min_output': 10.0,
                'longitude': 126.6770,
                'latitude': 33.5680,
                'unit_price_kwh': Decimal('300'),
                'base_fee': Decimal('1000')
            }
        ]
    ]
    
    # 충전기 등록
    print("\n🔌 충전기 등록 중...")
    all_chargers = []
    for station_id, chargers in zip(stations.keys(), chargers_config):
        for charger_config in chargers:
            charger = ChargerService.create_charger(
                session,
                **charger_config,
                station_id=station_id,
                current_status=random.choice([
                    ChargerStatusEnum.AVAILABLE,
                    ChargerStatusEnum.IN_USE,
                    ChargerStatusEnum.OFFLINE
                ]),
                location_detail=f"{charger_config['charger_id']} 위치"
            )
            all_chargers.append(charger)
            print(f"  ✅ {charger.charger_id} 등록됨")
        
        # 충전소의 총 충전기 수 업데이트
        stations[station_id].total_chargers = len(chargers)
    
    session.commit()
    
    # 샘플 사용 이력 생성 (지난 7일)
    print("\n📊 샘플 사용 이력 생성 중...")
    for i in range(7):
        target_date = date.today() - timedelta(days=i)
        for charger in all_chargers:
            # 하루에 3-8번의 충전 세션
            num_sessions = random.randint(3, 8)
            for j in range(num_sessions):
                # 랜덤 시간에 시작
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                start_time = datetime.combine(target_date, datetime.min.time()).replace(hour=hour, minute=minute)
                
                # 에너지 및 요금 계산
                energy = round(random.uniform(5, 50), 2)
                duration = random.randint(10, 120)
                
                energy_charge = Decimal(str(energy)) * charger.unit_price_kwh
                time_charge = Decimal(str(duration)) * Decimal('10')
                total_charge = charger.base_fee + energy_charge + time_charge
                
                transaction_id = f"TXN-{charger.charger_id}-{int(target_date.toordinal())}-{j}"
                
                log = UsageLogService.create_usage_log(
                    session,
                    charger.charger_id,
                    transaction_id,
                    target_date,
                    start_time,
                    end_time=start_time + timedelta(minutes=duration),
                    energy_delivered=Decimal(str(energy)),
                    duration_minutes=duration,
                    base_charge=charger.base_fee,
                    energy_charge=energy_charge,
                    time_charge=time_charge,
                    total_charge=total_charge,
                    payment_status='completed'
                )
        
        # 일일 통계 계산
        for charger in all_chargers:
            StatisticsService.calculate_daily_stats(session, charger.charger_id, target_date)
        
        print(f"  ✅ {target_date} 데이터 생성 완료")
    
    session.commit()
    
    # 전력 사용량 데이터 생성
    print("\n⚡ 전력 사용량 데이터 생성 중...")
    target_date = date.today()
    for charger in all_chargers:
        cumulative = Decimal('0')
        daily_cumulative = Decimal('0')
        
        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                measurement_time = datetime.combine(
                    target_date,
                    datetime.min.time()
                ).replace(hour=hour, minute=minute)
                
                # 사용 시간에는 전력 사용, 아니면 0
                if random.random() < 0.3:  # 30% 확률로 충전 중
                    input_power = random.uniform(10, charger.max_output)
                    is_charging = True
                else:
                    input_power = random.uniform(0, 2)
                    is_charging = False
                
                cumulative += Decimal(str(input_power / 4))  # 15분 단위
                daily_cumulative += Decimal(str(input_power / 4))
                
                PowerConsumptionService.create_power_record(
                    session,
                    charger.charger_id,
                    measurement_time,
                    input_power,
                    cumulative,
                    daily_cumulative=daily_cumulative,
                    is_charging=is_charging
                )
    
    print(f"  ✅ 전력 사용량 데이터 생성 완료")
    
    session.commit()
    session.close()
    
    # 요약 출력
    print("\n" + "="*50)
    print("✅ 데이터베이스 초기화 완료!")
    print("="*50)
    print(f"📍 충전소: {len(stations)}")
    print(f"🔌 충전기: {len(all_chargers)}")
    print(f"📊 기간: 지난 7일")
    print("="*50)


def reset_database():
    """데이터베이스 초기화 (모든 데이터 삭제)"""
    from database.models import Base
    
    print("⚠️  데이터베이스를 초기화하시겠습니까? (모든 데이터가 삭제됩니다)")
    response = input("계속하려면 'yes'를 입력하세요: ")
    
    if response.lower() == 'yes':
        print("🗑️  데이터베이스 초기화 중...")
        Base.metadata.drop_all(bind=db_manager.engine)
        Base.metadata.create_all(bind=db_manager.engine)
        print("✅ 데이터베이스 초기화 완료")
    else:
        print("❌ 취소됨")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_jeju_chargers()
        print("\n🎯 다음 명령어로 API를 실행하세요:")
        print("   python gis_dashboard_api.py")
        print("\n🌐 대시보드에 접속하세요:")
        print("   http://localhost:8000/docs (API 문서)")
        print("   gis_dashboard.html (웹 대시보드)")
