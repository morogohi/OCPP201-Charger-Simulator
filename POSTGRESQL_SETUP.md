# PostgreSQL 데이터베이스 설정 가이드

제주 EV 충전기 관리 시스템을 PostgreSQL 기반으로 운영하기 위한 완전한 설정 가이드입니다.

## 📋 목차

- [PostgreSQL 설치](#postgresql-설치)
- [데이터베이스 생성](#데이터베이스-생성)
- [Python 패키지 설치](#python-패키지-설치)
- [연결 설정](#연결-설정)
- [데이터 초기화](#데이터-초기화)
- [성능 최적화](#성능-최적화)
- [백업 및 복구](#백업-및-복구)

---

## PostgreSQL 설치

### Windows

#### 1단계: PostgreSQL 다운로드
```
https://www.postgresql.org/download/windows/
```

#### 2단계: 설치
```powershell
# 기본 설치 옵션:
# - 포트: 5432 (기본)
# - 슈퍼유저: postgres
# - 암호: 설정 필수
```

#### 3단계: 설치 확인
```powershell
psql --version
# psql (PostgreSQL) 15.x
```

---

### macOS

```bash
# Homebrew로 설치
brew install postgresql

# 서비스 시작
brew services start postgresql

# 사용자 확인
createdb test
dropdb test
```

---

### Linux (Ubuntu/Debian)

```bash
# 설치
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 상태 확인
sudo systemctl status postgresql
```

---

## 데이터베이스 생성

### 1단계: PostgreSQL 접속

```bash
# Windows
psql -U postgres

# Linux/macOS
sudo -u postgres psql
```

### 2단계: 데이터베이스 및 사용자 생성

```sql
-- 사용자 생성
CREATE USER charger_user WITH PASSWORD 'charger_password';

-- 데이터베이스 생성
CREATE DATABASE charger_db OWNER charger_user;

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE charger_db TO charger_user;

-- 스키마 권한 (선택)
GRANT ALL PRIVILEGES ON SCHEMA public TO charger_user;

-- 확인
\l  -- 데이터베이스 목록
\du -- 사용자 목록
```

### 3단계: 연결 테스트

```bash
# charger_user로 접속
psql -U charger_user -d charger_db -h localhost

# 또는
psql -U charger_user -d charger_db

# \q로 나가기
```

---

## Python 패키지 설치

### 필수 패키지

```bash
pip install psycopg2-binary
pip install psycopg2  # C 확장 버전 (더 빠름)
pip install fastapi uvicorn sqlalchemy
```

### requirements.txt 업데이트

```
# 기본
fastapi>=0.95.0
uvicorn>=0.21.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-dateutil>=2.8.2

# PostgreSQL
psycopg2-binary>=2.9.0

# OCPP
websockets>=10.0
aiohttp>=3.8.0
```

설치:
```bash
pip install -r requirements.txt
```

---

## 연결 설정

### 환경변수 설정

#### Windows (PowerShell)

```powershell
# 임시 설정 (현재 세션만)
$env:DATABASE_URL = "postgresql://charger_user:charger_password@localhost:5432/charger_db"

# 확인
$env:DATABASE_URL
```

#### Windows (CMD)

```cmd
set DATABASE_URL=postgresql://charger_user:charger_password@localhost:5432/charger_db
```

#### Linux/macOS

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export DATABASE_URL="postgresql://charger_user:charger_password@localhost:5432/charger_db"

# 적용
source ~/.bashrc

# 확인
echo $DATABASE_URL
```

### 연결 문자열 형식

```
postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]

예시:
- postgresql://charger_user:charger_password@localhost:5432/charger_db
- postgresql+psycopg2://user:password@localhost/charger_db
- postgresql://localhost/charger_db  (동일 호스트, 기본 인증)
```

### Python 코드에서 설정

```python
import os
from database.models_postgresql import DatabaseManager

# 환경변수에서 읽기
database_url = os.getenv(
    'DATABASE_URL',
    'postgresql://charger_user:charger_password@localhost:5432/charger_db'
)

db_manager = DatabaseManager(database_url)
db_manager.initialize()
```

---

## 데이터 초기화

### 1단계: 모델 선택

`models_postgresql.py` 사용:

```python
# 기존 models.py 대신
from database.models_postgresql import DatabaseManager
```

### 2단계: 초기화 스크립트 실행

```bash
python init_jeju_chargers.py
```

출력:
```
✅ 데이터베이스 초기화 완료: postgresql://charger_user:***@localhost:5432/charger_db
📍 충전소 등록 중...
  ✅ 제주시청 충전소 등록됨
  ...
```

### 3단계: 데이터 확인

```bash
# PostgreSQL CLI
psql -U charger_user -d charger_db

# 테이블 확인
\dt

# 충전소 조회
SELECT * FROM station_info;

# 충전기 조회
SELECT charger_id, station_id, current_status FROM charger_info;

# 통계
SELECT COUNT(*) FROM charger_usage_log;
```

---

## 성능 최적화

### 1. 인덱스 생성

PostgreSQL이 자동으로 생성하지만, 추가 인덱스가 필요한 경우:

```sql
-- 자주 쿼리되는 필드 인덱스
CREATE INDEX idx_charger_status_date 
ON charger_usage_log(charger_id, session_date) 
WHERE payment_status = 'completed';

-- 통계 쿼리 최적화
CREATE INDEX idx_daily_stats_charger_date 
ON daily_charger_stats(stats_date, charger_id);

-- 인덱스 확인
SELECT * FROM pg_indexes WHERE tablename = 'charger_usage_log';
```

### 2. 파티셔닝 (대규모 데이터)

```sql
-- charger_usage_log를 월별로 파티셔닝
CREATE TABLE charger_usage_log_2026_01 PARTITION OF charger_usage_log
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### 3. 자동 진공(Vacuum)

```sql
-- 자동 설정 확인
SHOW autovacuum;

-- 통계 재계산
ANALYZE;
```

### 4. 연결 풀링 (PgBouncer)

```bash
# 설치 (Linux)
sudo apt-get install pgbouncer

# 설정 (/etc/pgbouncer/pgbouncer.ini)
[databases]
charger_db = host=localhost port=5432 dbname=charger_db

[pgbouncer]
listen_port = 6432
max_client_conn = 1000
```

### 5. 캐싱 (Redis)

```python
# 선택사항: 자주 조회되는 데이터를 Redis에 캐싱
import redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 충전소 정보 캐싱 (1시간)
def get_station(station_id):
    cache_key = f"station:{station_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    station = StationService.get_station(db, station_id)
    redis_client.setex(cache_key, 3600, json.dumps(station))
    return station
```

---

## 백업 및 복구

### 전체 데이터베이스 백업

```bash
# SQL 포맷 (텍스트)
pg_dump -U charger_user -d charger_db > charger_db_backup.sql

# 커스텀 포맷 (압축)
pg_dump -U charger_user -d charger_db -F c -f charger_db_backup.dump

# 상세 정보 포함
pg_dump -U charger_user -d charger_db -v > backup_verbose.sql

# 특정 테이블만
pg_dump -U charger_user -d charger_db -t charger_usage_log > usage_log_backup.sql
```

### 테이블별 백업

```bash
# charger_usage_log만 백업
pg_dump -U charger_user -d charger_db -t charger_usage_log > charger_usage_log_backup.sql

# 여러 테이블
pg_dump -U charger_user -d charger_db -t charger_info -t station_info > tables_backup.sql
```

### 데이터만 백업 (스키마 제외)

```bash
pg_dump -U charger_user -d charger_db -a > charger_db_data_only.sql
```

### 복구

```bash
# SQL 파일에서 복구
psql -U charger_user -d charger_db < charger_db_backup.sql

# 커스텀 포맷에서 복구
pg_restore -U charger_user -d charger_db charger_db_backup.dump

# 기존 데이터 삭제 후 복구
pg_restore -U charger_user -d charger_db --clean charger_db_backup.dump
```

### 스케줄 백업 (Linux crontab)

```bash
# crontab 편집
crontab -e

# 매일 자정 백업
0 0 * * * pg_dump -U charger_user -d charger_db -F c -f /backups/charger_db_$(date +\%Y\%m\%d).dump

# 또는 (Python 스크립트)
0 0 * * * /usr/bin/python3 /path/to/backup_script.py
```

### Python 백업 스크립트

```python
# backup_script.py
import subprocess
from datetime import datetime
import os

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'/backups/charger_db_{timestamp}.dump'
    
    cmd = [
        'pg_dump',
        '-U', 'charger_user',
        '-d', 'charger_db',
        '-F', 'c',
        '-f', backup_file,
        '-h', 'localhost'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 백업 완료: {backup_file}")
        
        # 7일 이상된 백업 삭제
        import glob
        backups = glob.glob('/backups/charger_db_*.dump')
        for backup in backups:
            mtime = os.path.getmtime(backup)
            age_days = (time.time() - mtime) / 86400
            if age_days > 7:
                os.remove(backup)
                print(f"🗑️  오래된 백업 삭제: {backup}")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ 백업 실패: {e}")

if __name__ == "__main__":
    backup_database()
```

---

## 모니터링

### 활성 연결 확인

```sql
SELECT datname, usename, count(*) FROM pg_stat_activity 
GROUP BY datname, usename 
ORDER BY count(*) DESC;
```

### 느린 쿼리 로깅

```sql
-- 슬로우 쿼리 로깅 활성화
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1초 이상

-- 설정 적용
SELECT pg_reload_conf();
```

### 데이터베이스 크기

```sql
-- 전체 크기
SELECT pg_database.datname, 
       pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database 
WHERE datname = 'charger_db';

-- 테이블별 크기
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 트러블슈팅

### 연결 실패

```
error: could not connect to server
```

**해결:**
1. PostgreSQL 서비스 실행 확인
2. 호스트명, 포트, 사용자명, 암호 확인
3. 방화벽 설정 확인

```bash
# 서비스 재시작
# Windows
net stop postgresql-x64-15
net start postgresql-x64-15

# Linux
sudo systemctl restart postgresql
```

### 권한 오류

```
ERROR: permission denied for schema public
```

**해결:**
```sql
GRANT ALL PRIVILEGES ON SCHEMA public TO charger_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO charger_user;
```

### 락(Lock) 오류

```
ERROR: cannot access relation exclusively
```

**해결:**
```sql
-- 차단되는 연결 찾기
SELECT * FROM pg_stat_activity WHERE datname = 'charger_db';

-- 연결 강제 종료 (조심!)
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'charger_db' AND pid != pg_backend_pid();
```

---

## 데이터 마이그레이션

### SQLite에서 PostgreSQL로 마이그레이션

```python
# migrate_to_postgresql.py
from sqlalchemy import create_engine
from database.models import Base, StationInfo, ChargerInfo

# SQLite 연결
sqlite_engine = create_engine('sqlite:///./charger_management.db')

# PostgreSQL 연결
pg_engine = create_engine('postgresql://user:password@localhost/charger_db')

# 테이블 생성
Base.metadata.create_all(pg_engine)

# 데이터 마이그레이션
from sqlalchemy.orm import Session

sqlite_session = Session(sqlite_engine)
pg_session = Session(pg_engine)

try:
    # 모든 충전소 복사
    stations = sqlite_session.query(StationInfo).all()
    for station in stations:
        pg_session.add(station)
    pg_session.commit()
    
    print(f"✅ {len(stations)}개의 충전소 마이그레이션 완료")
    
except Exception as e:
    pg_session.rollback()
    print(f"❌ 마이그레이션 실패: {e}")

finally:
    sqlite_session.close()
    pg_session.close()
```

---

## 추가 리소스

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [psycopg2 문서](https://www.psycopg.org/psycopg2/docs/)
- [SQLAlchemy ORM 튜토리얼](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [PostgreSQL 성능 튜닝](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

**주의:** 프로덕션 환경에서는 암호를 환경변수에 저장하고, `.env` 파일을 사용하며, 정기적인 백업을 수행하세요.
