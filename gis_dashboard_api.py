"""
GIS 기반 충전기 모니터링 대시보드 API
FastAPI 기반 REST API 제공
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
import os

from database.models import (
    db_manager, ChargerTypeEnum, ChargerStatusEnum
)
from database.services import (
    StationService, ChargerService, UsageLogService,
    PowerConsumptionService, StatisticsService
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="EV Charger Management & GIS Dashboard API",
    description="제주 지역 EV 충전기 관리 및 GIS 기반 대시보드 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic 모델 ====================

class StationCreate(BaseModel):
    """충전소 생성 요청"""
    station_id: str
    station_name: str
    address: str
    longitude: float
    latitude: float
    operator_name: Optional[str] = None
    operator_phone: Optional[str] = None
    operator_email: Optional[str] = None


class StationUpdate(BaseModel):
    """충전소 수정 요청"""
    station_name: Optional[str] = None
    address: Optional[str] = None
    operator_name: Optional[str] = None
    operator_phone: Optional[str] = None
    operator_email: Optional[str] = None


class StationResponse(BaseModel):
    """충전소 응답"""
    id: int
    station_id: str
    station_name: str
    address: str
    longitude: float
    latitude: float
    operator_name: Optional[str]
    operator_phone: Optional[str]
    operator_email: Optional[str]
    total_chargers: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ChargerCreate(BaseModel):
    """충전기 생성 요청"""
    charger_id: str
    station_id: str
    serial_number: str
    charger_type: ChargerTypeEnum
    rated_power: float
    max_output: float
    min_output: float
    longitude: float
    latitude: float
    location_detail: Optional[str] = None
    manufacturer: Optional[str] = None
    model_name: Optional[str] = None
    charging_standard: Optional[str] = None
    connector_type: Optional[str] = None
    unit_price_kwh: Optional[Decimal] = None
    base_fee: Optional[Decimal] = None


class ChargerStatusUpdate(BaseModel):
    """충전기 상태 업데이트"""
    status: ChargerStatusEnum


class ChargerResponse(BaseModel):
    """충전기 응답"""
    id: int
    charger_id: str
    station_id: str
    serial_number: str
    charger_type: ChargerTypeEnum
    rated_power: float
    max_output: float
    min_output: float
    longitude: float
    latitude: float
    location_detail: Optional[str]
    current_status: ChargerStatusEnum
    current_power_limit: Optional[float]
    unit_price_kwh: Decimal
    base_fee: Decimal
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class GeoChargerResponse(BaseModel):
    """GIS 맵 표시용 충전기 응답"""
    charger_id: str
    station_id: str
    station_name: str
    address: str
    longitude: float
    latitude: float
    charger_type: ChargerTypeEnum
    current_status: ChargerStatusEnum
    rated_power: float
    unit_price_kwh: Decimal
    
    model_config = {"from_attributes": True}


class ChargerDashboard(BaseModel):
    """충전기 대시보드 정보"""
    charger_id: str
    station_id: str
    current_status: ChargerStatusEnum
    rated_power: float
    location: Dict[str, float]  # {longitude, latitude}
    usage_today: Dict[str, Any]  # 일일 통계
    hourly_stats: Dict[int, Dict[str, float]]  # 시간대별 통계


class UsageLogCreate(BaseModel):
    """사용 이력 생성 요청"""
    charger_id: str
    transaction_id: str
    session_date: date
    start_time: datetime
    energy_delivered: Optional[float] = None
    total_charge: Optional[Decimal] = None


class DailyRevenueResponse(BaseModel):
    """일일 매출 응답"""
    charger_id: str
    date: date
    num_sessions: int
    total_revenue: Decimal
    total_energy: Decimal
    avg_charge: Decimal


class StationSummaryResponse(BaseModel):
    """충전소 통계 요약"""
    station_id: str
    num_chargers: int
    available_chargers: int
    in_use_chargers: int
    fault_chargers: int
    total_revenue_today: Decimal
    total_energy_today: Decimal


# ==================== 의존성 ====================

def get_db():
    """데이터베이스 세션 반환"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


# ==================== 헬스체크 ====================

@app.get("/health")
async def health_check():
    """API 헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "EV Charger Management & GIS Dashboard API"
    }


# ==================== 충전소 엔드포인트 ====================

@app.post("/stations", response_model=StationResponse)
async def create_station(station: StationCreate, db=Depends(get_db)):
    """충전소 등록"""
    try:
        result = StationService.create_station(
            db,
            station.station_id,
            station.station_name,
            station.address,
            station.longitude,
            station.latitude,
            station.operator_name,
            station.operator_phone,
            station.operator_email
        )
        return result
    except Exception as e:
        logger.error(f"충전소 등록 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/stations/{station_id}", response_model=StationResponse)
async def get_station(station_id: str, db=Depends(get_db)):
    """충전소 조회"""
    station = StationService.get_station(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="충전소를 찾을 수 없습니다")
    return station


@app.get("/stations", response_model=List[StationResponse])
async def list_stations(db=Depends(get_db)):
    """모든 충전소 조회"""
    return StationService.get_all_stations(db)


@app.put("/stations/{station_id}", response_model=StationResponse)
async def update_station(station_id: str, update: StationUpdate, db=Depends(get_db)):
    """충전소 정보 수정"""
    result = StationService.update_station(db, station_id, **update.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="충전소를 찾을 수 없습니다")
    return result


# ==================== 충전기 엔드포인트 ====================

@app.post("/chargers", response_model=ChargerResponse)
async def create_charger(charger: ChargerCreate, db=Depends(get_db)):
    """충전기 등록"""
    try:
        result = ChargerService.create_charger(
            db,
            charger.charger_id,
            charger.station_id,
            charger.serial_number,
            charger.charger_type,
            charger.rated_power,
            charger.max_output,
            charger.min_output,
            charger.longitude,
            charger.latitude,
            location_detail=charger.location_detail,
            manufacturer=charger.manufacturer,
            model_name=charger.model_name,
            charging_standard=charger.charging_standard,
            connector_type=charger.connector_type,
            unit_price_kwh=charger.unit_price_kwh,
            base_fee=charger.base_fee
        )
        
        # 충전소의 총 충전기 수 업데이트
        station = StationService.get_station(db, charger.station_id)
        if station:
            station.total_chargers = len(ChargerService.get_chargers_by_station(db, charger.station_id))
            db.commit()
        
        return result
    except Exception as e:
        logger.error(f"충전기 등록 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/chargers/{charger_id}", response_model=ChargerResponse)
async def get_charger(charger_id: str, db=Depends(get_db)):
    """충전기 조회"""
    charger = ChargerService.get_charger(db, charger_id)
    if not charger:
        raise HTTPException(status_code=404, detail="충전기를 찾을 수 없습니다")
    return charger


@app.get("/stations/{station_id}/chargers", response_model=List[ChargerResponse])
async def list_chargers_by_station(station_id: str, db=Depends(get_db)):
    """충전소별 충전기 목록 조회"""
    return ChargerService.get_chargers_by_station(db, station_id)


@app.get("/chargers/status/{status}", response_model=List[ChargerResponse])
async def list_chargers_by_status(status: ChargerStatusEnum, db=Depends(get_db)):
    """상태별 충전기 목록 조회"""
    return ChargerService.get_chargers_by_status(db, status)


@app.patch("/chargers/{charger_id}/status")
async def update_charger_status(charger_id: str, update: ChargerStatusUpdate, db=Depends(get_db)):
    """충전기 상태 업데이트"""
    result = ChargerService.update_charger_status(db, charger_id, update.status)
    if not result:
        raise HTTPException(status_code=404, detail="충전기를 찾을 수 없습니다")
    return {"charger_id": charger_id, "status": update.status}


# ==================== GIS 맵 엔드포인트 ====================

@app.get("/geo/chargers", response_model=List[GeoChargerResponse])
async def get_geo_chargers(
    station_id: Optional[str] = Query(None, description="충전소 필터"),
    status: Optional[ChargerStatusEnum] = Query(None, description="상태 필터"),
    charger_type: Optional[ChargerTypeEnum] = Query(None, description="종류 필터"),
    db=Depends(get_db)
):
    """GIS 맵용 충전기 위치 정보 조회"""
    if station_id:
        chargers = ChargerService.get_chargers_by_station(db, station_id)
    elif status:
        chargers = ChargerService.get_chargers_by_status(db, status)
    elif charger_type:
        chargers = ChargerService.get_chargers_by_type(db, charger_type)
    else:
        from database.models import ChargerInfo
        chargers = db.query(ChargerInfo).all()
    
    # 충전소 정보 추가
    result = []
    for charger in chargers:
        station = StationService.get_station(db, charger.station_id)
        result.append({
            "charger_id": charger.charger_id,
            "station_id": charger.station_id,
            "station_name": station.station_name if station else "Unknown",
            "address": station.address if station else "",
            "longitude": charger.longitude,
            "latitude": charger.latitude,
            "charger_type": charger.charger_type,
            "current_status": charger.current_status,
            "rated_power": charger.rated_power,
            "unit_price_kwh": charger.unit_price_kwh
        })
    
    return result


@app.get("/geo/heatmap")
async def get_heatmap_data(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db=Depends(get_db)
):
    """충전기 이용량 히트맵 데이터"""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    from database.models import ChargerInfo, DailyChargerStats
    chargers = db.query(ChargerInfo).all()
    
    heatmap_data = []
    for charger in chargers:
        stats = db.query(DailyChargerStats).filter(
            (DailyChargerStats.charger_id == charger.charger_id) &
            (DailyChargerStats.stats_date >= start_date) &
            (DailyChargerStats.stats_date <= end_date)
        ).all()
        
        total_revenue = sum(s.total_revenue or 0 for s in stats)
        total_energy = sum(s.total_energy or 0 for s in stats)
        
        if total_revenue > 0 or total_energy > 0:
            heatmap_data.append({
                "longitude": charger.longitude,
                "latitude": charger.latitude,
                "charger_id": charger.charger_id,
                "intensity": float(total_revenue),
                "energy": float(total_energy),
                "revenue": float(total_revenue)
            })
    
    return {
        "period": f"{start_date} ~ {end_date}",
        "data": heatmap_data
    }


# ==================== 통계 엔드포인트 ====================

@app.get("/statistics/charger/{charger_id}/daily")
async def get_charger_daily_stats(
    charger_id: str,
    target_date: date = Query(None),
    db=Depends(get_db)
):
    """충전기 일일 통계"""
    if not target_date:
        target_date = date.today()
    
    result = UsageLogService.get_daily_revenue(db, charger_id, target_date)
    return result


@app.get("/statistics/charger/{charger_id}/period")
async def get_charger_period_stats(
    charger_id: str,
    start_date: date,
    end_date: date,
    db=Depends(get_db)
):
    """충전기 기간별 통계"""
    result = StatisticsService.get_charger_summary(db, charger_id, start_date, end_date)
    return result


@app.get("/statistics/station/{station_id}")
async def get_station_summary(
    station_id: str,
    start_date: date = None,
    end_date: date = None,
    db=Depends(get_db)
):
    """충전소 통계 요약"""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    result = StatisticsService.get_station_summary(db, station_id, start_date, end_date)
    return result


@app.get("/statistics/dashboard")
async def get_dashboard_stats(
    target_date: date = None,
    db=Depends(get_db)
):
    """전체 대시보드 통계"""
    if not target_date:
        target_date = date.today()
    
    from database.models import ChargerInfo, StationInfo, DailyChargerStats, ChargerUsageLog
    from sqlalchemy import func
    
    # 전체 충전소 및 충전기 수
    stations = db.query(StationInfo).all()
    chargers = db.query(ChargerInfo).all()
    
    # 상태별 충전기 수
    available = len(ChargerService.get_chargers_by_status(db, ChargerStatusEnum.AVAILABLE))
    in_use = len(ChargerService.get_chargers_by_status(db, ChargerStatusEnum.IN_USE))
    fault = len(ChargerService.get_chargers_by_status(db, ChargerStatusEnum.FAULT))
    
    # 오늘의 총 매출 및 에너지
    today_logs = db.query(ChargerUsageLog).filter(
        (ChargerUsageLog.session_date == target_date) &
        (ChargerUsageLog.payment_status == 'completed')
    ).all()
    
    total_revenue = sum(log.total_charge or 0 for log in today_logs)
    total_energy = sum(log.energy_delivered or 0 for log in today_logs)
    
    return {
        "date": target_date,
        "total_stations": len(stations),
        "total_chargers": len(chargers),
        "charger_status": {
            "available": available,
            "in_use": in_use,
            "fault": fault,
            "offline": len(chargers) - available - in_use - fault
        },
        "daily_stats": {
            "sessions": len(today_logs),
            "total_revenue": float(total_revenue),
            "total_energy": float(total_energy),
            "avg_charge": float(total_revenue / len(today_logs)) if today_logs else 0
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # 데이터베이스 초기화
    db_manager.initialize()
    
    # 서버 실행
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info"
    )
