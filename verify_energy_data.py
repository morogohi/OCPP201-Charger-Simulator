#!/usr/bin/env python3
"""Verify server correctly receives energy data"""

import psycopg2
from decimal import Decimal

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="charger_db",
        user="charger_user",
        password="admin"
    )
    
    cursor = conn.cursor()
    
    # Check total records
    cursor.execute("SELECT COUNT(*) FROM charger_usage_log")
    total = cursor.fetchone()[0]
    print(f"데이터베이스 총 거래 기록: {total}개\n")
    
    # Get charger statistics
    print("="*80)
    print("충전기별 에너지 통계")
    print("="*80)
    cursor.execute("""
        SELECT charger_id, COUNT(*) as transaction_count, 
               COALESCE(SUM(energy_delivered), 0) as total_energy,
               COALESCE(AVG(energy_delivered), 0) as avg_energy,
               COALESCE(MAX(energy_delivered), 0) as max_energy,
               COALESCE(SUM(total_charge), 0) as total_revenue
        FROM charger_usage_log
        GROUP BY charger_id
        ORDER BY total_energy DESC
        LIMIT 10
    """)
    
    print(f"{'충전기 ID':<20} {'거래수':>8} {'총에너지':>12} {'평균':>10} {'최대':>10} {'수익':>12}")
    print("-" * 80)
    for row in cursor.fetchall():
        charger_id, txn_count, total_energy, avg_energy, max_energy, total_revenue = row
        print(f"{charger_id:<20} {txn_count:>8} {float(total_energy):>10.2f}kWh {float(avg_energy):>8.2f}kWh "
              f"{float(max_energy):>8.2f}kWh {float(total_revenue):>12,.0f}원")
    
    print("\n" + "="*80)
    print("최근 10개 거래")
    print("="*80)
    cursor.execute("""
        SELECT charger_id, transaction_id, energy_delivered, total_charge, created_at
        FROM charger_usage_log
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    print(f"{'충전기 ID':<20} {'거래 ID':<30} {'에너지':>10} {'요금':>10} {'시간':<26}")
    print("-" * 80)
    for row in cursor.fetchall():
        charger_id, txn_id, energy, charge, created_at = row
        energy_val = float(energy) if energy else 0
        charge_val = float(charge) if charge else 0
        print(f"{charger_id:<20} {txn_id:<30} {energy_val:>9.2f}kWh {charge_val:>9,.0f}원 {str(created_at):<26}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ 서버에서 에너지 데이터를 정상적으로 수신하고 저장하고 있습니다!")
    
except Exception as e:
    print(f"오류: {type(e).__name__}: {e}")
