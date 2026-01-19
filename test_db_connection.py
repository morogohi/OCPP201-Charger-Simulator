#!/usr/bin/env python3
"""
PostgreSQL 데이터베이스 연결 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent))

def test_connection():
    """데이터베이스 연결 테스트"""
    
    print("=" * 60)
    print("📊 PostgreSQL 데이터베이스 연결 테스트")
    print("=" * 60)
    
    # 1. 환경변수 확인
    print("\n[1단계] 환경변수 확인")
    print("-" * 60)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        print(f"✅ DATABASE_URL 환경변수 설정됨")
        # 비밀번호 마스킹
        masked_url = database_url.replace(
            database_url.split(':')[1] if ':' in database_url else '',
            '***'
        )
        print(f"   연결: {masked_url}")
    else:
        print(f"❌ DATABASE_URL 환경변수 미설정")
        database_url = 'postgresql://charger_user:admin@localhost:5432/charger_db'
        print(f"   기본값 사용: {database_url.split(':')[0]}://***@localhost:5432/charger_db")
    
    # 2. psycopg2 모듈 확인
    print("\n[2단계] Python PostgreSQL 드라이버 확인")
    print("-" * 60)
    try:
        import psycopg2
        print(f"✅ psycopg2 설치됨 (버전: {psycopg2.__version__})")
    except ImportError:
        print(f"❌ psycopg2 미설치")
        print(f"   설치: pip install psycopg2-binary")
        return False
    
    # 3. SQLAlchemy 확인
    print("\n[3단계] SQLAlchemy 확인")
    print("-" * 60)
    try:
        from sqlalchemy import __version__
        print(f"✅ SQLAlchemy 설치됨 (버전: {__version__})")
    except ImportError:
        print(f"❌ SQLAlchemy 미설치")
        print(f"   설치: pip install sqlalchemy")
        return False
    
    # 4. 데이터베이스 연결 테스트
    print("\n[4단계] PostgreSQL 데이터베이스 연결 테스트")
    print("-" * 60)
    
    if not database_url:
        database_url = 'postgresql://charger_user:admin@localhost:5432/charger_db'
    
    try:
        import psycopg2
        
        # URL 파싱
        url_parts = database_url.replace('postgresql://', '').split('@')
        user_pass = url_parts[0].split(':')
        host_port_db = url_parts[1].split('/')
        
        user = user_pass[0]
        password = user_pass[1]
        host = host_port_db[0].split(':')[0]
        port = int(host_port_db[0].split(':')[1]) if ':' in host_port_db[0] else 5432
        database = host_port_db[1]
        
        print(f"연결 정보:")
        print(f"  - 사용자: {user}")
        print(f"  - 호스트: {host}")
        print(f"  - 포트: {port}")
        print(f"  - 데이터베이스: {database}")
        
        # 연결 시도
        print(f"\n연결 시도 중...")
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            connect_timeout=5
        )
        
        print(f"✅ 데이터베이스 연결 성공!")
        
        # 버전 확인
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\n📌 PostgreSQL 버전:")
        print(f"   {version.split(',')[0]}")
        
        # 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n📋 데이터베이스 테이블 ({len(tables)}개):")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print(f"\n⚠️  데이터베이스에 테이블이 없습니다")
            print(f"   샘플 데이터 초기화: python init_jeju_chargers.py")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ 데이터베이스 연결 실패")
        print(f"   오류: {str(e).split(chr(10))[0]}")
        print(f"\n해결 방법:")
        print(f"  1. PostgreSQL 서버 실행 확인")
        print(f"  2. 연결 정보 확인 (호스트, 포트, 사용자)")
        print(f"  3. 데이터베이스 및 사용자 생성 확인")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False
    
    # 5. SQLAlchemy 연결 테스트
    print("\n[5단계] SQLAlchemy 엔진 테스트")
    print("-" * 60)
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"✅ SQLAlchemy 엔진 연결 성공!")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy 연결 실패: {str(e)}")
        return False


def main():
    """메인 함수"""
    success = test_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        return 0
    else:
        print("❌ 연결 실패 - 위의 오류 메시지를 확인하세요")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
