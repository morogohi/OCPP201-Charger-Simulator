#!/usr/bin/env python3
"""
OCPP 2.0.1 + PostgreSQL + API 통합 테스트
"""

import os
import requests
import json
from datetime import datetime

# 환경설정
API_URL = "http://localhost:3000"
os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

print("\n" + "="*70)
print("  OCPP 2.0.1 EV Charger System - 통합 테스트")
print("="*70 + "\n")

# 테스트 1: 데이터베이스 연결
print("[1/6] 🗄️  데이터베이스 연결 테스트")
print("-" * 70)
try:
    from database.models_postgresql import DatabaseManager
    db = DatabaseManager()
    db.initialize()
    session = db.get_session()
    
    # 테이블 개수 확인
    from sqlalchemy import text
    result = session.execute(text("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema='public'
    """))
    count = result.scalar()
    
    session.close()
    print(f"✅ 데이터베이스 연결 성공")
    print(f"   테이블: {count}개\n")
except Exception as e:
    print(f"❌ 데이터베이스 연결 실패: {str(e)}\n")

# 테스트 2: 충전소 조회
print("[2/6] 🏢 충전소 데이터 조회")
print("-" * 70)
try:
    response = requests.get(f"{API_URL}/stations", timeout=5)
    if response.status_code == 200:
        stations = response.json()
        print(f"✅ 상태: {response.status_code}")
        print(f"   충전소: {len(stations)}개")
        if stations:
            print(f"   예시: {stations[0]['station_name']}\n")
    else:
        print(f"❌ 상태: {response.status_code}\n")
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}\n")

# 테스트 3: 충전기 조회
print("[3/6] 🔌 충전기 데이터 조회")
print("-" * 70)
try:
    response = requests.get(f"{API_URL}/chargers", timeout=5)
    if response.status_code == 200:
        chargers = response.json()
        print(f"✅ 상태: {response.status_code}")
        print(f"   충전기: {len(chargers)}개")
        
        # 상태별 분류
        available = sum(1 for c in chargers if c.get('current_status') == 'available')
        charging = sum(1 for c in chargers if c.get('current_status') == 'in_use')
        fault = sum(1 for c in chargers if c.get('current_status') == 'fault')
        
        print(f"   - 사용가능: {available}개")
        print(f"   - 충전중: {charging}개")
        print(f"   - 고장: {fault}개\n")
    else:
        print(f"❌ 상태: {response.status_code}\n")
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}\n")

# 테스트 4: GIS 데이터 조회
print("[4/6] 🗺️  GIS 지도 데이터 조회")
print("-" * 70)
try:
    response = requests.get(f"{API_URL}/geo/chargers", timeout=5)
    if response.status_code == 200:
        geo_data = response.json()
        print(f"✅ 상태: {response.status_code}")
        print(f"   좌표 데이터: {len(geo_data)}개")
        if geo_data:
            first = geo_data[0]
            print(f"   예시: {first.get('charger_id')} @ ({first.get('latitude')}, {first.get('longitude')})\n")
    else:
        print(f"❌ 상태: {response.status_code}\n")
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}\n")

# 테스트 5: 통계 조회
print("[5/6] 📊 통계 데이터 조회")
print("-" * 70)
try:
    response = requests.get(f"{API_URL}/statistics/dashboard", timeout=5)
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 상태: {response.status_code}")
        print(f"   활성 충전기: {stats.get('total_active_chargers', 0)}개")
        print(f"   오늘 충전량: {stats.get('total_energy_today', 0):.1f} kWh")
        print(f"   오늘 매출: ₩{stats.get('total_revenue_today', 0):,}")
        print(f"   이용률: {stats.get('utilization_rate', 0)}%\n")
    else:
        print(f"❌ 상태: {response.status_code}\n")
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}\n")

# 테스트 6: API 문서
print("[6/6] 📖 API 문서 접근")
print("-" * 70)
try:
    response = requests.get(f"{API_URL}/docs", timeout=5)
    if response.status_code == 200:
        print(f"✅ API 문서: {API_URL}/docs")
        print(f"   상태: {response.status_code}\n")
    else:
        print(f"❌ 상태: {response.status_code}\n")
except Exception as e:
    print(f"❌ 요청 실패: {str(e)}\n")

# 최종 결과
print("="*70)
print("✅ 모든 테스트 완료!")
print("="*70)
print("\n📌 다음 단계:")
print("  1. 고급 대시보드: c:\\Project\\OCPP201(P2M)\\advanced_dashboard.html")
print("  2. API 문서: http://localhost:3000/docs")
print("  3. 기본 대시보드: c:\\Project\\OCPP201(P2M)\\gis_dashboard.html")
print("\n")
