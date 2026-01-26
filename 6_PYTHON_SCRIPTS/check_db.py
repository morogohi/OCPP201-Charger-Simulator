#!/usr/bin/env python3
"""Check database for test records"""

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="charger_db",
        user="charger_user",
        password="admin"
    )
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check charger_info
    cursor.execute("SELECT COUNT(*) as count FROM charger_info")
    result = cursor.fetchone()
    print(f"Total chargers in DB: {result['count']}")
    
    # Check charger_usage_log
    cursor.execute("SELECT COUNT(*) as count FROM charger_usage_log")
    result = cursor.fetchone()
    print(f"Total usage records: {result['count']}")
    
    # Get recent records
    cursor.execute("""
        SELECT charger_id, transaction_id, energy_consumed, created_at
        FROM charger_usage_log
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    print("\nRecent records:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"Charger: {row['charger_id']}, Transaction: {row['transaction_id']}, "
              f"Energy: {row['energy_consumed']} kWh, Time: {row['created_at']}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
