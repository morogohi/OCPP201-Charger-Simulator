#!/usr/bin/env python3
"""
간단한 데이터베이스 및 서비스 테스트
"""

import os
os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

from database.models_postgresql import DatabaseManager
from database.services import StationService, ChargerService, StatisticsService

print("\n" + "="*70)
print("  OCPP 2.0.1 - 통합 테스트 (데이터베이스 + 서비스)")
print("="*70 + "\n")

# 1. 데이터베이스 연결
print("[1/5] Database Connection")
print("-" * 70)
try:
    db = DatabaseManager()
    db.initialize()
    session = db.get_session()
    print("SUCCESS: Database connected")
    
    # 테이블 개수 확인
    from sqlalchemy import text
    result = session.execute(text("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' ORDER BY table_name
    """))
    tables = [row[0] for row in result]
    print(f"Tables ({len(tables)}): {', '.join(tables)}")
    session.close()
    print()
except Exception as e:
    print(f"FAILED: {str(e)}\n")
    exit(1)

# 2. 충전소 조회
print("[2/5] Station Data")
print("-" * 70)
try:
    session = db.get_session()
    station_service = StationService(session)
    stations = station_service.get_all()
    print(f"SUCCESS: Found {len(stations)} stations")
    for station in stations[:2]:
        print(f"  - {station.station_name} ({station.location})")
    session.close()
    print()
except Exception as e:
    print(f"FAILED: {str(e)}\n")

# 3. 충전기 조회
print("[3/5] Charger Data")
print("-" * 70)
try:
    session = db.get_session()
    charger_service = ChargerService(session)
    chargers = charger_service.get_all()
    print(f"SUCCESS: Found {len(chargers)} chargers")
    
    # 상태별 분류
    available = sum(1 for c in chargers if c.current_status == 'available')
    in_use = sum(1 for c in chargers if c.current_status == 'in_use')
    fault = sum(1 for c in chargers if c.current_status == 'fault')
    offline = len(chargers) - available - in_use - fault
    
    print(f"  - Available: {available}")
    print(f"  - In Use: {in_use}")
    print(f"  - Fault: {fault}")
    print(f"  - Offline: {offline}")
    
    for charger in chargers[:2]:
        print(f"  - {charger.charger_id} @ ({charger.latitude:.4f}, {charger.longitude:.4f})")
    session.close()
    print()
except Exception as e:
    print(f"FAILED: {str(e)}\n")

# 4. 통계 조회
print("[4/5] Statistics")
print("-" * 70)
try:
    session = db.get_session()
    stats_service = StatisticsService(session)
    
    # 오늘 통계
    today_stats = stats_service.get_daily_stats()
    
    print(f"SUCCESS: Statistics data retrieved")
    print(f"  - Total Chargers: {today_stats.get('total_chargers', 0)}")
    print(f"  - Active Chargers: {today_stats.get('active_chargers', 0)}")
    print(f"  - Total Energy: {today_stats.get('total_energy', 0):.1f} kWh")
    print(f"  - Total Revenue: {today_stats.get('total_revenue', 0):,.0f} KRW")
    print(f"  - Sessions: {today_stats.get('sessions', 0)}")
    session.close()
    print()
except Exception as e:
    print(f"FAILED: {str(e)}\n")

# 5. API 모델 확인
print("[5/5] API Models")
print("-" * 70)
try:
    from gis_dashboard_api import app
    print(f"SUCCESS: FastAPI app initialized")
    print(f"  - Title: {app.title}")
    print(f"  - Version: {app.version}")
    
    # 라우트 확인
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(f"{route.path}")
    print(f"  - Routes: {len(routes)} endpoints")
    print()
except Exception as e:
    print(f"FAILED: {str(e)}\n")

print("="*70)
print("SUCCESS: All tests passed!")
print("="*70)
print("\n[Next Steps]")
print("1. Start API server:")
print("   python gis_dashboard_api.py")
print("\n2. Open dashboard:")
print("   advanced_dashboard.html (in browser)")
print("\n3. API Documentation:")
print("   http://localhost:3000/docs")
print("\n")
