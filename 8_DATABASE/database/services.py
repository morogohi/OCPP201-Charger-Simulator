"""
충전기 데이터베이스 관리 서비스
CRUD 작업 및 통계 조회 기능 제공
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database.models import (
    StationInfo, ChargerInfo, ChargerUsageLog, PowerConsumption,
    DailyChargerStats, HourlyChargerStats, StationDailyStats,
    ChargerTypeEnum, ChargerStatusEnum
)


class StationService:
    """충전소 관리 서비스"""
    
    @staticmethod
    def create_station(
        session: Session,
        station_id: str,
        station_name: str,
        address: str,
        longitude: float,
        latitude: float,
        operator_name: str = None,
        operator_phone: str = None,
        operator_email: str = None
    ) -> StationInfo:
        """충전소 등록"""
        station = StationInfo(
            station_id=station_id,
            station_name=station_name,
            address=address,
            longitude=longitude,
            latitude=latitude,
            operator_name=operator_name,
            operator_phone=operator_phone,
            operator_email=operator_email
        )
        session.add(station)
        session.commit()
        return station
    
    @staticmethod
    def get_station(session: Session, station_id: str) -> Optional[StationInfo]:
        """충전소 조회"""
        return session.query(StationInfo).filter(
            StationInfo.station_id == station_id
        ).first()
    
    @staticmethod
    def get_all_stations(session: Session) -> List[StationInfo]:
        """모든 충전소 조회"""
        return session.query(StationInfo).all()
    
    @staticmethod
    def update_station(session: Session, station_id: str, **kwargs) -> Optional[StationInfo]:
        """충전소 정보 수정"""
        station = StationService.get_station(session, station_id)
        if station:
            for key, value in kwargs.items():
                if hasattr(station, key):
                    setattr(station, key, value)
            session.commit()
        return station
    
    @staticmethod
    def delete_station(session: Session, station_id: str) -> bool:
        """충전소 삭제"""
        station = StationService.get_station(session, station_id)
        if station:
            session.delete(station)
            session.commit()
            return True
        return False


class ChargerService:
    """충전기 관리 서비스"""
    
    @staticmethod
    def create_charger(
        session: Session,
        charger_id: str,
        station_id: str,
        serial_number: str,
        charger_type: ChargerTypeEnum,
        rated_power: float,
        max_output: float,
        min_output: float,
        longitude: float,
        latitude: float,
        **kwargs
    ) -> ChargerInfo:
        """충전기 등록"""
        charger = ChargerInfo(
            charger_id=charger_id,
            station_id=station_id,
            serial_number=serial_number,
            charger_type=charger_type,
            rated_power=rated_power,
            max_output=max_output,
            min_output=min_output,
            longitude=longitude,
            latitude=latitude,
            **kwargs
        )
        session.add(charger)
        session.commit()
        return charger
    
    @staticmethod
    def get_charger(session: Session, charger_id: str) -> Optional[ChargerInfo]:
        """충전기 조회"""
        return session.query(ChargerInfo).filter(
            ChargerInfo.charger_id == charger_id
        ).first()
    
    @staticmethod
    def get_chargers_by_station(session: Session, station_id: str) -> List[ChargerInfo]:
        """충전소별 충전기 조회"""
        return session.query(ChargerInfo).filter(
            ChargerInfo.station_id == station_id
        ).all()
    
    @staticmethod
    def get_chargers_by_status(session: Session, status: ChargerStatusEnum) -> List[ChargerInfo]:
        """상태별 충전기 조회"""
        return session.query(ChargerInfo).filter(
            ChargerInfo.current_status == status
        ).all()
    
    @staticmethod
    def get_chargers_by_type(session: Session, charger_type: ChargerTypeEnum) -> List[ChargerInfo]:
        """종류별 충전기 조회"""
        return session.query(ChargerInfo).filter(
            ChargerInfo.charger_type == charger_type
        ).all()
    
    @staticmethod
    def update_charger_status(
        session: Session,
        charger_id: str,
        status: ChargerStatusEnum
    ) -> Optional[ChargerInfo]:
        """충전기 상태 업데이트"""
        charger = ChargerService.get_charger(session, charger_id)
        if charger:
            charger.current_status = status
            charger.last_status_update = datetime.utcnow()
            session.commit()
        return charger
    
    @staticmethod
    def update_power_limit(
        session: Session,
        charger_id: str,
        power_limit: float
    ) -> Optional[ChargerInfo]:
        """충전기 출력 제한 업데이트"""
        charger = ChargerService.get_charger(session, charger_id)
        if charger:
            charger.current_power_limit = power_limit
            session.commit()
        return charger
    
    @staticmethod
    def update_charger(session: Session, charger_id: str, **kwargs) -> Optional[ChargerInfo]:
        """충전기 정보 수정"""
        charger = ChargerService.get_charger(session, charger_id)
        if charger:
            for key, value in kwargs.items():
                if hasattr(charger, key):
                    setattr(charger, key, value)
            session.commit()
        return charger
    
    @staticmethod
    def delete_charger(session: Session, charger_id: str) -> bool:
        """충전기 삭제"""
        charger = ChargerService.get_charger(session, charger_id)
        if charger:
            session.delete(charger)
            session.commit()
            return True
        return False


class UsageLogService:
    """사용 이력 관리 서비스"""
    
    @staticmethod
    def create_usage_log(
        session: Session,
        charger_id: str,
        transaction_id: str,
        session_date: date,
        start_time: datetime,
        **kwargs
    ) -> ChargerUsageLog:
        """충전 세션 기록 생성"""
        log = ChargerUsageLog(
            charger_id=charger_id,
            transaction_id=transaction_id,
            session_date=session_date,
            start_time=start_time,
            **kwargs
        )
        session.add(log)
        session.commit()
        return log
    
    @staticmethod
    def update_usage_log(
        session: Session,
        transaction_id: str,
        **kwargs
    ) -> Optional[ChargerUsageLog]:
        """사용 이력 업데이트"""
        log = session.query(ChargerUsageLog).filter(
            ChargerUsageLog.transaction_id == transaction_id
        ).first()
        
        if log:
            for key, value in kwargs.items():
                if hasattr(log, key):
                    setattr(log, key, value)
            session.commit()
        return log
    
    @staticmethod
    def complete_usage_log(
        session: Session,
        transaction_id: str,
        end_time: datetime,
        energy_delivered: float,
        total_charge: Decimal,
        payment_status: str = 'completed'
    ) -> Optional[ChargerUsageLog]:
        """충전 세션 종료"""
        log = session.query(ChargerUsageLog).filter(
            ChargerUsageLog.transaction_id == transaction_id
        ).first()
        
        if log:
            log.end_time = end_time
            log.duration_minutes = int((end_time - log.start_time).total_seconds() / 60)
            log.energy_delivered = Decimal(str(energy_delivered))
            log.total_charge = total_charge
            log.payment_status = payment_status
            log.status = 'completed'
            session.commit()
        return log
    
    @staticmethod
    def get_usage_logs_by_charger(
        session: Session,
        charger_id: str,
        start_date: date = None,
        end_date: date = None
    ) -> List[ChargerUsageLog]:
        """충전기별 사용 이력 조회"""
        query = session.query(ChargerUsageLog).filter(
            ChargerUsageLog.charger_id == charger_id
        )
        
        if start_date:
            query = query.filter(ChargerUsageLog.session_date >= start_date)
        if end_date:
            query = query.filter(ChargerUsageLog.session_date <= end_date)
        
        return query.order_by(ChargerUsageLog.start_time.desc()).all()
    
    @staticmethod
    def get_daily_revenue(
        session: Session,
        charger_id: str,
        target_date: date
    ) -> Dict[str, Any]:
        """특정 충전기의 일일 매출 조회"""
        logs = session.query(ChargerUsageLog).filter(
            and_(
                ChargerUsageLog.charger_id == charger_id,
                ChargerUsageLog.session_date == target_date,
                ChargerUsageLog.payment_status == 'completed'
            )
        ).all()
        
        total_revenue = sum(log.total_charge for log in logs if log.total_charge)
        total_energy = sum(log.energy_delivered for log in logs if log.energy_delivered)
        
        return {
            'charger_id': charger_id,
            'date': target_date,
            'num_sessions': len(logs),
            'total_revenue': total_revenue,
            'total_energy': total_energy,
            'avg_charge': total_revenue / len(logs) if logs else Decimal('0')
        }


class PowerConsumptionService:
    """전력 사용량 관리 서비스"""
    
    @staticmethod
    def create_power_record(
        session: Session,
        charger_id: str,
        measurement_time: datetime,
        input_power: float,
        cumulative_energy: float,
        **kwargs
    ) -> PowerConsumption:
        """전력 기록 생성"""
        record = PowerConsumption(
            charger_id=charger_id,
            measurement_time=measurement_time,
            measurement_date=measurement_time.date(),
            hour=measurement_time.hour,
            input_power=input_power,
            cumulative_energy=Decimal(str(cumulative_energy)),
            daily_cumulative=Decimal(str(kwargs.get('daily_cumulative', 0))),
            **{k: v for k, v in kwargs.items() if k != 'daily_cumulative'}
        )
        session.add(record)
        session.commit()
        return record
    
    @staticmethod
    def get_power_consumption(
        session: Session,
        charger_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[PowerConsumption]:
        """전력 데이터 조회"""
        return session.query(PowerConsumption).filter(
            and_(
                PowerConsumption.charger_id == charger_id,
                PowerConsumption.measurement_time >= start_time,
                PowerConsumption.measurement_time <= end_time
            )
        ).order_by(PowerConsumption.measurement_time).all()
    
    @staticmethod
    def get_hourly_energy(
        session: Session,
        charger_id: str,
        target_date: date
    ) -> Dict[int, float]:
        """시간대별 에너지 조회"""
        records = session.query(PowerConsumption).filter(
            and_(
                PowerConsumption.charger_id == charger_id,
                PowerConsumption.measurement_date == target_date
            )
        ).all()
        
        hourly_energy = {}
        for record in records:
            if record.hour not in hourly_energy:
                hourly_energy[record.hour] = 0
            hourly_energy[record.hour] = float(record.input_power)
        
        return hourly_energy


class StatisticsService:
    """통계 및 분석 서비스"""
    
    @staticmethod
    def calculate_daily_stats(session: Session, charger_id: str, target_date: date) -> DailyChargerStats:
        """일일 통계 계산 및 저장"""
        # 기존 통계 확인
        existing = session.query(DailyChargerStats).filter(
            and_(
                DailyChargerStats.charger_id == charger_id,
                DailyChargerStats.stats_date == target_date
            )
        ).first()
        
        if existing:
            stats = existing
        else:
            stats = DailyChargerStats(
                charger_id=charger_id,
                stats_date=target_date
            )
        
        # 일일 사용 이력 조회
        logs = session.query(ChargerUsageLog).filter(
            and_(
                ChargerUsageLog.charger_id == charger_id,
                ChargerUsageLog.session_date == target_date,
                ChargerUsageLog.payment_status == 'completed'
            )
        ).all()
        
        # 통계 계산
        stats.num_sessions = len(logs)
        stats.total_energy = Decimal(str(sum(log.energy_delivered or 0 for log in logs)))
        stats.total_duration_minutes = sum(log.duration_minutes or 0 for log in logs)
        stats.total_revenue = Decimal(str(sum(log.total_charge or 0 for log in logs)))
        
        if logs:
            stats.avg_charge_per_session = stats.total_revenue / len(logs)
        
        # 시간대별 통계 계산
        hourly_energy = {}
        hourly_sessions = {}
        hourly_revenue = {}
        
        for log in logs:
            hour = log.start_time.hour
            energy_value = float(log.energy_delivered) if log.energy_delivered else 0
            revenue_value = float(log.total_charge) if log.total_charge else 0
            
            hourly_energy[hour] = hourly_energy.get(hour, 0) + energy_value
            hourly_sessions[hour] = hourly_sessions.get(hour, 0) + 1
            hourly_revenue[hour] = hourly_revenue.get(hour, 0) + revenue_value
        
        stats.hourly_energy = hourly_energy
        stats.hourly_sessions = hourly_sessions
        stats.hourly_revenue = hourly_revenue
        
        session.add(stats)
        session.commit()
        return stats
    
    @staticmethod
    def get_charger_summary(
        session: Session,
        charger_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """충전기 기간별 요약 통계"""
        daily_stats = session.query(DailyChargerStats).filter(
            and_(
                DailyChargerStats.charger_id == charger_id,
                DailyChargerStats.stats_date >= start_date,
                DailyChargerStats.stats_date <= end_date
            )
        ).all()
        
        total_energy = sum(s.total_energy or 0 for s in daily_stats)
        total_revenue = sum(s.total_revenue or 0 for s in daily_stats)
        total_sessions = sum(s.num_sessions for s in daily_stats)
        
        return {
            'charger_id': charger_id,
            'period': f"{start_date} ~ {end_date}",
            'total_sessions': total_sessions,
            'total_energy': total_energy,
            'total_revenue': total_revenue,
            'avg_daily_revenue': total_revenue / len(daily_stats) if daily_stats else Decimal('0'),
            'daily_stats': [
                {
                    'date': s.stats_date,
                    'sessions': s.num_sessions,
                    'energy': s.total_energy,
                    'revenue': s.total_revenue
                }
                for s in daily_stats
            ]
        }
    
    @staticmethod
    def get_station_summary(
        session: Session,
        station_id: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """충전소 기간별 요약 통계"""
        chargers = session.query(ChargerInfo).filter(
            ChargerInfo.station_id == station_id
        ).all()
        
        total_energy = Decimal('0')
        total_revenue = Decimal('0')
        
        for charger in chargers:
            daily_stats = session.query(DailyChargerStats).filter(
                and_(
                    DailyChargerStats.charger_id == charger.charger_id,
                    DailyChargerStats.stats_date >= start_date,
                    DailyChargerStats.stats_date <= end_date
                )
            ).all()
            
            total_energy += sum(s.total_energy or 0 for s in daily_stats)
            total_revenue += sum(s.total_revenue or 0 for s in daily_stats)
        
        return {
            'station_id': station_id,
            'period': f"{start_date} ~ {end_date}",
            'num_chargers': len(chargers),
            'total_energy': total_energy,
            'total_revenue': total_revenue,
            'avg_charger_revenue': total_revenue / len(chargers) if chargers else Decimal('0')
        }


if __name__ == "__main__":
    from database.models import db_manager
    
    # 데이터베이스 초기화
    db_manager.initialize()
    session = db_manager.get_session()
    
    print("✅ 데이터베이스 서비스 모듈 로드 완료")
    
    session.close()
