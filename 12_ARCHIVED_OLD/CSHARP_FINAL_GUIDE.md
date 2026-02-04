# 🎯 C# OCPP 시뮬레이터 - 최종 통합 가이드

## 📍 현재 상황

```
✅ C# OCPP 2.0.1 시뮬레이터 완성
   └─ 1,200+ 줄 코드
   └─ 5개 시나리오 + 6개 고급 예제
   └─ WebSocket 기반 OCPP 메시지 구현

✅ Python OCPP 서버 준비됨
   └─ 에너지 데이터 처리 완료
   └─ PostgreSQL 데이터베이스 연동
   └─ 340+ 거래 기록

✅ 문서화 완료
   └─ 아키텍처 다이어그램
   └─ 실행 매뉴얼
   └─ 빠른 시작 가이드
```

---

## 🚀 3단계 실행 프로세스

### Step 1️⃣: Python 서버 시작 (터미널 1)

```powershell
# 프로젝트 폴더로 이동
cd c:\Project\OCPP201\(P2M)

# Python OCPP 서버 시작
python ocpp_server.py

# ✅ 다음 메시지가 나타나면 준비 완료:
# [INFO] OCPP Server listening on ws://localhost:9000
# [INFO] Server started. Press Ctrl+C to stop.
```

**서버 모니터링:**
```powershell
# 별도 터미널에서 포트 확인
netstat -ano | findstr :9000

# 또는 PowerShell로 확인
Get-NetTCPConnection -LocalPort 9000 | Select-Object State, LocalPort
```

---

### Step 2️⃣: C# 클라이언트 실행 (터미널 2)

```powershell
# 새 터미널 열기 (Ctrl+Shift+`)

cd c:\Project\OCPP201\(P2M)

# 방법 A: 자동 빌드 + 실행 (권장)
.\build_and_run.ps1 2

# 또는 방법 B: 직접 실행
dotnet run --project OCPPSimulator -- 2

# 또는 방법 C: 릴리스 모드로 빌드 후 실행
dotnet build OCPPSimulator -c Release
dotnet run --project OCPPSimulator --no-build -c Release -- 2
```

**실행 중 화면:**
```
[연결] emart_jeju_01에 연결 중...
✓ WebSocket 연결 성공
[BootNotification 전송]

[시작] 충전 세션 시작...
[TransactionEvent - Started] Energy: 0.00 kWh

[5초 경과] TransactionEvent - Updated, Energy: 0.14 kWh
[10초 경과] TransactionEvent - Updated, Energy: 0.28 kWh
[15초 경과] TransactionEvent - Updated, Energy: 0.42 kWh

[종료] TransactionEvent - Ended, Energy: 0.42 kWh

✓ 시나리오 2 완료 (30초)
```

---

### Step 3️⃣: 데이터 검증 (터미널 3)

```powershell
# 새 터미널 열기

cd c:\Project\OCPP201\(P2M)

# C# 실행이 끝난 후 데이터 확인
python verify_energy_data.py

# ✅ 출력 예시:
# ✓ Database connected
# ✓ Found 1 new record
#
# Transaction Details:
# ├─ charger_id: emart_jeju_01
# ├─ transaction_id: txn_2026011910304501
# ├─ energy_delivered: 0.42 kWh
# ├─ total_charge: 63.0 원
# └─ created_at: 2026-01-21 10:30:47
```

---

## 📊 시나리오별 실행 시간표

| 시나리오 | 설명 | 시간 | 명령어 |
|---------|------|------|--------|
| **1** | 기본 연결 테스트 | 5초 | `.\build_and_run.ps1 1` |
| **2** | 충전 세션 (에너지 추적) | 30초 | `.\build_and_run.ps1 2` |
| **3** | 다중 충전기 (3개) | 40초 | `.\build_and_run.ps1 3` |
| **4** | 에너지 데이터 검증 | 10초 | `.\build_and_run.ps1 4` |
| **5** | 스트레스 테스트 (5개) | 40초 | `.\build_and_run.ps1 5` |
| **all** | 모든 시나리오 | 125초 | `.\build_and_run.ps1 all` |

---

## 🔄 전체 워크플로우

```
시작
  ↓
[터미널 1] Python 서버 실행
  ├─ python ocpp_server.py
  ├─ 대기: "Server listening on ws://localhost:9000"
  └─ ✅ 서버 준비 완료
  ↓
[터미널 2] C# 클라이언트 실행
  ├─ .\build_and_run.ps1 2
  ├─ WebSocket 연결
  ├─ 5개 메시지 교환 (Started → Updated → Updated → Updated → Ended)
  ├─ 30초 실행
  └─ ✅ 클라이언트 완료
  ↓
[Python 서버] 데이터 저장
  ├─ TransactionEvent 메시지 수신
  ├─ 에너지 데이터 추출 (chargingPeriods.dimensions)
  ├─ 데이터 변환 (Wh → kWh)
  ├─ PostgreSQL에 저장
  └─ ✅ 데이터베이스 업데이트 완료
  ↓
[터미널 3] 데이터 검증
  ├─ python verify_energy_data.py
  ├─ 데이터베이스 조회
  ├─ 에너지 값 확인 (0.42 kWh)
  ├─ 비용 계산 확인 (63원)
  └─ ✅ 검증 완료
  ↓
완료 ✨
```

---

## 💻 명령어 빠른 레퍼런스

### 빌드 관련
```powershell
# 디버그 빌드 (개발용)
dotnet build OCPPSimulator

# 릴리스 빌드 (프로덕션)
dotnet build OCPPSimulator -c Release

# 빌드 캐시 제거 후 빌드
dotnet clean OCPPSimulator
dotnet build OCPPSimulator -c Release
```

### 실행 관련
```powershell
# 시나리오별 실행
.\build_and_run.ps1 1         # 기본 연결
.\build_and_run.ps1 2         # 충전 세션
.\build_and_run.ps1 3         # 다중 충전기
.\build_and_run.ps1 4         # 에너지 검증
.\build_and_run.ps1 5         # 스트레스 테스트
.\build_and_run.ps1 all       # 모든 시나리오

# 직접 실행 (빌드 건너뛰기)
dotnet run --project OCPPSimulator --no-build -- 2
```

### 서버 관련
```powershell
# Python 서버 시작
python ocpp_server.py

# 데이터 검증
python verify_energy_data.py

# 데이터베이스 직접 조회
psql -U postgres -d charger_db -c "
  SELECT charger_id, energy_delivered, total_charge 
  FROM charger_usage_log 
  ORDER BY created_at DESC 
  LIMIT 5;"
```

---

## 🔍 예상 결과물

### C# 클라이언트 실행 후 Python 서버 로그

```log
=== OCPP Server Running ===
[2026-01-21 10:30:45.123] WebSocket connected: emart_jeju_01

[2026-01-21 10:30:45.456] BootNotification received
  Vendor: OCPP.NET
  Model: CSharpSimulator
  SerialNumber: SN-emart_jeju_01-001

[2026-01-21 10:30:47.789] TransactionEvent - Started
  transactionId: txn_2026011910304501
  chargingState: Preparing
  energy: 0.00 kWh

[2026-01-21 10:30:52.111] TransactionEvent - Updated
  transactionId: txn_2026011910304501
  chargingState: Charging
  energy: 0.14 kWh
  → Stored in database ✓

[2026-01-21 10:30:57.222] TransactionEvent - Updated
  transactionId: txn_2026011910304501
  chargingState: Charging
  energy: 0.28 kWh
  → Stored in database ✓

[2026-01-21 10:31:02.333] TransactionEvent - Updated
  transactionId: txn_2026011910304501
  chargingState: Charging
  energy: 0.42 kWh
  → Stored in database ✓

[2026-01-21 10:31:27.444] TransactionEvent - Ended
  transactionId: txn_2026011910304501
  chargingState: Available
  energy: 0.42 kWh (Final)
  totalCharge: 63.0 원
  → Stored in database ✓

[2026-01-21 10:31:30.555] WebSocket disconnected: emart_jeju_01
```

### 데이터베이스 최종 결과

```sql
charger_id       │ transaction_id          │ energy_delivered │ total_charge
─────────────────┼─────────────────────────┼──────────────────┼──────────────
emart_jeju_01    │ txn_2026011910304501    │ 0.42             │ 63.0
```

---

## ⚡ 성능 예상치

| 항목 | 값 |
|------|-----|
| **빌드 시간** | 5-10초 |
| **시나리오 1 실행** | 5초 |
| **시나리오 2 실행** | 30초 |
| **시나리오 3 실행** | 40초 (병렬) |
| **데이터 검증** | 1초 |
| **총 E2E 시간** | ~50초 (시나리오 2 기준) |

---

## ✅ 최종 체크리스트

### 사전 확인
- [ ] .NET 6.0 SDK 설치됨: `dotnet --version` 실행
- [ ] Python 3.x 설치됨: `python --version` 실행
- [ ] PostgreSQL 설치됨: `psql --version` 실행
- [ ] 프로젝트 폴더 접근 가능: `c:\Project\OCPP201(P2M)`

### 실행 확인
- [ ] Python 서버 실행: `python ocpp_server.py` (포트 9000 수신)
- [ ] C# 빌드 성공: `dotnet build OCPPSimulator`
- [ ] 시나리오 1 완료: `.\build_and_run.ps1 1` (5초)
- [ ] 시나리오 2 완료: `.\build_and_run.ps1 2` (30초)
- [ ] 서버 로그에 TransactionEvent 메시지 표시됨

### 데이터 검증
- [ ] 데이터베이스에 레코드 저장됨: `python verify_energy_data.py`
- [ ] 에너지 값 정확함: 0.42 kWh ✓
- [ ] 비용 계산 정확함: 63원 (0.42 × 150) ✓
- [ ] 타임스탐프 기록됨 ✓

### 최종 확인
- [ ] 모든 시나리오 실행 가능: `.\build_and_run.ps1 all`
- [ ] 에러 메시지 없음
- [ ] 데이터베이스 일관성 유지됨

---

## 🎓 추가 학습 자료

### 문서 읽기 순서
1. **CSHARP_QUICK_START.md** - 5분 빠른 시작 (먼저 읽기)
2. **CSHARP_EXECUTION_MANUAL.md** - 상세 실행 가이드
3. **CSHARP_ARCHITECTURE.md** - 아키텍처 및 흐름도
4. **OCPPSimulator/README_KO.md** - C# 코드 설명

### 코드 탐색
- [OCPPClient.cs](OCPPSimulator/Clients/OCPPClient.cs) - WebSocket 클라이언트 (430줄)
- [OCPPMessages.cs](OCPPSimulator/Models/OCPPMessages.cs) - OCPP 메시지 정의
- [Program.cs](OCPPSimulator/Program.cs) - 5개 시나리오

### 서버 소스
- [ocpp_server.py](ocpp_server.py) - Python OCPP 서버
- [verify_energy_data.py](verify_energy_data.py) - 데이터 검증 스크립트

---

## 🆘 문제 해결

### 문제: "Unable to connect to server"
```powershell
# ✅ 해결
python ocpp_server.py          # 터미널 1에서 실행
netstat -ano | findstr :9000   # 포트 9000 확인
```

### 문제: "Build failed"
```powershell
# ✅ 해결
dotnet clean OCPPSimulator
dotnet build OCPPSimulator -c Release
```

### 문제: "No records in database"
```powershell
# ✅ 해결
# 1. Python 서버 로그 확인 (에러 메시지 찾기)
# 2. 데이터베이스 연결 확인
psql -U postgres -d charger_db -c "SELECT 1;"
# 3. 테이블 존재 확인
psql -U postgres -d charger_db -c "\d charger_usage_log"
```

---

## 📞 지원

문제가 발생하면:
1. 해당 오류 메시지를 [CSHARP_EXECUTION_MANUAL.md](CSHARP_EXECUTION_MANUAL.md)에서 검색
2. 문제 해결 섹션 참고
3. Python 서버 로그에서 추가 정보 확인

---

**준비 완료! 시작하세요:** 🚀

```powershell
# 터미널 1: 서버
python ocpp_server.py

# 터미널 2: 클라이언트
.\build_and_run.ps1 2

# 터미널 3: 검증
python verify_energy_data.py
```

✨ **모든 것이 준비되었습니다!** ✨
