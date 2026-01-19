"""
제주 EV 충전기 데이터 관리 시스템 - PostgreSQL 최적화 모델
OCPP 2.0.1 충전기 정보 및 운영 데이터 저장
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime, 
    Date, Numeric, ForeignKey, Enum, Boolean, Text, Index,
    Table, UniqueConstraint, BigInteger, TIMESTAMP
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.types import JSON, JSONB
import enum
import os

Base = declarative_base()


class ChargerTypeEnum(str, enum.Enum):
    """충전기 종류 열거형"""
    FAST = "fast"        # 급속 충전
    SLOW = "slow"        # 완속 충전
    ULTRA_FAST = "ultra_fast"  # 초급속 충전


class ChargerStatusEnum(str, enum.Enum):
    """충전기 현재 상태 열거형"""
    AVAILABLE = "available"        # 사용 가능
    IN_USE = "in_use"              # 사용 중
    MAINTENANCE = "maintenance"    # 정비 중
    FAULT = "fault"                # 고장
    OFFLINE = "offline"            # 오프라인
    RESERVED = "reserved"          # 예약됨


# ==================== 기본 정보 테이블 ====================

class StationInfo(Base):
    """
    충전소 (스테이션) 정보
    하나의 충전소에 여러 개의 충전기가 있을 수 있음
    """
    __tablename__ = 'station_info'
    __table_args__ = (
        UniqueConstraint('station_id', name='uq_station_id'),
        Index('idx_station_location', 'longitude', 'latitude'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), unique=True, nullable=False, comment="충전소 고유 ID")
    station_name = Column(String(100), nullable=False, comment="충전소 이름")
    
    # 위치 정보
    address = Column(String(255), nullable=False, comment="충전소 주소")
    longitude = Column(Float, nullable=False, comment="경도 (Longitude)")
    latitude = Column(Float, nullable=False, comment="위도 (Latitude)")
    
    # 운영 정보
    operator_name = Column(String(100), nullable=True, comment="운영사 이름")
    operator_phone = Column(String(20), nullable=True, comment="운영사 전화")
    operator_email = Column(String(100), nullable=True, comment="운영사 이메일")
    
    # 기타 정보
    total_chargers = Column(Integer, default=0, comment="보유 충전기 총 개수")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="등록일시")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")
    
    # 관계
    chargers = relationship("ChargerInfo", back_populates="station", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<StationInfo(station_id={self.station_id}, name={self.station_name})>"


class ChargerInfo(Base):
    """
    충전기 정보
    각 충전기의 기본 사양 및 설정 정보
    """
    __tablename__ = 'charger_info'
    __table_args__ = (
        UniqueConstraint('charger_id', name='uq_charger_id'),
        UniqueConstraint('serial_number', name='uq_serial_number'),
        Index('idx_charger_station', 'station_id'),
        Index('idx_charger_status', 'current_status'),
        Index('idx_charger_type', 'charger_type'),
        Index('idx_charger_location', 'longitude', 'latitude'),
        Index('idx_charger_created', 'created_at'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    charger_id = Column(String(50), unique=True, nullable=False, comment="충전기 고유 ID")
    station_id = Column(String(50), ForeignKey('station_info.station_id', ondelete='CASCADE'), nullable=False, comment="소속 충전소 ID")
    
    # 충전기 기본 정보
    serial_number = Column(String(100), unique=True, nullable=False, comment="충전기 시리얼번호 (기물번호)")
    charger_type = Column(Enum(ChargerTypeEnum), default=ChargerTypeEnum.SLOW, comment="충전기 종류")
    manufacturer = Column(String(100), nullable=True, comment="제조사")
    model_name = Column(String(100), nullable=True, comment="모델명")
    manufacturing_date = Column(Date, nullable=True, comment="제조일자")
    
    # 충전기 용량 (kW)
    rated_power = Column(Float, nullable=False, comment="정격 전력 (kW)")
    max_output = Column(Float, nullable=False, comment="최대 출력 (kW)")
    min_output = Column(Float, nullable=False, comment="최소 출력 (kW)")
    
    # 위치 정보
    location_detail = Column(String(255), nullable=True, comment="충전기 상세 위치")
    longitude = Column(Float, nullable=False, comment="경도")
    latitude = Column(Float, nullable=False, comment="위도")
    floor_level = Column(String(20), nullable=True, comment="층수 (예: 1F, B2F)")
    
    # 충전 방식
    charging_standard = Column(String(50), nullable=True, comment="충전 규격 (AC, DC, etc)")
    connector_type = Column(String(100), nullable=True, comment="커넥터 타입")
    is_multi_connector = Column(Boolean, default=False, comment="다중 커넥터 지원 여부")
    
    # 현재 상태 및 제어
    current_status = Column(Enum(ChargerStatusEnum), default=ChargerStatusEnum.OFFLINE, comment="충전기 현재 상태")
    last_status_update = Column(TIMESTAMP, default=datetime.utcnow, comment="상태 마지막 업데이트")
    
    # 출력 제어
    supports_remote_control = Column(Boolean, default=True, comment="원격 제어 지원 여부")
    power_control_available = Column(Boolean, default=True, comment="출력 제어 가능 여부")
    current_power_limit = Column(Float, nullable=True, comment="현재 전력 제한값 (kW)")
    
    # 요금 정보
    base_fee = Column(Numeric(10, 2), default=Decimal('0'), comment="기본 요금 (₩)")
    unit_price_kwh = Column(Numeric(10, 2), default=Decimal('300'), comment="단위 요금 (₩/kWh)")
    unit_price_time = Column(Numeric(10, 2), default=Decimal('0'), comment="시간당 요금 (₩/분)")
    parking_fee = Column(Numeric(10, 2), default=Decimal('0'), comment="주차료 (₩)")
    
    # 메타 정보
    asset_tag = Column(String(100), nullable=True, comment="자산 태그")
    fixed_asset_no = Column(String(100), nullable=True, comment="고정자산번호")
    installation_date = Column(Date, nullable=True, comment="설치일자")
    warranty_expiry = Column(Date, nullable=True, comment="보증만료일")
    
    # 시스템 정보
    firmware_version = Column(String(50), nullable=True, comment="펌웨어 버전")
    last_maintenance = Column(TIMESTAMP, nullable=True, comment="마지막 정비일시")
    next_maintenance = Column(TIMESTAMP, nullable=True, comment="다음 정비 예정일시")
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="등록일시")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")
    
    # 관계
    station = relationship("StationInfo", back_populates="chargers")
    usage_logs = relationship("ChargerUsageLog", back_populates="charger", cascade="all, delete-orphan")
    power_consumption = relationship("PowerConsumption", back_populates="charger", cascade="all, delete-orphan")
    daily_stats = relationship("DailyChargerStats", back_populates="charger", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChargerInfo(charger_id={self.charger_id}, type={self.charger_type})>"


# ==================== 운영 데이터 테이블 ====================

class ChargerUsageLog(Base):
    """
    충전기 사용 이력
    실제 충전 세션별 기록
    """
    __tablename__ = 'charger_usage_log'
    __table_args__ = (
        UniqueConstraint('transaction_id', name='uq_transaction_id'),
        Index('idx_usage_charger_time', 'charger_id', 'start_time'),
        Index('idx_usage_session_date', 'session_date'),
        Index('idx_usage_start_time', 'start_time'),
        Index('idx_usage_payment_status', 'payment_status'),
    )
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    charger_id = Column(String(50), ForeignKey('charger_info.charger_id', ondelete='CASCADE'), nullable=False, comment="충전기 ID")
    
    # 세션 기본 정보
    transaction_id = Column(String(100), unique=True, nullable=False, comment="거래 고유 ID")
    session_date = Column(Date, nullable=False, comment="충전 날짜")
    
    # 시간 정보
    start_time = Column(TIMESTAMP, nullable=False, comment="충전 시작 시간")
    end_time = Column(TIMESTAMP, nullable=True, comment="충전 종료 시간")
    duration_minutes = Column(Integer, nullable=True, comment="충전 시간 (분)")
    
    # 충전 에너지 정보
    energy_delivered = Column(Numeric(10, 3), default=Decimal('0'), comment="공급 에너지 (kWh)")
    energy_meter_start = Column(Numeric(12, 3), nullable=True, comment="시작 메터값 (kWh)")
    energy_meter_end = Column(Numeric(12, 3), nullable=True, comment="종료 메터값 (kWh)")
    
    # 전력 정보
    average_power = Column(Float, nullable=True, comment="평균 출력 (kW)")
    max_power = Column(Float, nullable=True, comment="최대 출력 (kW)")
    min_power = Column(Float, nullable=True, comment="최소 출력 (kW)")
    
    # 요금 정보
    base_charge = Column(Numeric(10, 2), default=Decimal('0'), comment="기본 요금 (₩)")
    energy_charge = Column(Numeric(10, 2), default=Decimal('0'), comment="전력료 (₩)")
    time_charge = Column(Numeric(10, 2), default=Decimal('0'), comment="시간료 (₩)")
    parking_charge = Column(Numeric(10, 2), default=Decimal('0'), comment="주차료 (₩)")
    total_charge = Column(Numeric(10, 2), default=Decimal('0'), comment="총 요금 (₩)")
    
    # 결제 정보
    payment_method = Column(String(50), nullable=True, comment="결제 수단 (card, cash, app, etc)")
    payment_status = Column(String(20), default='pending', comment="결제 상태 (pending, completed, failed)")
    payment_date = Column(TIMESTAMP, nullable=True, comment="결제 일시")
    
    # 사용자 정보 (익명 처리)
    vehicle_type = Column(String(50), nullable=True, comment="차량 유형")
    user_id_hash = Column(String(100), nullable=True, comment="사용자 ID (해시)")
    
    # 상태 정보
    status = Column(String(20), default='completed', comment="충전 상태")
    error_code = Column(String(50), nullable=True, comment="오류 코드 (있을 경우)")
    error_message = Column(Text, nullable=True, comment="오류 메시지")
    
    # 추가 데이터
    extra_data = Column(JSONB, nullable=True, comment="추가 데이터 (JSON)")
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="기록 생성일시")
    
    charger = relationship("ChargerInfo", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<ChargerUsageLog(transaction_id={self.transaction_id}, energy={self.energy_delivered}kWh)>"


class PowerConsumption(Base):
    """
    입력 전력 및 누적 전력량 정보
    5분 또는 15분 단위의 실시간 전력 데이터
    """
    __tablename__ = 'power_consumption'
    __table_args__ = (
        Index('idx_power_charger_time', 'charger_id', 'measurement_time'),
        Index('idx_power_measurement_time', 'measurement_time'),
        Index('idx_power_date', 'measurement_date'),
        Index('idx_power_hour', 'measurement_date', 'hour'),
    )
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    charger_id = Column(String(50), ForeignKey('charger_info.charger_id', ondelete='CASCADE'), nullable=False, comment="충전기 ID")
    
    # 시간 정보
    measurement_time = Column(TIMESTAMP, nullable=False, comment="측정 시간")
    measurement_date = Column(Date, nullable=False, comment="측정 날짜")
    hour = Column(Integer, nullable=False, comment="시간 (0-23)")
    
    # 순간 전력
    input_power = Column(Float, nullable=False, comment="입력 전력 (kW)")
    
    # 누적 데이터
    cumulative_energy = Column(Numeric(12, 3), nullable=False, comment="누적 에너지 (kWh)")
    daily_cumulative = Column(Numeric(10, 3), nullable=False, comment="일일 누적 에너지 (kWh)")
    
    # 전기계약 정보
    power_factor = Column(Float, nullable=True, comment="역률 (Power Factor)")
    voltage = Column(Float, nullable=True, comment="전압 (V)")
    current = Column(Float, nullable=True, comment="전류 (A)")
    
    # 상태
    is_charging = Column(Boolean, default=False, comment="충전 중 여부")
    charger_status = Column(String(50), nullable=True, comment="충전기 상태")
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="기록 생성일시")
    
    charger = relationship("ChargerInfo", back_populates="power_consumption")
    
    def __repr__(self):
        return f"<PowerConsumption(charger_id={self.charger_id}, power={self.input_power}kW)>"


# ==================== 통계 및 분석 테이블 ====================

class DailyChargerStats(Base):
    """
    충전기 일일 통계
    매일 자정에 갱신
    """
    __tablename__ = 'daily_charger_stats'
    __table_args__ = (
        UniqueConstraint('charger_id', 'stats_date', name='uq_charger_daily_stats'),
        Index('idx_daily_charger_date', 'charger_id', 'stats_date'),
        Index('idx_daily_stats_date', 'stats_date'),
    )
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    charger_id = Column(String(50), ForeignKey('charger_info.charger_id', ondelete='CASCADE'), nullable=False, comment="충전기 ID")
    stats_date = Column(Date, nullable=False, comment="통계 날짜")
    
    # 사용량 통계
    num_sessions = Column(Integer, default=0, comment="충전 세션 수")
    total_energy = Column(Numeric(10, 3), default=Decimal('0'), comment="총 공급 에너지 (kWh)")
    total_duration_minutes = Column(Integer, default=0, comment="총 충전 시간 (분)")
    
    # 요금 통계
    total_revenue = Column(Numeric(12, 2), default=Decimal('0'), comment="총 매출 (₩)")
    avg_charge_per_session = Column(Numeric(10, 2), default=Decimal('0'), comment="세션당 평균 요금 (₩)")
    
    # 시간대별 통계 (JSONB - PostgreSQL 최적화)
    hourly_energy = Column(JSONB, nullable=True, comment="시간대별 에너지 (JSONB)")
    hourly_sessions = Column(JSONB, nullable=True, comment="시간대별 세션 수 (JSONB)")
    hourly_revenue = Column(JSONB, nullable=True, comment="시간대별 매출 (JSONB)")
    
    # 운영 통계
    uptime_percentage = Column(Float, default=100.0, comment="가용률 (%)")
    fault_count = Column(Integer, default=0, comment="고장 발생 횟수")
    maintenance_required = Column(Boolean, default=False, comment="정비 필요 여부")
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="기록 생성일시")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")
    
    charger = relationship("ChargerInfo", back_populates="daily_stats")
    
    def __repr__(self):
        return f"<DailyChargerStats(charger_id={self.charger_id}, date={self.stats_date})>"


class HourlyChargerStats(Base):
    """
    충전기 시간별 통계
    매시간 갱신
    """
    __tablename__ = 'hourly_charger_stats'
    __table_args__ = (
        UniqueConstraint('charger_id', 'stats_hour', name='uq_charger_hourly_stats'),
        Index('idx_hourly_charger_hour', 'charger_id', 'stats_hour'),
        Index('idx_hourly_stats_hour', 'stats_hour'),
    )
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    charger_id = Column(String(50), ForeignKey('charger_info.charger_id', ondelete='CASCADE'), nullable=False, comment="충전기 ID")
    stats_hour = Column(TIMESTAMP, nullable=False, comment="통계 시간 (HH:00:00)")
    
    # 사용량 통계
    num_sessions = Column(Integer, default=0, comment="충전 세션 수")
    total_energy = Column(Numeric(10, 3), default=Decimal('0'), comment="공급 에너지 (kWh)")
    total_duration_minutes = Column(Integer, default=0, comment="충전 시간 (분)")
    
    # 요금 통계
    total_revenue = Column(Numeric(12, 2), default=Decimal('0'), comment="시간 매출 (₩)")
    
    # 전력 통계
    avg_power = Column(Float, nullable=True, comment="평균 출력 (kW)")
    max_power = Column(Float, nullable=True, comment="최대 출력 (kW)")
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="기록 생성일시")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")
    
    def __repr__(self):
        return f"<HourlyChargerStats(charger_id={self.charger_id}, hour={self.stats_hour})>"


class StationDailyStats(Base):
    """
    충전소 일일 통계
    """
    __tablename__ = 'station_daily_stats'
    __table_args__ = (
        UniqueConstraint('station_id', 'stats_date', name='uq_station_daily_stats'),
        Index('idx_station_daily_date', 'station_id', 'stats_date'),
        Index('idx_station_stats_date', 'stats_date'),
    )
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    station_id = Column(String(50), nullable=False, comment="충전소 ID")
    stats_date = Column(Date, nullable=False, comment="통계 날짜")
    
    # 통계
    num_sessions = Column(Integer, default=0, comment="충전 세션 수")
    total_energy = Column(Numeric(10, 3), default=Decimal('0'), comment="총 공급 에너지 (kWh)")
    total_revenue = Column(Numeric(12, 2), default=Decimal('0'), comment="총 매출 (₩)")
    
    # 충전기 상태
    num_available = Column(Integer, default=0, comment="사용 가능 충전기 수")
    num_in_use = Column(Integer, default=0, comment="사용 중 충전기 수")
    num_fault = Column(Integer, default=0, comment="고장 충전기 수")
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="기록 생성일시")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일시")
    
    def __repr__(self):
        return f"<StationDailyStats(station_id={self.station_id}, date={self.stats_date})>"


# ==================== 데이터베이스 관리 클래스 ====================

class DatabaseManager:
    """데이터베이스 연결 및 세션 관리"""
    
    def __init__(self, database_url: str = None):
        """
        데이터베이스 초기화
        
        Args:
            database_url: 데이터베이스 연결 문자열
                PostgreSQL (권장): "postgresql://user:password@localhost:5432/charger_db"
                PostgreSQL (psycopg2): "postgresql+psycopg2://user:password@localhost/charger_db"
                SQLite: "sqlite:///./charger_management.db"
        """
        if database_url is None:
            # 환경변수에서 읽기, 없으면 기본값 사용
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://charger_user:charger_password@localhost:5432/charger_db'
            )
        
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self, echo: bool = False):
        """데이터베이스 엔진 및 테이블 생성"""
        # PostgreSQL 최적화 옵션
        connect_args = {}
        if 'postgresql' in self.database_url:
            connect_args = {
                'connect_timeout': 10,
                'application_name': 'charger_management'
            }
        
        self.engine = create_engine(
            self.database_url,
            echo=echo,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args=connect_args
        )
        
        # 모든 테이블 생성
        Base.metadata.create_all(bind=self.engine)
        
        # 세션 팩토리 생성
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        print(f"✅ 데이터베이스 초기화 완료: {self._mask_url()}")
    
    def _mask_url(self):
        """URL에서 비밀번호 마스킹"""
        url = self.database_url
        if '@' in url:
            prefix = url.split('@')[0]
            suffix = url.split('@')[1]
            if ':' in prefix:
                user_part = prefix.split('://')[1].split(':')[0]
                return f"postgresql://{user_part}:***@{suffix}"
        return url
    
    def get_session(self):
        """세션 반환"""
        if self.SessionLocal is None:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다. initialize() 메서드를 먼저 호출하세요.")
        return self.SessionLocal()
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()


# ==================== 기본 설정 ====================

# PostgreSQL 기본 데이터베이스 URL
DEFAULT_DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://charger_user:charger_password@localhost:5432/charger_db'
)

# 데이터베이스 관리자 인스턴스
db_manager = DatabaseManager(DEFAULT_DATABASE_URL)


if __name__ == "__main__":
    # 테스트: 데이터베이스 초기화
    db_manager.initialize()
    print("\n✅ PostgreSQL 데이터베이스 스키마가 생성되었습니다!")
    print("\n📊 생성된 테이블:")
    for table in Base.metadata.tables:
        print(f"  - {table}")
    print("\n💡 팁: 다음과 같이 환경변수를 설정하여 연결 문자열을 변경할 수 있습니다:")
    print("   export DATABASE_URL='postgresql://user:password@host:5432/dbname'")
