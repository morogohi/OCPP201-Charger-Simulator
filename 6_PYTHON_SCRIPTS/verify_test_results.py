#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 결과 검증 스크립트

OCPP 2.0.1 시뮬레이터 테스트 후 데이터베이스에서 결과를 검증합니다.
"""

import psycopg2
from datetime import datetime, timedelta
from tabulate import tabulate
import sys

class TestResultVerifier:
    """테스트 결과 검증 클래스"""
    
    def __init__(self, host='localhost', database='charger_db', 
                 user='charger_user', password='admin'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.cur = None
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cur = self.conn.cursor()
            print("✅ 데이터베이스 연결 성공")
            return True
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """연결 해제"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
    
    def get_recent_transactions(self, minutes=30, limit=20):
        """최근 거래 조회"""
        try:
            self.cur.execute('''
                SELECT charger_id, transaction_id, energy_consumed, cost, 
                       duration_seconds, start_time, end_time
                FROM charger_usage_log
                WHERE start_time > NOW() - INTERVAL '%d minutes'
                ORDER BY start_time DESC
                LIMIT %d
            ''' % (minutes, limit))
            
            rows = self.cur.fetchall()
            return rows
        except Exception as e:
            print(f"❌ 조회 오류: {e}")
            return []
    
    def get_charger_stats(self):
        """충전기별 통계"""
        try:
            self.cur.execute('''
                SELECT charger_id, COUNT(*) as transaction_count, 
                       SUM(energy_consumed) as total_energy_kwh, 
                       SUM(cost) as total_cost_won,
                       AVG(duration_seconds) as avg_duration_sec
                FROM charger_usage_log
                WHERE start_time > NOW() - INTERVAL '1 day'
                GROUP BY charger_id
                ORDER BY charger_id
            ''')
            
            rows = self.cur.fetchall()
            return rows
        except Exception as e:
            print(f"❌ 조회 오류: {e}")
            return []
    
    def get_hourly_stats(self):
        """시간별 통계"""
        try:
            self.cur.execute('''
                SELECT DATE_TRUNC('hour', start_time) as hour,
                       COUNT(*) as transaction_count,
                       SUM(energy_consumed) as total_energy_kwh,
                       SUM(cost) as total_cost_won
                FROM charger_usage_log
                WHERE start_time > NOW() - INTERVAL '24 hours'
                GROUP BY DATE_TRUNC('hour', start_time)
                ORDER BY hour DESC
                LIMIT 10
            ''')
            
            rows = self.cur.fetchall()
            return rows
        except Exception as e:
            print(f"❌ 조회 오류: {e}")
            return []
    
    def verify_scenario_1(self):
        """시나리오 1 검증: 기본 연결"""
        print("\n" + "="*80)
        print("[검증] 시나리오 1: 기본 연결 및 BootNotification")
        print("="*80)
        
        try:
            self.cur.execute('''
                SELECT COUNT(*) FROM charger_usage_log
                WHERE start_time > NOW() - INTERVAL '5 minutes'
            ''')
            
            count = self.cur.fetchone()[0]
            
            if count > 0:
                print(f"✅ 연결 성공: {count}건의 거래 기록 발견")
                return True
            else:
                print("❌ 연결 실패: 거래 기록 없음")
                return False
                
        except Exception as e:
            print(f"❌ 검증 오류: {e}")
            return False
    
    def verify_scenario_2(self):
        """시나리오 2 검증: 충전 세션"""
        print("\n" + "="*80)
        print("[검증] 시나리오 2: 충전 세션")
        print("="*80)
        
        try:
            self.cur.execute('''
                SELECT charger_id, energy_consumed, cost, duration_seconds, 
                       transaction_id, start_time
                FROM charger_usage_log
                WHERE start_time > NOW() - INTERVAL '30 minutes'
                  AND energy_consumed > 0
                ORDER BY start_time DESC
                LIMIT 1
            ''')
            
            row = self.cur.fetchone()
            
            if row:
                charger_id, energy, cost, duration, tid, start_time = row
                
                print(f"✅ 거래 기록 발견:")
                print(f"   충전기: {charger_id}")
                print(f"   거래ID: {tid}")
                print(f"   에너지: {energy:.2f} kWh")
                print(f"   요금: ₩{cost:.0f}")
                print(f"   지속시간: {duration}초")
                print(f"   시작시간: {start_time}")
                
                # 검증
                checks = []
                checks.append(("에너지 > 0", energy > 0))
                checks.append(("요금 계산됨", cost > 0))
                checks.append(("지속시간 30초 이상", duration >= 30))
                
                all_pass = all(check[1] for check in checks)
                
                print(f"\n   검증 결과:")
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"   {status} {check_name}")
                
                return all_pass
            else:
                print("❌ 거래 기록 없음")
                return False
                
        except Exception as e:
            print(f"❌ 검증 오류: {e}")
            return False
    
    def verify_scenario_3(self):
        """시나리오 3 검증: 다중 충전기"""
        print("\n" + "="*80)
        print("[검증] 시나리오 3: 다중 충전기")
        print("="*80)
        
        try:
            self.cur.execute('''
                SELECT COUNT(DISTINCT charger_id) as charger_count,
                       COUNT(*) as transaction_count,
                       SUM(energy_consumed) as total_energy
                FROM charger_usage_log
                WHERE start_time > NOW() - INTERVAL '60 minutes'
            ''')
            
            charger_count, trans_count, total_energy = self.cur.fetchone()
            
            if charger_count and charger_count > 0:
                print(f"✅ 다중 충전기 감지:")
                print(f"   충전기 수: {charger_count}개")
                print(f"   거래 수: {trans_count}건")
                print(f"   총 에너지: {total_energy:.2f} kWh")
                
                # 충전기별 상세
                self.cur.execute('''
                    SELECT charger_id, COUNT(*) as trans_count, 
                           SUM(energy_consumed) as energy
                    FROM charger_usage_log
                    WHERE start_time > NOW() - INTERVAL '60 minutes'
                    GROUP BY charger_id
                    ORDER BY charger_id
                ''')
                
                print(f"\n   충전기별 통계:")
                for cid, tcount, energy in self.cur.fetchall():
                    print(f"   • {cid}: {tcount}건, {energy:.2f}kWh")
                
                return charger_count >= 2
            else:
                print("❌ 충전기 기록 없음")
                return False
                
        except Exception as e:
            print(f"❌ 검증 오류: {e}")
            return False
    
    def show_recent_transactions(self, minutes=30):
        """최근 거래 표시"""
        print("\n" + "="*80)
        print(f"[최근 거래] 최근 {minutes}분")
        print("="*80)
        
        rows = self.get_recent_transactions(minutes)
        
        if not rows:
            print("기록 없음")
            return
        
        headers = ["충전기", "거래ID", "에너지(kWh)", "요금(₩)", "시간(초)", "시작시간"]
        table_data = []
        
        for row in rows:
            charger_id, tid, energy, cost, duration, start_time, end_time = row
            table_data.append([
                charger_id,
                tid[:12] if tid else "-",
                f"{energy:.2f}" if energy else "0",
                f"{cost:.0f}" if cost else "0",
                duration if duration else "-",
                start_time.strftime("%H:%M:%S") if start_time else "-"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def show_charger_stats(self):
        """충전기별 통계 표시"""
        print("\n" + "="*80)
        print("[충전기별 통계] 최근 24시간")
        print("="*80)
        
        rows = self.get_charger_stats()
        
        if not rows:
            print("기록 없음")
            return
        
        headers = ["충전기", "거래수", "총에너지(kWh)", "총요금(₩)", "평균시간(초)"]
        table_data = []
        
        for row in rows:
            charger_id, trans_count, total_energy, total_cost, avg_duration = row
            table_data.append([
                charger_id,
                trans_count,
                f"{total_energy:.2f}" if total_energy else "0",
                f"{total_cost:.0f}" if total_cost else "0",
                f"{avg_duration:.0f}" if avg_duration else "-"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def show_hourly_stats(self):
        """시간별 통계 표시"""
        print("\n" + "="*80)
        print("[시간별 통계] 최근 24시간")
        print("="*80)
        
        rows = self.get_hourly_stats()
        
        if not rows:
            print("기록 없음")
            return
        
        headers = ["시간", "거래수", "총에너지(kWh)", "총요금(₩)"]
        table_data = []
        
        for row in rows:
            hour, trans_count, total_energy, total_cost = row
            table_data.append([
                hour.strftime("%Y-%m-%d %H:00") if hour else "-",
                trans_count,
                f"{total_energy:.2f}" if total_energy else "0",
                f"{total_cost:.0f}" if total_cost else "0"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def run_all_verifications(self):
        """모든 검증 실행"""
        if not self.connect():
            return False
        
        results = {}
        
        try:
            # 각 시나리오 검증
            results['scenario_1'] = self.verify_scenario_1()
            results['scenario_2'] = self.verify_scenario_2()
            results['scenario_3'] = self.verify_scenario_3()
            
            # 통계 표시
            self.show_recent_transactions()
            self.show_charger_stats()
            self.show_hourly_stats()
            
            # 요약
            print("\n" + "="*80)
            print("[검증 요약]")
            print("="*80)
            
            for scenario, passed in results.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status} - {scenario}")
            
            all_pass = all(results.values())
            
            print()
            if all_pass:
                print("🎉 모든 테스트 검증 완료!")
            else:
                print("⚠️  일부 검증 실패. 테스트 로그를 확인하세요.")
            
            return all_pass
            
        finally:
            self.disconnect()


def main():
    """메인 함수"""
    print("="*80)
    print("  OCPP 2.0.1 테스트 결과 검증")
    print("="*80)
    print()
    
    verifier = TestResultVerifier()
    verifier.run_all_verifications()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단됨")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
