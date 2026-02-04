#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이마트 제주 3개 점포에 충전기 추가 스크립트
- 이마트 제주점: 100kW 12개
- 이마트 신제주점: 50kW 10개
- 이마트 서귀포점: 100kW 12개
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# 환경 설정
os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

# Windows 인코딩
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from database.models_postgresql import DatabaseManager
from sqlalchemy import text

# 이마트 점포 정보
EMART_STATIONS = [
    {
        'station_id': 'emart_jeju_main',
        'station_name': '이마트 제주점 충전소',
        'location': '제주특별자치도 제주시 중앙로 148',
        'latitude': 33.5119,
        'longitude': 126.5245,
        'address': '제주시 중앙로 148',
        'chargers': [
            {
                'count': 12,
                'power': 100,
                'type': 'ULTRA_FAST'  # 초급속 충전
            }
        ]
    },
    {
        'station_id': 'emart_shinjeju',
        'station_name': '이마트 신제주점 충전소',
        'location': '제주특별자치도 제주시 신제주로 36',
        'latitude': 33.5087,
        'longitude': 126.5290,
        'address': '제주시 신제주로 36',
        'chargers': [
            {
                'count': 10,
                'power': 50,
                'type': 'FAST'  # 급속 충전
            }
        ]
    },
    {
        'station_id': 'emart_seogwipo',
        'station_id_alt': 'emart_seogwipo_main',  # 중복 방지
        'station_name': '이마트 서귀포점 충전소',
        'location': '제주특별자치도 서귀포시 중산간로 465',
        'latitude': 33.2432,
        'longitude': 126.5659,
        'address': '서귀포시 중산간로 465',
        'chargers': [
            {
                'count': 12,
                'power': 100,
                'type': 'ULTRA_FAST'  # 초급속 충전
            }
        ]
    }
]

def add_emart_stations():
    """이마트 점포의 충전소와 충전기 추가"""
    db = DatabaseManager()
    db.initialize()
    session = db.get_session()
    
    print("\n" + "="*70)
    print("  이마트 제주 3개 점포 충전기 추가")
    print("="*70 + "\n")
    
    try:
        for station_info in EMART_STATIONS:
            station_id = station_info['station_id']
            station_name = station_info['station_name']
            
            print(f"📍 {station_name}")
            print(f"   주소: {station_info['address']}")
            print(f"   좌표: ({station_info['latitude']:.4f}, {station_info['longitude']:.4f})")
            
            # 기존 충전소 확인
            result = session.execute(text("""
                SELECT station_id FROM station_info 
                WHERE station_id = :station_id
            """), {'station_id': station_id})
            
            existing = result.scalar()
            
            if existing:
                print(f"   ⚠️  이미 존재함 (스킵)\n")
                continue
            
            # 충전소 추가
            session.execute(text("""
                INSERT INTO station_info 
                (station_id, station_name, address, latitude, longitude, total_chargers, created_at)
                VALUES 
                (:station_id, :station_name, :address, :latitude, :longitude, :total_chargers, :created_at)
            """), {
                'station_id': station_id,
                'station_name': station_name,
                'address': station_info['address'],
                'latitude': station_info['latitude'],
                'longitude': station_info['longitude'],
                'total_chargers': sum(c['count'] for c in station_info['chargers']),
                'created_at': datetime.now()
            })
            
            # 충전기 추가
            charger_count = 0
            for charger_group in station_info['chargers']:
                count = charger_group['count']
                power = charger_group['power']
                charger_type = charger_group['type']
                
                for i in range(1, count + 1):
                    charger_id = f"{station_id}_{i:02d}"
                    charger_name = f"{station_name} - {i}번"
                    serial_number = f"SN-{station_id.upper()}-{i:04d}"
                    
                    # 위도/경도 약간 다르게 설정 (클러스터링)
                    lat = station_info['latitude'] + (i * 0.0001)
                    lng = station_info['longitude'] + (i * 0.0001)
                    
                    session.execute(text("""
                        INSERT INTO charger_info 
                        (charger_id, station_id, serial_number, charger_type, 
                         rated_power, max_output, min_output,
                         connector_type, latitude, longitude, 
                         current_status, location_detail, installation_date, created_at)
                        VALUES 
                        (:charger_id, :station_id, :serial_number, :charger_type, 
                         :rated_power, :max_output, :min_output,
                         :connector_type, :latitude, :longitude, 
                         :current_status, :location_detail, :installation_date, :created_at)
                    """), {
                        'charger_id': charger_id,
                        'station_id': station_id,
                        'serial_number': serial_number,
                        'charger_type': charger_type,
                        'rated_power': float(power),
                        'max_output': float(power),
                        'min_output': 10.0,
                        'connector_type': 'Type2_DC',
                        'latitude': lat,
                        'longitude': lng,
                        'current_status': 'AVAILABLE',
                        'location_detail': charger_name,
                        'installation_date': datetime.now().date(),
                        'created_at': datetime.now()
                    })
                    charger_count += 1
            
            print(f"   ✅ 충전기 {charger_count}개 추가됨")
            print(f"      - 전력: {EMART_STATIONS[EMART_STATIONS.index(station_info)]['chargers'][0]['power']}kW")
            print()
        
        # 커밋
        session.commit()
        
        # 최종 통계
        result = session.execute(text("""
            SELECT COUNT(*) FROM station_info 
            WHERE station_id IN ('emart_jeju_main', 'emart_shinjeju', 'emart_seogwipo')
        """))
        station_count = result.scalar()
        
        result = session.execute(text("""
            SELECT COUNT(*) FROM charger_info 
            WHERE station_id IN ('emart_jeju_main', 'emart_shinjeju', 'emart_seogwipo')
        """))
        charger_count = result.scalar()
        
        print("="*70)
        print(f"✅ 데이터 추가 완료!")
        print(f"   추가된 충전소: {station_count}개")
        print(f"   추가된 충전기: {charger_count}개")
        print("="*70 + "\n")
        
        # 상세 정보 출력
        print("📊 추가된 충전기 위치 정보:\n")
        
        for station in EMART_STATIONS:
            sid = station['station_id']
            result = session.execute(text(f"""
                SELECT charger_id, latitude, longitude, rated_power, current_status 
                FROM charger_info 
                WHERE station_id = '{sid}'
                ORDER BY charger_id
                LIMIT 3
            """))
            
            chargers = result.fetchall()
            if chargers:
                print(f"📍 {station['station_name']}")
                for charger_id, lat, lng, power, status in chargers:
                    print(f"   • {charger_id}: ({lat:.4f}, {lng:.4f}) - {power}kW - {status}")
                print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = add_emart_stations()
    sys.exit(0 if success else 1)
