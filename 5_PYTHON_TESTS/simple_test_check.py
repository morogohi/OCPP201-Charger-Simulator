#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OCPP 2.0.1 간단한 테스트 결과 확인"""

import psycopg2
from tabulate import tabulate
from datetime import datetime

try:
    conn = psycopg2.connect(
        host='localhost',
        database='charger_db',
        user='charger_user',
        password='admin'
    )
    cur = conn.cursor()
    
    print("\n" + "="*80)
    print("  OCPP 2.0.1 테스트 결과 확인")
    print("="*80)
    
    # 1. 전체 통계
    cur.execute("SELECT COUNT(*) as total FROM charger_usage_log")
    total_transactions = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) as total FROM charger_info")
    total_chargers = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(*) as recent FROM charger_usage_log 
        WHERE created_at > NOW() - INTERVAL '24 hours'
    """)
    recent_24h = cur.fetchone()[0]
    
    print("\n📊 데이터베이스 요약")
    print("─" * 80)
    print(f"  ✅ 총 충전기 수: {total_chargers}개")
    print(f"  ✅ 총 거래 기록: {total_transactions}건")
    print(f"  ✅ 최근 24시간: {recent_24h}건")
    
    # 2. 최근 거래
    print("\n📋 최근 거래 (Top 10)")
    print("─" * 80)
    
    cur.execute("""
        SELECT charger_id, transaction_id, energy_delivered, total_charge, 
               duration_minutes, start_time
        FROM charger_usage_log
        ORDER BY start_time DESC
        LIMIT 10
    """)
    
    rows = cur.fetchall()
    if rows:
        headers = ["충전기", "거래ID", "에너지(kWh)", "요금(₩)", "시간(분)", "시작시간"]
        table_data = []
        for charger_id, tid, energy, cost, duration, start_time in rows:
            table_data.append([
                charger_id,
                tid[:25] + "..." if tid and len(tid) > 25 else tid,
                f"{float(energy):.2f}" if energy else "0",
                f"{float(cost):.0f}" if cost else "0",
                duration if duration else "-",
                start_time.strftime("%Y-%m-%d %H:%M:%S") if start_time else "-"
            ])
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # 3. 충전기별 통계
    print("\n📈 충전기별 통계 (Top 10)")
    print("─" * 80)
    
    cur.execute("""
        SELECT charger_id, COUNT(*) as trans_count, 
               SUM(energy_delivered) as total_energy, 
               SUM(total_charge) as total_cost
        FROM charger_usage_log
        GROUP BY charger_id
        ORDER BY trans_count DESC
        LIMIT 10
    """)
    
    rows = cur.fetchall()
    if rows:
        headers = ["충전기", "거래수", "총에너지(kWh)", "총요금(₩)"]
        table_data = []
        for charger_id, trans_count, total_energy, total_cost in rows:
            table_data.append([
                charger_id,
                trans_count,
                f"{float(total_energy):.2f}" if total_energy else "0",
                f"{float(total_cost):.0f}" if total_cost else "0"
            ])
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # 4. 시간별 통계
    print("\n⏰ 시간별 통계 (최근 6시간)")
    print("─" * 80)
    
    cur.execute("""
        SELECT DATE_TRUNC('hour', start_time) as hour,
               COUNT(*) as trans_count,
               SUM(energy_delivered) as total_energy,
               SUM(total_charge) as total_cost
        FROM charger_usage_log
        WHERE start_time > NOW() - INTERVAL '6 hours'
        GROUP BY DATE_TRUNC('hour', start_time)
        ORDER BY hour DESC
    """)
    
    rows = cur.fetchall()
    if rows:
        headers = ["시간", "거래수", "총에너지(kWh)", "총요금(₩)"]
        table_data = []
        for hour, trans_count, total_energy, total_cost in rows:
            table_data.append([
                hour.strftime("%Y-%m-%d %H:00") if hour else "-",
                trans_count,
                f"{float(total_energy):.2f}" if total_energy else "0",
                f"{float(total_cost):.0f}" if total_cost else "0"
            ])
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print("\n" + "="*80)
    print("✅ 데이터베이스 검증 완료!")
    print("="*80 + "\n")
    
    cur.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ 데이터베이스 오류: {e}")
except Exception as e:
    print(f"❌ 오류: {e}")
