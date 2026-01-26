#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""데이터베이스 스키마 확인"""

import psycopg2
from psycopg2 import sql

try:
    conn = psycopg2.connect(
        host='localhost',
        database='charger_db',
        user='charger_user',
        password='admin'
    )
    cur = conn.cursor()
    
    # 테이블 목록 확인
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' ORDER BY table_name
    """)
    
    print("=" * 80)
    print("✅ 데이터베이스 테이블 목록")
    print("=" * 80)
    for table in cur.fetchall():
        print(f"  • {table[0]}")
    
    # charger_usage_log 테이블 컬럼 확인
    cur.execute("""
        SELECT column_name, data_type FROM information_schema.columns 
        WHERE table_name='charger_usage_log' ORDER BY ordinal_position
    """)
    
    print("\n" + "=" * 80)
    print("✅ charger_usage_log 테이블 구조")
    print("=" * 80)
    columns = cur.fetchall()
    if columns:
        for col_name, col_type in columns:
            print(f"  • {col_name:<20} : {col_type}")
    else:
        print("  ❌ 테이블이 없거나 컬럼이 없습니다")
    
    # 샘플 데이터 확인
    try:
        cur.execute("SELECT COUNT(*) FROM charger_usage_log")
        count = cur.fetchone()[0]
        print(f"\n✅ charger_usage_log 데이터 행 수: {count}")
        
        if count > 0:
            print("\n최근 데이터 샘플:")
            cur.execute("SELECT * FROM charger_usage_log LIMIT 3")
            for row in cur.fetchall():
                print(f"  {row}")
    except Exception as e:
        print(f"  ❌ 데이터 조회 오류: {e}")
    
    # charger_info 테이블 확인
    cur.execute("""
        SELECT column_name, data_type FROM information_schema.columns 
        WHERE table_name='charger_info' ORDER BY ordinal_position
    """)
    
    print("\n" + "=" * 80)
    print("✅ charger_info 테이블 구조")
    print("=" * 80)
    columns = cur.fetchall()
    if columns:
        for col_name, col_type in columns:
            print(f"  • {col_name:<20} : {col_type}")
    else:
        print("  ❌ 테이블이 없습니다")
    
    # 충전기 데이터 개수
    try:
        cur.execute("SELECT COUNT(*) FROM charger_info")
        count = cur.fetchone()[0]
        print(f"\n✅ charger_info 데이터 행 수: {count}")
    except Exception as e:
        print(f"  ❌ 오류: {e}")
    
    cur.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ 데이터베이스 오류: {e}")
except Exception as e:
    print(f"❌ 오류: {e}")
