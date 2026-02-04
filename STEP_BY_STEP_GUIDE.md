# 🎯 단계별 실행 가이드 - PowerShell/CMD 오류 해결

현재 발생한 오류들을 해결하는 **정확한 단계별 가이드**입니다.

---

## 📍 현재 상황 분석

### 발생한 오류들:
```
1. .\.venv\Scripts\Activate.ps1 - PowerShell 실행 정책 문제
2. DATABASE_URL 설정 - 문자열 따옴표 누락
3. 경로 오류 - C:\Project에서 실행 시 발생
```

### 원인:
- ❌ 잘못된 경로에서 명령어 실행
- ❌ PowerShell 실행 정책 제한
- ❌ 문자열 따옴표 누락

---

## ✅ 올바른 실행 방법

### 방법 1️⃣: PowerShell (권장) 🌟

#### Step 1: 프로젝트 폴더로 이동
```powershell
cd "C:\Project\OCPP201(P2M)"
```

#### Step 2: 가상환경 활성화
```powershell
& ".\.venv\Scripts\Activate.ps1"
```

**확인**: 터미널 왼쪽에 `(.venv)` 표시되면 성공

#### Step 3: 환경변수 설정
```powershell
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
$env:OCPP_PROTOCOL_DEBUG = "false"
```

#### Step 4: 설정 검증
```powershell
python verify_setup.py
```

**예상 결과**:
```
======================================================================
결과: 14 성공 / 0 실패
======================================================================
✅ 모든 검사 통과!
```

#### Step 5: 새 터미널 열기 (Ctrl+Shift+`)
각 터미널에서 위 Step 1-3을 반복한 후, 아래 명령어 실행:

**Terminal 1 - OCPP 서버**:
```powershell
python 4_PYTHON_SOURCE\ocpp_server.py
```

**Terminal 2 - GIS 대시보드**:
```powershell
python 4_PYTHON_SOURCE\gis_dashboard_api.py
```

**Terminal 3 - Python 시뮬레이터**:
```powershell
python -c "
import asyncio
import sys
sys.path.insert(0, '4_PYTHON_SOURCE')
sys.path.insert(0, '8_DATABASE')
from charger_simulator import ChargerSimulator

async def main():
    charger = ChargerSimulator('TEST_001', 'ws://localhost:9000')
    try:
        print('Python 시뮬레이터 시작')
        await charger.connect()
        print('✅ 연결됨')
        await asyncio.sleep(30)
        print('✅ 완료')
    finally:
        await charger.disconnect()

asyncio.run(main())
"
```

---

### 방법 2️⃣: CMD (Windows 명령 프롬프트)

#### Step 1: 프로젝트 폴더로 이동
```cmd
cd /d "C:\Project\OCPP201(P2M)"
```

#### Step 2: 가상환경 활성화
```cmd
.venv\Scripts\activate.bat
```

**확인**: 터미널 왼쪽에 `(.venv)` 표시되면 성공

#### Step 3: 환경변수 설정
```cmd
set DATABASE_URL=postgresql://charger_user:admin@localhost:5432/charger_db
set OCPP_PROTOCOL_DEBUG=false
```

#### Step 4: 설정 검증
```cmd
python verify_setup.py
```

#### Step 5: 서비스 시작
각 터미널에서 위 Step 1-3 반복 후:

**Terminal 1**:
```cmd
python 4_PYTHON_SOURCE\ocpp_server.py
```

**Terminal 2**:
```cmd
python 4_PYTHON_SOURCE\gis_dashboard_api.py
```

**Terminal 3**:
```cmd
python 6_PYTHON_SCRIPTS\test_simulator.py
```

---

### 방법 3️⃣: 자동 설정 스크립트 (가장 간단)

#### PowerShell 사용:
```powershell
cd "C:\Project\OCPP201(P2M)"
& ".\setup_env.ps1"
```

#### CMD 사용:
```cmd
cd "C:\Project\OCPP201(P2M)"
setup_env.bat
```

이 스크립트가 자동으로:
- ✅ 가상환경 활성화
- ✅ 환경변수 설정
- ✅ 설정 검증
- ✅ 다음 단계 안내

---

## 🧪 빠른 테스트

### 한 줄로 모든 검증하기
```powershell
cd "C:\Project\OCPP201(P2M)" ; & ".\.venv\Scripts\Activate.ps1" ; $env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db" ; python verify_setup.py
```

### 데이터베이스 연결 확인
```powershell
cd "C:\Project\OCPP201(P2M)" ; & ".\.venv\Scripts\Activate.ps1" ; $env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db" ; python 5_PYTHON_TESTS\test_db_connection.py
```

---

## 🔍 문제 해결

### 문제: PowerShell에서 스크립트 실행 안 됨

**해결 1**: `&` 연산자 사용
```powershell
# 잘못된 방법:
.\.venv\Scripts\Activate.ps1

# 올바른 방법:
& ".\.venv\Scripts\Activate.ps1"
```

**해결 2**: 실행 정책 변경 (관리자 권한 필요)
```powershell
# PowerShell을 관리자로 열고:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 그 후:
.\.venv\Scripts\Activate.ps1
```

### 문제: DATABASE_URL 오류

**원인**: 문자열을 따옴표로 감싸지 않음

**잘못된 방법**:
```powershell
$env:DATABASE_URL = postgresql://charger_user:admin@localhost:5432/charger_db
```

**올바른 방법**:
```powershell
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
```

### 문제: 경로 오류

**확인**:
```powershell
# 올바른 위치인지 확인
pwd
# 결과: C:\Project\OCPP201(P2M)

# 파일 존재 확인
Test-Path "4_PYTHON_SOURCE\ocpp_server.py"
# 결과: True
```

---

## 📋 체크리스트

```
✅ 단계 1: 올바른 폴더에 있는가?
   pwd → C:\Project\OCPP201(P2M)

✅ 단계 2: 가상환경이 활성화되었는가?
   (.venv) 프롬프트 표시 확인

✅ 단계 3: DATABASE_URL이 설정되었는가?
   echo $env:DATABASE_URL 로 확인

✅ 단계 4: verify_setup.py 실행 성공?
   14 성공 / 0 실패 메시지 확인

✅ 단계 5: 포트가 사용 가능한가?
   netstat -ano | findstr "9000\|8000"
   (결과가 비어있으면 OK)

✅ 단계 6: PostgreSQL 실행 중?
   Get-Service postgresql*

✅ 단계 7: 3개 터미널 준비 완료?
```

---

## 🚀 즉시 시작하기

**가장 빠른 방법 (복사-붙여넣기):**

```powershell
# PowerShell에 이 전체 블록 붙여넣기:
$ErrorActionPreference = "Stop"
cd "C:\Project\OCPP201(P2M)"
& ".\.venv\Scripts\Activate.ps1"
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
$env:OCPP_PROTOCOL_DEBUG = "false"
python verify_setup.py
Write-Host ""
Write-Host "✅ 준비 완료! 이제 새 터미널 3개를 열어서:"
Write-Host "T1: python 4_PYTHON_SOURCE\ocpp_server.py"
Write-Host "T2: python 4_PYTHON_SOURCE\gis_dashboard_api.py"
Write-Host "T3: python 6_PYTHON_SCRIPTS\test_simulator.py"
```

---

**🎉 이제 성공적으로 시작할 수 있습니다!**
