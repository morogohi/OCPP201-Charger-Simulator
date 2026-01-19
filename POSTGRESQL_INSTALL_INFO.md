# PostgreSQL 설치 완료 정보

## ✅ 설치 현황

| 항목 | 정보 |
|------|------|
| **버전** | PostgreSQL 18.1 |
| **설치 경로** | `C:\Program Files\PostgreSQL\18` |
| **bin 경로** | `C:\Program Files\PostgreSQL\18\bin` |
| **포트** | 5432 (기본) |
| **설치 날짜** | 2026-01-19 |

## 🔧 Quick Start

### 1. PATH 설정 (선택)

```powershell
# 영구 설정 - PowerShell 관리자 모드 필요
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
[Environment]::SetEnvironmentVariable(
    "PATH",
    "$([Environment]::GetEnvironmentVariable('PATH', 'Machine'));$pgBin",
    "Machine"
)
```

### 2. DATABASE_URL 설정

```powershell
# 이미 설정됨
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"

# 영구 설정 확인
[Environment]::GetEnvironmentVariable("DATABASE_URL", "User")
```

### 3. 데이터베이스 상태 확인

```powershell
# 연결 테스트
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
&"$pgBin\psql" -U charger_user -d charger_db -h localhost -c "SELECT version();"
```

### 4. API 서버 실행

```powershell
cd C:\Project\OCPP201(P2M)
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python gis_dashboard_api.py
```

## 📊 데이터베이스 정보

### 사용자
- **사용자명**: charger_user
- **암호**: admin
- **권한**: 데이터베이스 소유자

### 데이터베이스
- **이름**: charger_db
- **소유자**: charger_user
- **인코딩**: UTF8

### 테이블 (7개)
```
✅ station_info           - 충전소 정보
✅ charger_info           - 충전기 정보  
✅ charger_usage_log      - 충전 거래 기록
✅ power_consumption      - 전력 사용량
✅ daily_charger_stats    - 일일 충전기 통계
✅ hourly_charger_stats   - 시간별 충전기 통계
✅ station_daily_stats    - 일일 충전소 통계
```

## 🚀 자주 사용하는 명령어

### psql 명령어

```powershell
# 데이터베이스 접속
&"C:\Program Files\PostgreSQL\18\bin\psql" -U charger_user -d charger_db

# SQL 파일 실행
&"C:\Program Files\PostgreSQL\18\bin\psql" -U charger_user -d charger_db -f script.sql

# 데이터 백업
&"C:\Program Files\PostgreSQL\18\bin\pg_dump" -U charger_user charger_db > backup.sql

# 데이터 복구
&"C:\Program Files\PostgreSQL\18\bin\psql" -U charger_user charger_db < backup.sql
```

### Python에서 사용

```python
import os
os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

# 연결 테스트
python test_db_connection.py

# 샘플 데이터 초기화
python init_jeju_chargers.py

# API 서버 실행
python gis_dashboard_api.py
```

## 📝 참고사항

- PostgreSQL 서비스는 자동으로 시작됩니다
- 포트 5432가 다른 애플리케이션에 의해 사용 중인 경우, 설치 시 다른 포트 선택 가능
- psql 사용 전 DATABASE_URL 환경변수 설정 필수
- 데이터베이스 암호 변경: `ALTER USER charger_user WITH PASSWORD 'new_password';`

## 📚 추가 정보

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/18/)
- [psql 명령어 레퍼런스](https://www.postgresql.org/docs/18/app-psql.html)
- [POSTGRESQL_SETUP.md](./POSTGRESQL_SETUP.md) - 상세 설정 가이드
- [POSTGRESQL_IMPLEMENTATION.md](./POSTGRESQL_IMPLEMENTATION.md) - 구현 요약
- [test_db_connection.py](./test_db_connection.py) - 연결 테스트 스크립트
