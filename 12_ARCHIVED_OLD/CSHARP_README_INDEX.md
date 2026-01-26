# 📚 C# OCPP 시뮬레이터 - 문서 인덱스 및 빠른 시작

## 🎯 당신의 상황에 맞는 가이드 찾기

### ⚡ 지금 바로 실행하고 싶다면?
👉 **[CSHARP_QUICK_START.md](CSHARP_QUICK_START.md)** (5분)
```
3단계로 C# 시뮬레이터 실행:
1. Python 서버 시작
2. C# 클라이언트 빌드 & 실행
3. 데이터 검증
```

---

### 📖 상세한 설명이 필요하다면?
👉 **[CSHARP_FINAL_GUIDE.md](CSHARP_FINAL_GUIDE.md)** (10분)
```
✓ 3단계 실행 프로세스
✓ 시나리오별 실행 방법
✓ 예상 결과물
✓ 전체 워크플로우
✓ 문제 해결 가이드
```

---

### 🔧 자세한 실행 매뉴얼이 필요하다면?
👉 **[CSHARP_EXECUTION_MANUAL.md](CSHARP_EXECUTION_MANUAL.md)** (20분)
```
✓ 5가지 빌드 방법
✓ 시나리오 1~5 상세 설명
✓ 예상 출력 (정확한 메시지)
✓ 데이터베이스 검증
✓ 10가지 오류 해결책
✓ 성능 최적화 팁
```

---

### 🏗️ 아키텍처와 흐름도를 이해하고 싶다면?
👉 **[CSHARP_ARCHITECTURE.md](CSHARP_ARCHITECTURE.md)** (15분)
```
✓ 시스템 아키텍처 다이어그램
✓ 메시지 흐름 도표
✓ 상태 변화도
✓ 에너지 누적 계산
✓ 성능 프로파일
✓ 문제 해결 흐름도
```

---

### 💻 C# 코드를 분석하고 싶다면?
👉 **[OCPPSimulator/README_KO.md](OCPPSimulator/README_KO.md)** (20분)
```
소스 코드 설명:
✓ OCPPClient.cs - WebSocket 통신 (430줄)
✓ OCPPMessages.cs - OCPP 메시지 모델
✓ Program.cs - 5개 시나리오 (250줄)
✓ AdvancedExamples.cs - 6개 고급 예제
```

---

### ✅ 프로젝트 상태를 확인하고 싶다면?
👉 **[CSHARP_SIMULATOR_COMPLETION.md](CSHARP_SIMULATOR_COMPLETION.md)**
```
✓ 프로젝트 완성도 100%
✓ 구현된 기능 목록
✓ 코드 통계
✓ GitHub 커밋 정보
✓ 다음 단계 로드맵
```

---

## 🚀 가장 빠른 시작 (2분)

### 터미널 1: Python 서버 실행
```powershell
cd c:\Project\OCPP201\(P2M)
python ocpp_server.py
```
✅ 메시지: `Server listening on ws://localhost:9000`

---

### 터미널 2: C# 클라이언트 실행
```powershell
cd c:\Project\OCPP201\(P2M)
.\build_and_run.ps1 2
```
⏱️ 30초 대기

---

### 터미널 3: 데이터 검증
```powershell
cd c:\Project\OCPP201\(P2M)
python verify_energy_data.py
```
✅ 출력: `✓ Found 1 new record`

---

## 📊 전체 문서 맵

```
📁 C# OCPP 시뮬레이터 프로젝트
│
├─ 🚀 빠른 시작
│  ├─ CSHARP_QUICK_START.md (이 문서)
│  └─ CSHARP_FINAL_GUIDE.md
│
├─ 📖 상세 가이드
│  ├─ CSHARP_EXECUTION_MANUAL.md (가장 상세)
│  └─ CSHARP_ARCHITECTURE.md (아키텍처)
│
├─ 💻 소스 코드
│  └─ OCPPSimulator/
│     ├─ README_KO.md
│     ├─ Program.cs (5개 시나리오)
│     ├─ Clients/OCPPClient.cs (WebSocket)
│     ├─ Models/OCPPMessages.cs (OCPP 메시지)
│     └─ AdvancedExamples.cs (6개 고급 예제)
│
├─ 🔧 빌드 스크립트
│  ├─ build_and_run.ps1 (PowerShell)
│  └─ build_and_test.bat (Batch)
│
├─ ✅ 프로젝트 상태
│  ├─ CSHARP_SIMULATOR_COMPLETION.md
│  └─ ENERGY_DATA_FIX_REPORT.md
│
└─ 🐍 Python 서버
   ├─ ocpp_server.py (OCPP 서버)
   └─ verify_energy_data.py (데이터 검증)
```

---

## 🎓 학습 경로

### 초급 (5분)
1. CSHARP_QUICK_START.md 읽기
2. `.\build_and_run.ps1 2` 실행
3. 데이터 검증

### 중급 (20분)
1. CSHARP_FINAL_GUIDE.md 읽기
2. 모든 시나리오 실행 (`.\build_and_run.ps1 all`)
3. 예상 출력과 비교

### 고급 (1시간)
1. CSHARP_ARCHITECTURE.md 읽기
2. CSHARP_EXECUTION_MANUAL.md 읽기
3. OCPPSimulator/README_KO.md로 코드 분석
4. AdvancedExamples.cs 실행

### 전문가 (2시간)
1. OCPPSimulator 소스 코드 분석
2. ocpp_server.py 분석
3. 커스텀 시나리오 작성
4. PostgreSQL 데이터 분석

---

## 💡 실행 환경별 명령어

### Windows PowerShell
```powershell
# 자동 빌드 + 실행
.\build_and_run.ps1 2

# 수동으로 실행
dotnet run --project OCPPSimulator -- 2
```

### Windows CMD
```batch
# 배치 파일 실행
call build_and_test.bat

# 또는 직접 명령
dotnet run --project OCPPSimulator -- 2
```

### Linux/Mac (WSL)
```bash
# PowerShell Core 사용
pwsh -File build_and_run.ps1 -Scenario 2

# 또는 직접 실행
dotnet run --project OCPPSimulator -- 2
```

---

## ⚙️ 시나리오 선택 가이드

| 목표 | 시나리오 | 시간 |
|------|--------|------|
| 기본 테스트 | `1` | 5초 |
| 에너지 추적 테스트 | `2` | 30초 |
| 병렬 처리 테스트 | `3` | 40초 |
| 데이터 경로 검증 | `4` | 10초 |
| 안정성 테스트 | `5` | 40초 |
| **모든 테스트** | `all` | 125초 |

---

## 🔍 자주 묻는 질문

### Q1: Python 서버는 어디에 있나요?
**A:** `c:\Project\OCPP201(P2M)\ocpp_server.py`
```powershell
python ocpp_server.py
```

### Q2: C# 프로젝트는 어디에 있나요?
**A:** `c:\Project\OCPP201(P2M)\OCPPSimulator\`
```powershell
cd OCPPSimulator
dotnet build
```

### Q3: 데이터베이스는 어디에 있나요?
**A:** PostgreSQL `charger_db`
```powershell
psql -U postgres -d charger_db
SELECT * FROM charger_usage_log;
```

### Q4: 에너지 데이터는 어떻게 확인하나요?
**A:** 검증 스크립트 실행
```powershell
python verify_energy_data.py
```

### Q5: 모든 시나리오를 한번에 실행할 수 있나요?
**A:** 네!
```powershell
.\build_and_run.ps1 all
```

---

## ✅ 실행 전 체크리스트

```
[ ] .NET 6.0 SDK 설치됨 (dotnet --version)
[ ] Python 3.x 설치됨 (python --version)
[ ] PostgreSQL 설치됨 (psql --version)
[ ] 프로젝트 폴더 접근 가능 (c:\Project\OCPP201(P2M))
[ ] OCPPSimulator 폴더 존재 (OCPPSimulator/ 확인)
[ ] 서버 파일 존재 (ocpp_server.py 확인)
```

---

## 🆘 도움말

### 더 상세한 정보가 필요하면
→ [CSHARP_EXECUTION_MANUAL.md](CSHARP_EXECUTION_MANUAL.md) 참고

### 아키텍처를 이해하고 싶으면
→ [CSHARP_ARCHITECTURE.md](CSHARP_ARCHITECTURE.md) 참고

### 코드를 분석하고 싶으면
→ [OCPPSimulator/README_KO.md](OCPPSimulator/README_KO.md) 참고

### 문제가 발생하면
→ [CSHARP_EXECUTION_MANUAL.md](CSHARP_EXECUTION_MANUAL.md)의 "오류 및 해결" 섹션 참고

---

## 📞 빠른 명령어 레퍼런스

```powershell
# 빠른 시작 (권장)
cd c:\Project\OCPP201\(P2M)
python ocpp_server.py &                    # 백그라운드에서 서버 실행
Start-Sleep -Seconds 2
.\build_and_run.ps1 2                      # C# 클라이언트 실행
python verify_energy_data.py                # 데이터 확인

# 모든 시나리오 실행
.\build_and_run.ps1 all

# 깨끗하게 빌드
dotnet clean OCPPSimulator
dotnet build OCPPSimulator -c Release
dotnet run --project OCPPSimulator -- 2
```

---

## 📈 다음 단계

✅ **현재 완료:**
- C# OCPP 2.0.1 시뮬레이터
- 5개 테스트 시나리오
- Python 서버 통합
- 데이터베이스 저장

🎯 **제안 사항:**
1. 모든 시나리오 실행해보기
2. 아키텍처 다이어그램 이해하기
3. 소스 코드 분석해보기
4. 커스텀 시나리오 작성해보기

---

**준비 완료! 시작하세요!** 🚀

```powershell
# 이 명령어만 실행하면 됩니다:
.\build_and_run.ps1 2
```

더 알고 싶으면: [CSHARP_FINAL_GUIDE.md](CSHARP_FINAL_GUIDE.md) 📖
