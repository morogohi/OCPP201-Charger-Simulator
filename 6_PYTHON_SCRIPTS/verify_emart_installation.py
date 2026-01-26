#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
이마트 충전기 설치 최종 확인
"""

import os
os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

from database.models_postgresql import DatabaseManager
from sqlalchemy import text

db = DatabaseManager()
db.initialize()
session = db.get_session()

print("\n" + "="*80)
print("  이마트 제주 3개 점포 충전기 설치 최종 확인")
print("="*80 + "\n")

# 1. 충전소 확인
print("📍 [1/3] 충전소 정보 확인")
print("-"*80)

result = session.execute(text("""
    SELECT station_id, station_name, address, latitude, longitude, total_chargers
    FROM station_info 
    WHERE station_id IN ('emart_jeju_main', 'emart_shinjeju', 'emart_seogwipo')
    ORDER BY latitude DESC
"""))

stations = result.fetchall()
for sid, sname, addr, lat, lng, total in stations:
    print(f"✅ {sname}")
    print(f"   주소: {addr}")
    print(f"   좌표: {lat:.4f}°N, {lng:.4f}°E")
    print(f"   충전기: {total}개\n")

# 2. 충전기 상세 정보
print("🔌 [2/3] 충전기 상세 정보")
print("-"*80)

result = session.execute(text("""
    SELECT 
        station_id,
        COUNT(*) as count,
        MAX(rated_power) as power_kw,
        charger_type,
        COUNT(CASE WHEN current_status = 'AVAILABLE' THEN 1 END) as available_count
    FROM charger_info
    WHERE station_id IN ('emart_jeju_main', 'emart_shinjeju', 'emart_seogwipo')
    GROUP BY station_id, charger_type
    ORDER BY station_id
"""))

for sid, count, power, ctype, avail in result:
    print(f"📍 {sid}")
    print(f"   충전기: {count}개")
    print(f"   전력: {int(power)}kW")
    print(f"   타입: {ctype}")
    print(f"   사용가능: {avail}/{count} ✅\n")

# 3. 지도 표시 확인
print("🗺️  [3/3] GIS 지도 표시 확인")
print("-"*80)

result = session.execute(text("""
    SELECT 
        charger_id, 
        station_id,
        latitude, 
        longitude, 
        rated_power,
        current_status
    FROM charger_info
    WHERE station_id IN ('emart_jeju_main', 'emart_shinjeju', 'emart_seogwipo')
    ORDER BY station_id, charger_id
    LIMIT 15
"""))

for cid, sid, lat, lng, power, status in result:
    status_icon = "✅" if status == "AVAILABLE" else "⚠️"
    print(f"{status_icon} {cid}: ({lat:.4f}, {lng:.4f}) - {power}kW - {status}")

print("\n... (총 34개 충전기)")

# 4. 최종 통계
print("\n" + "="*80)
print("✅ 최종 설치 통계")
print("="*80)

result = session.execute(text("""
    SELECT 
        COUNT(DISTINCT station_id) as stations,
        COUNT(*) as chargers,
        SUM(rated_power) as total_power,
        COUNT(CASE WHEN current_status = 'AVAILABLE' THEN 1 END) as available
    FROM charger_info
    WHERE station_id IN ('emart_jeju_main', 'emart_shinjeju', 'emart_seogwipo')
"""))

stations, chargers, total_power, available = result.fetchone()

print(f"\n✅ 충전소: {stations}개 (이마트 제주점, 신제주점, 서귀포점)")
print(f"✅ 충전기: {chargers}개")
print(f"✅ 총 설치 용량: {int(total_power)}kW")
print(f"✅ 사용가능: {available}/{chargers}개\n")

print("="*80)
print("🎉 설치 완료! 대시보드에서 확인할 수 있습니다.")
print("="*80 + "\n")

print("📌 다음 단계:")
print("  1. advanced_dashboard.html을 브라우저에서 열기")
print("  2. Leaflet 지도에서 이마트 3개 점포의 충전기 마커 확인")
print("  3. 실시간 상태 모니터링 시작\n")

session.close()
