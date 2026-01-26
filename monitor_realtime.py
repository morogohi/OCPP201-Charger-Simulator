#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실시간 모니터링 대시보드 (Terminal 4용)
OCPP 서버와 데이터베이스 상태를 실시간으로 모니터링합니다.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Windows UTF-8 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)

# 경로 설정
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '8_DATABASE'))

# 환경변수 설정
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

try:
    from database.models_postgresql import DatabaseManager
    from database.services import ChargerService, StatisticsService
except ImportError:
    print("❌ database 모듈을 import할 수 없습니다")
    sys.exit(1)


def clear_screen():
    """화면 지우기"""
    os.system('clear' if os.name == 'posix' else 'cls')


def get_timestamp():
    """현재 시간 반환"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def monitor_chargers():
    """충전기 상태 모니터링"""
    try:
        db = DatabaseManager()
        db.initialize()
        session = db.get_session()
        
        chargers = ChargerService.get_all_chargers(session)
        
        print(f"\n{'시간':<20} {'충전기 ID':<25} {'상태':<15} {'마지막 업데이트'}")
        print("=" * 80)
        
        for charger in chargers:
            # 시뮬레이터 관련 충전기만 표시
            if 'SIM' in charger.charger_id:
                status = charger.current_status if charger.current_status else "UNKNOWN"
                last_update = charger.last_status_update.strftime('%Y-%m-%d %H:%M:%S') if charger.last_status_update else "없음"
                print(f"{get_timestamp():<20} {charger.charger_id:<25} {status:<15} {last_update}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 오류: {e}")


def monitor_statistics():
    """통계 정보 모니터링"""
    try:
        db = DatabaseManager()
        db.initialize()
        session = db.get_session()
        
        # 일일 통계
        from sqlalchemy import func, desc
        from database.models_postgresql import DailyChargerStats
        
        daily_stats = session.query(DailyChargerStats).order_by(
            desc(DailyChargerStats.stat_date)
        ).limit(5).all()
        
        print(f"\n{'날짜':<15} {'충전기':<25} {'충전 횟수':<12} {'에너지(kWh)':<15} {'수익(₩)'}")
        print("=" * 80)
        
        for stat in daily_stats:
            date_str = stat.stat_date.strftime('%Y-%m-%d')
            charger_id = stat.charger_id if hasattr(stat, 'charger_id') else "ALL"
            count = stat.total_transactions if hasattr(stat, 'total_transactions') else 0
            energy = stat.total_energy if hasattr(stat, 'total_energy') else 0
            revenue = stat.total_revenue if hasattr(stat, 'total_revenue') else 0
            
            print(f"{date_str:<15} {charger_id:<25} {count:<12} {float(energy):<15.2f} {int(revenue)}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 오류: {e}")


def monitor_usage_logs():
    """사용 로그 모니터링"""
    try:
        db = DatabaseManager()
        db.initialize()
        session = db.get_session()
        
        from database.models_postgresql import ChargerUsageLog
        from sqlalchemy import desc
        
        logs = session.query(ChargerUsageLog).order_by(
            desc(ChargerUsageLog.start_time)
        ).limit(10).all()
        
        print(f"\n{'시작':<20} {'충전기':<25} {'상태':<12} {'에너지':<12} {'수익(₩)'}")
        print("=" * 80)
        
        for log in logs:
            start = log.start_time.strftime('%Y-%m-%d %H:%M:%S') if log.start_time else "없음"
            charger = log.charger_id if log.charger_id else "UNKNOWN"
            status = "완료" if log.end_time else "진행 중"
            energy = log.energy_delivered if log.energy_delivered else 0
            revenue = log.total_cost if log.total_cost else 0
            
            print(f"{start:<20} {charger:<25} {status:<12} {float(energy):<12.2f} {int(revenue)}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 오류: {e}")


def show_header():
    """헤더 표시"""
    print("\n" + "=" * 80)
    print("실시간 모니터링 대시보드".center(80))
    print("=" * 80)


def main():
    """메인 루프"""
    print("실시간 모니터링 시작...")
    print("Ctrl+C를 눌러서 중지할 수 있습니다\n")
    
    try:
        counter = 0
        while True:
            clear_screen()
            show_header()
            
            print(f"\n[{get_timestamp()}] 모니터링 중... (갱신 간격: 5초)")
            
            # 다양한 정보 표시
            print("\n" + "="*80)
            print("📊 충전기 상태")
            print("="*80)
            monitor_chargers()
            
            print("\n" + "="*80)
            print("📈 일일 통계")
            print("="*80)
            monitor_statistics()
            
            print("\n" + "="*80)
            print("📋 최근 거래")
            print("="*80)
            monitor_usage_logs()
            
            print("\n" + "="*80)
            print(f"[{get_timestamp()}] 5초 후 자동 갱신됩니다... (Ctrl+C로 중지)")
            print("="*80)
            
            # 5초 대기
            time.sleep(5)
            counter += 1
            
    except KeyboardInterrupt:
        print("\n\n❌ 모니터링 중지됨")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
