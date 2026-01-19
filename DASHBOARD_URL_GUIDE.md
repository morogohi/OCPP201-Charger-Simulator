# 대시보드 및 API 접속 가이드

## 🚀 빠른 시작

### 1단계: API 서버 실행

```powershell
cd "c:\Project\OCPP201(P2M)"

# 환경변수 설정
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# API 서버 실행
python gis_dashboard_api.py
```

**예상 출력:**
```
✅ 데이터베이스 초기화 완료
INFO:     Started server process [XXXX]
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
```

---

## 🌐 접속 정보

### API 서버

| 항목 | 주소 | 설명 |
|------|------|------|
| **API 기본 URL** | http://localhost:3000 | REST API 기본 주소 |
| **API 문서** | http://localhost:3000/docs | Swagger UI (API 테스트 가능) |
| **데이터베이스** | localhost:5432 | PostgreSQL |

### 대시보드

| 이름 | URL | 설명 |
|------|-----|------|
| **고급 대시보드** | [advanced_dashboard.html](./advanced_dashboard.html) | ✨ 신규 (권장) |
| **기본 대시보드** | [gis_dashboard.html](./gis_dashboard.html) | 기존 버전 |

---

## 📋 대시보드 사용 방법

### 고급 대시보드 (advanced_dashboard.html) - ⭐ 권장

#### 1️⃣ 파일로 직접 열기
```powershell
# PowerShell에서 실행
Start-Process "c:\Project\OCPP201(P2M)\advanced_dashboard.html"

# 또는 수동으로 열기
# 1. 파일 탐색기 열기
# 2. c:\Project\OCPP201(P2M)\advanced_dashboard.html 더블클릭
# 3. 기본 브라우저에서 열기
```

#### 2️⃣ 브라우저에서 직접 주소 입력
```
file:///c:/Project/OCPP201(P2M)/advanced_dashboard.html
```

#### 3️⃣ HTTP 서버를 통해 열기
```powershell
# Python의 간단한 HTTP 서버 실행
cd "c:\Project\OCPP201(P2M)"
python -m http.server 8080

# 브라우저에서 접속
# http://localhost:8080/advanced_dashboard.html
```

### 기본 대시보드 (gis_dashboard.html)

```powershell
# 파일로 직접 열기
Start-Process "c:\Project\OCPP201(P2M)\gis_dashboard.html"
```

---

## 🔌 API 엔드포인트 목록

### 🏢 충전소 관리

```
GET    /stations              # 모든 충전소 조회
POST   /stations              # 새 충전소 생성
GET    /stations/{id}         # 특정 충전소 조회
PUT    /stations/{id}         # 충전소 정보 수정
DELETE /stations/{id}         # 충전소 삭제
```

**예시 요청:**
```bash
curl -X GET "http://localhost:3000/stations" \
  -H "Content-Type: application/json"
```

---

### 🔌 충전기 관리

```
GET    /chargers              # 모든 충전기 조회
POST   /chargers              # 새 충전기 생성
GET    /chargers/{id}         # 특정 충전기 조회
PATCH  /chargers/{id}/status  # 충전기 상태 변경
```

**예시 요청:**
```bash
curl -X GET "http://localhost:3000/chargers" \
  -H "Content-Type: application/json"
```

---

### 🗺️ GIS 데이터

```
GET    /geo/chargers          # 지도 표시용 충전기 데이터
GET    /geo/heatmap           # 사용량 히트맵 데이터
```

**응답 예시:**
```json
{
  "charger_id": "JEJU_CHG_001_01",
  "station_id": "JEJU_STA_001",
  "station_name": "제주시청 충전소",
  "longitude": 126.5307,
  "latitude": 33.4857,
  "charger_type": "fast",
  "current_status": "available",
  "rated_power": 50.0,
  "unit_price_kwh": 150.0
}
```

---

### 📊 통계 조회

```
GET    /statistics/dashboard              # 대시보드 전체 통계
GET    /statistics/charger/{id}/daily     # 특정 충전기의 일일 통계
GET    /statistics/charger/{id}/period    # 충전기의 기간별 통계
GET    /statistics/station/{id}           # 충전소의 통계
```

**대시보드 통계 응답 예시:**
```json
{
  "total_active_chargers": 128,
  "total_energy_today": 2451.5,
  "total_revenue_today": 350000,
  "utilization_rate": 88,
  "hourly_data": [...]
}
```

---

## 💾 데이터베이스 정보

### PostgreSQL 연결

```powershell
# psql을 사용한 직접 접속
$pgBin = "C:\Program Files\PostgreSQL\18\bin\psql"
&$pgBin -U charger_user -d charger_db -h localhost

# 또는 환경변수로 접속
$env:PGPASSWORD = "admin"
&"C:\Program Files\PostgreSQL\18\bin\psql" -U charger_user -d charger_db -h localhost
```

### 주요 테이블

```sql
-- 충전소 정보
SELECT * FROM station_info;

-- 충전기 정보
SELECT * FROM charger_info;

-- 충전 거래 이력
SELECT * FROM charger_usage_log;

-- 전력 사용량
SELECT * FROM power_consumption;

-- 일일 통계
SELECT * FROM daily_charger_stats;
```

---

## 🎛️ Smart Charging 제어

### 기능

1. **원격 출력 제한**
   - 슬라이더로 10~100kW 범위 내에서 출력 제한
   - 실시간 OCPP 메시지 전송

2. **원격 시작/중지**
   - 원격으로 충전 시작 신호 전송
   - 충전 중단 신호 전송

3. **실시간 모니터링**
   - 충전기 상태 실시간 업데이트
   - 전력 사용량 실시간 차트

---

## 📈 주요 시각화

### 지도 표시
- 제주도 OpenStreetMap 기반
- 상태별 마커 (초록/파랑/빨강/회색)
- 마커 클릭 시 상세 정보 팝업

### 시간대별 차트
- X축: 00시 ~ 23시
- Y축: 전력 사용량 (kWh)
- 실시간 업데이트

### KPI 카드
- 활성 충전기 수
- 오늘 총 충전량
- 총 매출
- 이용률

---

## 🐛 문제 해결

### API 서버가 실행되지 않음

```powershell
# 1. 포트 확인
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

# 2. 포트 점유 프로세스 종료
Get-Process | Where-Object {$_.Id -eq <PID>} | Stop-Process -Force

# 3. 데이터베이스 연결 확인
python test_db_connection.py

# 4. 환경변수 설정 확인
$env:DATABASE_URL
```

### 대시보드가 로드되지 않음

```powershell
# 1. 파일 경로 확인
Test-Path "c:\Project\OCPP201(P2M)\advanced_dashboard.html"

# 2. 브라우저 콘솔 확인
# F12 → Console 탭에서 에러 메시지 확인

# 3. 파일 권한 확인
Get-Item "c:\Project\OCPP201(P2M)\advanced_dashboard.html" | 
  Select-Object FullName, Attributes
```

### API 요청이 실패함

```powershell
# 1. API 서버 상태 확인
Invoke-WebRequest -Uri "http://localhost:3000/stations" -ErrorAction SilentlyContinue

# 2. CORS 문제 확인
# 브라우저 콘솔에서 CORS 에러 메시지 확인

# 3. 데이터베이스 연결 확인
python test_db_connection.py
```

---

## 🔄 데이터 새로고침

### 자동 갱신
- 대시보드: 5초마다 자동 갱신
- 지도: 마커 상태 실시간 업데이트

### 수동 갱신
```javascript
// 브라우저 콘솔에서 실행
location.reload();  // 페이지 새로고침
```

---

## 📱 모바일 접속

### 반응형 디자인
- 태블릿/모바일 환경 지원
- 터치 제어 최적화

### 접속 방법
```
로컬 네트워크의 다른 기기에서:
http://<PC의_IP_주소>:3000/docs
```

**PC IP 확인:**
```powershell
ipconfig | findstr "IPv4"
```

---

## 💡 팁

### 개발자 도구 사용
```powershell
# F12: 개발자 도구 열기
# Ctrl+Shift+I: 검사 도구 열기
# F5: 페이지 새로고침
# Ctrl+Shift+Delete: 캐시 삭제
```

### API 테스트 도구
- **Swagger UI**: http://localhost:3000/docs
- **Postman**: API 요청 테스트 (별도 설치)
- **curl**: 명령줄에서 API 테스트

### 로그 확인
```powershell
# API 서버 로그
# 터미널에서 실시간 확인

# 데이터베이스 쿼리 로그
# /database 폴더의 로그 파일 확인
```

---

## 📞 지원

| 항목 | 정보 |
|------|------|
| **프로젝트 경로** | c:\Project\OCPP201(P2M) |
| **GitHub 저장소** | https://github.com/morogohi/OCPP201-Charger-Simulator |
| **문서** | FINAL_SETUP_GUIDE.md, POSTGRESQL_SETUP.md |
| **API 문서** | http://localhost:3000/docs |

---

**마지막 업데이트**: 2026-01-19  
**API 버전**: 1.0  
**권장 브라우저**: Chrome, Edge, Firefox
