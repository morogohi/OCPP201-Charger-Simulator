"""
OCPP 2.0.1 데이터 모델 정의
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# Enums
class BootReasonEnum(str, Enum):
    """부팅 이유"""
    APPLICATION_RESET = "ApplicationReset"
    FIRMWARE_UPDATE = "FirmwareUpdate"
    LOCAL_RESET = "LocalReset"
    POWER_UP = "PowerUp"
    WATCHDOG_RESET = "WatchdogReset"
    SCHEDULED_RESET = "ScheduledReset"
    TRIGGERED_RESET = "TriggeredReset"
    UNKNOWN = "Unknown"


class GenericStatusEnum(str, Enum):
    """일반 상태"""
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    FAILED = "Failed"


class ConnectorStatusEnum(str, Enum):
    """커넥터 상태"""
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"


class ChargePointStatusEnum(str, Enum):
    """충전 포인트 상태"""
    AVAILABLE = "Available"
    PREPARING = "Preparing"
    CHARGING = "Charging"
    OCCUPIED = "Occupied"
    RESERVED = "Reserved"
    UNAVAILABLE = "Unavailable"
    FAULTED = "Faulted"


class TransactionEventEnum(str, Enum):
    """트랜잭션 이벤트"""
    STARTED = "Started"
    UPDATED = "Updated"
    ENDED = "Ended"


class ReasonEnum(str, Enum):
    """종료 이유"""
    DE_AUTHORIZED = "DeAuthorized"
    EMERGENCY_STOP = "EmergencyStop"
    ENERGY_LIMIT_REACHED = "EnergyLimitReached"
    GROUNDING_FAILURE = "GroundingFailure"
    IMMEDIATE_RESET = "ImmediateReset"
    LOCAL_OUT_OF_CREDITS = "LocalOutOfCredits"
    LOCAL_RESET = "LocalReset"
    LOCK_FAILURE = "LockFailure"
    NO_ENERGY_SOURCE = "NoEnergySource"
    OTHER = "Other"
    OVERCURRENT_FAULT = "OvercurrentFault"
    POWER_LOSS = "PowerLoss"
    POWER_QUALITY = "PowerQuality"
    PRESENT_VOLTAGE_LOW = "PresentVoltageLow"
    REMOTE_OFF = "RemoteOff"
    REMOTE_RESET = "RemoteReset"
    SESSION_ENDED = "SessionEnded"
    SOC_LIMIT_REACHED = "SocLimitReached"
    STOPPED_BY_EV = "StoppedByEV"
    STOPPED_BY_EVSE = "StoppedByEVSE"
    TIME_LIMIT_REACHED = "TimeLimitReached"
    TIMEOUT = "Timeout"


# 기본 모델
class ChargingProfileModel(BaseModel):
    """충전 프로필"""
    chargingProfileId: int
    stackLevel: int
    chargingProfilePurpose: str
    chargingProfileKind: str


class ConnectorModel(BaseModel):
    """커넥터"""
    connectorId: int
    connectorStatus: ConnectorStatusEnum = ConnectorStatusEnum.AVAILABLE


class EVSEModel(BaseModel):
    """EVSE (Electric Vehicle Supply Equipment)"""
    id: int
    connectorId: Optional[int] = None
    connectors: List[ConnectorModel] = []


# 요청/응답 모델
class BootNotificationRequest(BaseModel):
    """부팅 알림 요청"""
    reason: BootReasonEnum
    chargingStation: Dict[str, Any]


class BootNotificationResponse(BaseModel):
    """부팅 알림 응답"""
    currentTime: datetime
    interval: int
    status: GenericStatusEnum


class HeartbeatRequest(BaseModel):
    """하트비트 요청"""
    pass


class HeartbeatResponse(BaseModel):
    """하트비트 응답"""
    currentTime: datetime


class MeterValue(BaseModel):
    """미터 값"""
    timestamp: datetime
    sampledValue: List[Dict[str, Any]] = []


class TransactionEventRequest(BaseModel):
    """트랜잭션 이벤트 요청"""
    eventType: TransactionEventEnum
    timestamp: datetime
    transactionInfo: Optional[Dict[str, Any]] = None
    meterValue: Optional[List[MeterValue]] = None
    offline: bool = False
    numberOfPhasesUsed: Optional[int] = None
    cableMaxCurrent: Optional[float] = None
    reservationId: Optional[int] = None


class TransactionEventResponse(BaseModel):
    """트랜잭션 이벤트 응답"""
    totalCost: Optional[float] = None
    chargingPriority: Optional[int] = None
    idTokenInfo: Optional[Dict[str, Any]] = None


class StatusNotificationRequest(BaseModel):
    """상태 알림 요청"""
    timestamp: datetime
    connectorStatus: ConnectorStatusEnum
    evseId: int
    connectorId: int


class StatusNotificationResponse(BaseModel):
    """상태 알림 응답"""
    pass


class AuthorizeRequest(BaseModel):
    """인증 요청"""
    idToken: Dict[str, Any]
    certificate: Optional[str] = None
    iso15118CertificateHashData: Optional[List[Dict[str, Any]]] = None


class AuthorizeResponse(BaseModel):
    """인증 응답"""
    idTokenInfo: Dict[str, Any]
    certificateStatus: Optional[str] = None
