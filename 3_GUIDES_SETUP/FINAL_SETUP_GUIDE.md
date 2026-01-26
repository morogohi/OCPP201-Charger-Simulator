# OCPP 2.0.1 + PostgreSQL 최종 설정 가이드

## 📋 목차
1. [PostgreSQL 설치 확인](#postgresql-설치-확인)
2. [환경 변수 설정](#환경-변수-설정)
3. [데이터베이스 확인](#데이터베이스-확인)
4. [API 서버 실행](#api-서버-실행)
5. [대시보드 접속](#대시보드-접속)

---

## ✅ PostgreSQL 설치 확인

### Windows
```powershell
# PostgreSQL 18 설치 경로
C:\Program Files\PostgreSQL\18

# 버전 확인
&"C:\Program Files\PostgreSQL\18\bin\psql" --version
# psql (PostgreSQL) 18.1
```

---

## 🔧 환경 변수 설정

### 방법 1: PowerShell (권장)

**임시 설정 (현재 세션)**
```powershell
# PostgreSQL PATH
$env:PATH += ";C:\Program Files\PostgreSQL\18\bin"

# 데이터베이스 연결
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 확인
$env:DATABASE_URL
```

**영구 설정 (시스템 환경변수)**
```powershell
# 관리자 권한이 필요합니다

# PostgreSQL PATH 추가
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
[Environment]::SetEnvironmentVariable(
    "PATH",
    "$([Environment]::GetEnvironmentVariable('PATH', 'Machine'));$pgBin",
    "Machine"
)

# DATABASE_URL 설정
[Environment]::SetEnvironmentVariable(
    "DATABASE_URL",
    "postgresql://charger_user:admin@localhost:5432/charger_db",
    "User"
)
```

### 방법 2: 자동 설정 스크립트

```powershell
# 관리자 권한으로 실행
.\setup_postgresql_env.ps1

# 또는 매개변수로 실행
.\setup_postgresql_env.ps1 -Permanent
```

### 방법 3: 검증 스크립트

```cmd
# CMD에서 실행
verify_postgresql_setup.bat
```

---

## 📊 데이터베이스 확인

### 데이터베이스 정보
| 항목 | 값 |
|------|-----|
| **호스트** | localhost |
| **포트** | 5432 |
| **데이터베이스** | charger_db |
| **사용자** | charger_user |
| **암호** | admin |

### 테이블 확인
```powershell
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# Python으로 확인
python test_db_connection.py

# SQL로 확인
&"$pgBin\psql" -U charger_user -d charger_db -c "\dt"
```

**생성된 테이블**
```
✅ station_info           - 충전소 정보
✅ charger_info           - 충전기 정보
✅ charger_usage_log      - 충전 거래 기록
✅ power_consumption      - 전력 사용량
✅ daily_charger_stats    - 일일 충전기 통계
✅ hourly_charger_stats   - 시간별 충전기 통계
✅ station_daily_stats    - 일일 충전소 통계
```

### 샘플 데이터 확인
```powershell
# 제주 지역 데이터 (이미 초기화됨)
# - 5개 충전소
# - 9개 충전기
# - 지난 7일의 사용 기록

python test_db_connection.py
```

---

## 🚀 API 서버 실행

### 단계별 실행

```powershell
# 1. 프로젝트 디렉토리 이동
cd C:\Project\OCPP201(P2M)

# 2. 환경변수 설정 (필요한 경우)
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 3. API 서버 시작
python gis_dashboard_api.py

# 또는 uvicorn으로 실행
uvicorn gis_dashboard_api:app --reload --port 8000
```

### 예상 출력
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
INFO:     Application startup complete
```

---

## 🌐 대시보드 접속

### API 문서
```
http://localhost:8000/docs
```

특징:
- 모든 API 엔드포인트 테스트 가능
- 요청/응답 예시 표시
- Swagger UI 기반

### 웹 대시보드

```
gis_dashboard.html (파일로 열기)
또는
http://localhost:8000
```

기능:
- 제주 지역 지도 (Leaflet.js)
- 실시간 충전기 위치 표시
- 상태별 색상 구분 (초록/파랑/빨강/회색)
- 충전소별 필터링
- 통계 및 수익 정보
- 실시간 자동 갱신

---

## 🔍 문제 해결

### PostgreSQL 연결 실패
```powershell
# 1. 서버 상태 확인
net start | find "PostgreSQL"

# 2. 포트 확인
netstat -ano | find "5432"

# 3. 직접 접속 시도
&"C:\Program Files\PostgreSQL\18\bin\psql" -U postgres
# 슈퍼유저로 연결

# 4. 데이터베이스 및 사용자 재생성
&"C:\Program Files\PostgreSQL\18\bin\psql" -U postgres -c `
  "CREATE USER charger_user WITH PASSWORD 'admin'; CREATE DATABASE charger_db OWNER charger_user;"
```

### psql 명령어를 찾을 수 없음
```powershell
# 전체 경로 사용
&"C:\Program Files\PostgreSQL\18\bin\psql" --version

# 또는 PATH 추가
$env:PATH += ";C:\Program Files\PostgreSQL\18\bin"
psql --version
```

### API 포트 충돌
```powershell
# 다른 포트 사용
python gis_dashboard_api.py --port 8001

# 또는 기존 프로세스 종료
netstat -ano | find "8000"
taskkill /PID <PID> /F
```

---

## 📚 유용한 명령어

### psql 명령어
```powershell
$pgBin = "C:\Program Files\PostgreSQL\18\bin"

# 데이터베이스 접속
&"$pgBin\psql" -U charger_user -d charger_db

# SQL 파일 실행
&"$pgBin\psql" -U charger_user -d charger_db -f script.sql

# 데이터 백업
&"$pgBin\pg_dump" -U charger_user charger_db > backup.sql

# 데이터 복구
&"$pgBin\psql" -U charger_user charger_db < backup.sql

# 단일 쿼리 실행
&"$pgBin\psql" -U charger_user -d charger_db -c "SELECT * FROM station_info;"
```

### Python 스크립트
```powershell
# 연결 테스트
python test_db_connection.py

# 샘플 데이터 초기화
python init_jeju_chargers.py

# API 서버 실행
python gis_dashboard_api.py

# OCPP 시뮬레이터 실행
python charger_simulator.py
```

---

## ✨ 다음 단계

1. **API 서버 실행**
   ```powershell
   cd C:\Project\OCPP201(P2M)
   $env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
   python gis_dashboard_api.py
   ```

2. **대시보드 열기**
   - API 문서: http://localhost:8000/docs
   - 웹 대시보드: http://localhost:8000

3. **샘플 데이터 확인**
   - 제주 5개 충전소
   - 9개 충전기
   - 지난 7일의 통계

4. **실시간 모니터링**
   - 충전기 상태 확인
   - 일일 매출 및 전력량 조회
   - 충전소별 통계

---

## 📞 참고 자료

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/18/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [POSTGRESQL_SETUP.md](./POSTGRESQL_SETUP.md) - 상세 설정 가이드
- [POSTGRESQL_INSTALL_INFO.md](./POSTGRESQL_INSTALL_INFO.md) - 설치 정보
- [GIS_DATABASE_GUIDE.md](./GIS_DATABASE_GUIDE.md) - 데이터베이스 가이드

---

**마지막 업데이트**: 2026-01-19
**PostgreSQL 버전**: 18.1 (Windows)
**설치 경로**: C:\Program Files\PostgreSQL\18
