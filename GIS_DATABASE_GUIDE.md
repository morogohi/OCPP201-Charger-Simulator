# 제주 EV 충전기 관리 & GIS 대시보드 시스템

완전한 제주 지역 EV 충전기 데이터 관리 및 GIS 기반 모니터링 시스템입니다.

## 📋 목차

- [시스템 개요](#시스템-개요)
- [데이터베이스 구조](#데이터베이스-구조)
- [설치 및 실행](#설치-및-실행)
- [API 문서](#api-문서)
- [대시보드 사용 방법](#대시보드-사용-방법)
- [데이터 항목](#데이터-항목)

---

## 시스템 개요

### 기능

- **충전소 관리**: 제주 지역 EV 충전소 정보 등록 및 관리
- **충전기 관리**: 충전기 기본 정보, 상태, 요금 관리
- **GIS 맵**: 지도 기반 충전기 위치 시각화
- **실시간 모니터링**: 충전기 상태, 사용률 실시간 추적
- **통계 분석**: 시간별, 일별, 기간별 통계
- **요금 관리**: 충전기별 요금 설정 및 매출 추적
- **전력 모니터링**: 입력 전력, 누적 전력량 실시간 추적
- **데이터 내보내기**: JSON 형식 데이터 다운로드

### 기술 스택

| 항목 | 기술 |
|------|------|
| **백엔드** | FastAPI, SQLAlchemy, Python |
| **데이터베이스** | SQLite / PostgreSQL |
| **프론트엔드** | HTML5, Bootstrap 5, Leaflet.js |
| **차트** | Chart.js |
| **지도** | OpenStreetMap, Leaflet |

---

## 데이터베이스 구조

### 테이블 구성

#### 1. **station_info** (충전소 정보)
충전소의 기본 정보를 저장합니다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| station_id | String(50) | 충전소 고유 ID |
| station_name | String(100) | 충전소 이름 |
| address | String(255) | 주소 |
| longitude | Float | 경도 |
| latitude | Float | 위도 |
| operator_name | String(100) | 운영사 이름 |
| operator_phone | String(20) | 운영사 전화 |
| operator_email | String(100) | 운영사 이메일 |
| total_chargers | Integer | 보유 충전기 수 |

#### 2. **charger_info** (충전기 정보)
각 충전기의 기본 사양과 설정 정보입니다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| charger_id | String(50) | 충전기 고유 ID |
| station_id | String(50) | 소속 충전소 ID |
| serial_number | String(100) | 시리얼번호 (기물번호) |
| charger_type | Enum | 종류 (fast/slow/ultra_fast) |
| rated_power | Float | 정격 전력 (kW) |
| max_output | Float | 최대 출력 (kW) |
| min_output | Float | 최소 출력 (kW) |
| longitude | Float | 경도 |
| latitude | Float | 위도 |
| current_status | Enum | 현재 상태 (available/in_use/fault/offline) |
| current_power_limit | Float | 현재 전력 제한값 (kW) |
| base_fee | Decimal | 기본 요금 (₩) |
| unit_price_kwh | Decimal | 단위 요금 (₩/kWh) |
| supports_remote_control | Boolean | 원격 제어 지원 여부 |
| power_control_available | Boolean | 출력 제어 가능 여부 |
| manufacturing_date | Date | 제조일자 |
| installation_date | Date | 설치일자 |
| last_maintenance | DateTime | 마지막 정비일시 |
| next_maintenance | DateTime | 다음 정비 예정일시 |

#### 3. **charger_usage_log** (사용 이력)
실제 충전 세션별 기록입니다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| transaction_id | String(100) | 거래 고유 ID |
| charger_id | String(50) | 충전기 ID |
| session_date | Date | 충전 날짜 |
| start_time | DateTime | 충전 시작 시간 |
| end_time | DateTime | 충전 종료 시간 |
| duration_minutes | Integer | 충전 시간 (분) |
| energy_delivered | Decimal(10,3) | 공급 에너지 (kWh) |
| base_charge | Decimal(10,2) | 기본 요금 (₩) |
| energy_charge | Decimal(10,2) | 전력료 (₩) |
| time_charge | Decimal(10,2) | 시간료 (₩) |
| total_charge | Decimal(10,2) | 총 요금 (₩) |
| payment_method | String(50) | 결제 수단 |
| payment_status | String(20) | 결제 상태 |
| average_power | Float | 평균 출력 (kW) |
| max_power | Float | 최대 출력 (kW) |

#### 4. **power_consumption** (전력 사용량)
5분 또는 15분 단위의 실시간 전력 데이터입니다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| charger_id | String(50) | 충전기 ID |
| measurement_time | DateTime | 측정 시간 |
| measurement_date | Date | 측정 날짜 |
| hour | Integer | 시간 (0-23) |
| input_power | Float | 입력 전력 (kW) |
| cumulative_energy | Decimal(12,3) | 누적 에너지 (kWh) |
| daily_cumulative | Decimal(10,3) | 일일 누적 에너지 (kWh) |
| is_charging | Boolean | 충전 중 여부 |
| power_factor | Float | 역률 |
| voltage | Float | 전압 (V) |
| current | Float | 전류 (A) |

#### 5. **daily_charger_stats** (일일 통계)
충전기 일일 통계입니다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| charger_id | String(50) | 충전기 ID |
| stats_date | Date | 통계 날짜 |
| num_sessions | Integer | 충전 세션 수 |
| total_energy | Decimal(10,3) | 총 공급 에너지 (kWh) |
| total_duration_minutes | Integer | 총 충전 시간 (분) |
| total_revenue | Decimal(12,2) | 총 매출 (₩) |
| hourly_energy | JSON | 시간대별 에너지 |
| hourly_sessions | JSON | 시간대별 세션 수 |
| hourly_revenue | JSON | 시간대별 매출 |
| uptime_percentage | Float | 가용률 (%) |

#### 6. **hourly_charger_stats** (시간별 통계)
충전기 시간별 통계입니다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| charger_id | String(50) | 충전기 ID |
| stats_hour | DateTime | 통계 시간 |
| num_sessions | Integer | 세션 수 |
| total_energy | Decimal(10,3) | 에너지 (kWh) |
| total_revenue | Decimal(12,2) | 매출 (₩) |

#### 7. **station_daily_stats** (충전소 일일 통계)
충전소 일일 통계입니다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| station_id | String(50) | 충전소 ID |
| stats_date | Date | 통계 날짜 |
| num_sessions | Integer | 총 세션 수 |
| total_energy | Decimal(10,3) | 총 에너지 (kWh) |
| total_revenue | Decimal(12,2) | 총 매출 (₩) |
| num_available | Integer | 사용 가능 충전기 수 |
| num_in_use | Integer | 사용 중 충전기 수 |
| num_fault | Integer | 고장 충전기 수 |

---

## 설치 및 실행

### 1단계: 필수 패키지 설치

```bash
pip install fastapi uvicorn sqlalchemy pydantic python-dateutil
```

### 2단계: 데이터베이스 초기화 및 샘플 데이터 생성

```bash
python init_jeju_chargers.py
```

출력:
```
📍 충전소 등록 중...
  ✅ 제주시청 충전소 등록됨
  ✅ 서귀포 해양관광 충전소 등록됨
  ...

🔌 충전기 등록 중...
  ✅ JEJU_CHG_001_01 등록됨
  ...

📊 샘플 사용 이력 생성 중...
  ✅ 2026-01-19 데이터 생성 완료
  ...

⚡ 전력 사용량 데이터 생성 중...
  ✅ 전력 사용량 데이터 생성 완료

✅ 데이터베이스 초기화 완료!
```

### 3단계: API 서버 실행

```bash
python gis_dashboard_api.py
```

출력:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4단계: 대시보드 접속

- **API 문서**: http://localhost:8000/docs
- **웹 대시보드**: `gis_dashboard.html`을 웹브라우저로 열기

---

## API 문서

### 충전소 API

#### 충전소 등록
```http
POST /stations
Content-Type: application/json

{
  "station_id": "JEJU_STA_001",
  "station_name": "제주시청 충전소",
  "address": "제주시 문평로 61",
  "longitude": 126.5307,
  "latitude": 33.4857,
  "operator_name": "제주 EV 충전 네트워크",
  "operator_phone": "064-741-2500",
  "operator_email": "jeju@evcharger.kr"
}
```

#### 충전소 조회
```http
GET /stations/{station_id}
```

#### 모든 충전소 조회
```http
GET /stations
```

#### 충전소 정보 수정
```http
PUT /stations/{station_id}
Content-Type: application/json

{
  "station_name": "새로운 이름",
  "operator_name": "새로운 운영사"
}
```

---

### 충전기 API

#### 충전기 등록
```http
POST /chargers
Content-Type: application/json

{
  "charger_id": "JEJU_CHG_001_01",
  "station_id": "JEJU_STA_001",
  "serial_number": "SN-2024-0001",
  "charger_type": "fast",
  "rated_power": 50.0,
  "max_output": 55.0,
  "min_output": 10.0,
  "longitude": 126.5310,
  "latitude": 33.4860,
  "unit_price_kwh": "300",
  "base_fee": "1000"
}
```

#### 충전기 조회
```http
GET /chargers/{charger_id}
```

#### 충전소별 충전기 목록
```http
GET /stations/{station_id}/chargers
```

#### 상태별 충전기 목록
```http
GET /chargers/status/{status}
```

상태 값: `available`, `in_use`, `fault`, `offline`

#### 충전기 상태 업데이트
```http
PATCH /chargers/{charger_id}/status
Content-Type: application/json

{
  "status": "in_use"
}
```

---

### GIS 맵 API

#### 지도용 충전기 데이터
```http
GET /geo/chargers?station_id=JEJU_STA_001&status=available&charger_type=fast
```

응답:
```json
[
  {
    "charger_id": "JEJU_CHG_001_01",
    "station_id": "JEJU_STA_001",
    "station_name": "제주시청 충전소",
    "address": "제주시 문평로 61",
    "longitude": 126.5310,
    "latitude": 33.4860,
    "charger_type": "fast",
    "current_status": "available",
    "rated_power": 50.0,
    "unit_price_kwh": "300"
  }
]
```

#### 히트맵 데이터
```http
GET /geo/heatmap?start_date=2026-01-01&end_date=2026-01-31
```

---

### 통계 API

#### 일일 통계
```http
GET /statistics/charger/{charger_id}/daily?target_date=2026-01-19
```

응답:
```json
{
  "charger_id": "JEJU_CHG_001_01",
  "date": "2026-01-19",
  "num_sessions": 5,
  "total_revenue": "15000",
  "total_energy": "75.50",
  "avg_charge": "3000"
}
```

#### 기간별 통계
```http
GET /statistics/charger/{charger_id}/period?start_date=2026-01-01&end_date=2026-01-31
```

#### 충전소 통계
```http
GET /statistics/station/{station_id}?start_date=2026-01-01&end_date=2026-01-31
```

#### 대시보드 전체 통계
```http
GET /statistics/dashboard?target_date=2026-01-19
```

응답:
```json
{
  "date": "2026-01-19",
  "total_stations": 5,
  "total_chargers": 10,
  "charger_status": {
    "available": 7,
    "in_use": 2,
    "fault": 1,
    "offline": 0
  },
  "daily_stats": {
    "sessions": 35,
    "total_revenue": 105000,
    "total_energy": 525.75,
    "avg_charge": 3000
  }
}
```

---

## 대시보드 사용 방법

### 지도 인터페이스

1. **지도 표시**: 제주 지역이 중심으로 표시됩니다
2. **마커 색상**:
   - 🟢 초록색: 사용 가능
   - 🔵 파란색: 사용 중
   - 🔴 빨간색: 고장
   - ⚫ 회색: 오프라인

### 필터 기능

- **충전소**: 특정 충전소의 충전기만 표시
- **상태**: 특정 상태의 충전기만 표시
- **종류**: 급속/완속/초급속 충전기 필터링

### 통계 정보

사이드바에서 다음 정보를 확인할 수 있습니다:
- 운영 중인 충전기 수
- 현재 사용 중인 충전기
- 오늘의 총 매출
- 오늘의 총 충전량

### 충전기 상세 정보

마커나 목록에서 충전기를 클릭하면 다음 정보를 확인할 수 있습니다:
- 충전기 기본 정보
- 현재 상태
- 요금 정보
- 오늘의 세션 수, 에너지, 매출

### 데이터 내보내기

"내보내기" 버튼을 클릭하여 현재 데이터를 JSON 형식으로 다운로드합니다.

---

## 데이터 항목

### 충전소 정보 항목

- ✅ 충전소 ID
- ✅ 충전소 명칭
- ✅ 운영사
- ✅ 주소
- ✅ 경도/위도
- ✅ 운영사 연락처

### 충전기 정보 항목

- ✅ 충전기 ID
- ✅ 충전기 종류 (급속/완속/초급속)
- ✅ 충전기 용량 (kW)
- ✅ 설치 위치 (주소, 경도/위도)
- ✅ 현재 사용 상태
- ✅ 출력 제어 기능
- ✅ 요금 (기본요금, 단위 요금)
- ✅ 기물번호 (시리얼번호)
- ✅ 제조사, 모델명
- ✅ 제조일자, 설치일자
- ✅ 정비 이력

### 운영 데이터 항목

- ✅ 충전 세션별 기록
- ✅ 에너지 공급량 (kWh)
- ✅ 충전 시간대
- ✅ 매출 정보
  - ✅ 시간대별 매출
  - ✅ 일일 누적 매출
  - ✅ 기간별 누적 매출
- ✅ 요금 구성 (기본요금, 전력료, 시간료)
- ✅ 결제 상태

### 전력 정보 항목

- ✅ 입력 전력 (kW)
- ✅ 누적 전력량 (kWh)
  - ✅ 시간대별 누적
  - ✅ 일일 누적
  - ✅ 누계 누적
- ✅ 역률, 전압, 전류

### 분석 데이터

- ✅ 시간대별 통계 (세션, 에너지, 매출)
- ✅ 일일 통계
- ✅ 기간별 요약
- ✅ 충전소별 통계
- ✅ 가용률

---

## 트러블슈팅

### 데이터베이스 오류

**문제**: `database is locked`
```
해결: 기존 session을 닫고 새 session을 열기
```

### API 연결 실패

**문제**: `Connection refused`
```
해결: 
1. API 서버 실행 확인: python gis_dashboard_api.py
2. 포트 8000이 사용 중인지 확인
3. 방화벽 설정 확인
```

### 지도가 표시되지 않음

**문제**: 지도가 로드되지 않음
```
해결:
1. 인터넷 연결 확인
2. 브라우저 콘솔에서 오류 메시지 확인
3. 캐시 삭제 및 새로고침
```

---

## 추가 커스터마이징

### 데이터베이스 변경

#### PostgreSQL 사용

```python
# gis_dashboard_api.py에서
db_manager = DatabaseManager(
    "postgresql://user:password@localhost/charger_db"
)
```

#### MySQL 사용

```python
db_manager = DatabaseManager(
    "mysql+pymysql://user:password@localhost/charger_db"
)
```

### 대시보드 커스터마이징

`gis_dashboard.html`을 수정하여:
- 색상 변경
- 추가 통계 추가
- 맵 스타일 변경

---

## 라이선스

MIT License

---

## 문의

데이터베이스 설계 및 API 개발에 대한 문의사항은 프로젝트 이슈를 등록해주세요.
