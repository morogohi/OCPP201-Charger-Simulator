# C# OCPP 시뮬레이터 테스트 실행 가이드

## 사전 요구사항

### 1. .NET SDK 확인
```powershell
dotnet --version
```

필요한 버전:
- ✅ .NET 6.0 이상
- 현재 설치: .NET 10.0.102

### 2. 의존성 확인
```bash
cd C:\Project\OCPP201(P2M)\OCPPSimulator
dotnet restore
```

### 3. 파이썬 OCPP 서버 실행 (필수)
```powershell
# 별도 터미널에서
cd C:\Project\OCPP201(P2M)
python ocpp_server.py
```

**출력 예시:**
```
[INFO] OCPP 2.0.1 서버 시작: ws://127.0.0.1:9000
[INFO] 서버 준비 완료. 클라이언트 연결 대기 중...
```

---

## 빌드 및 실행

### 방법 1: PowerShell 스크립트 사용 (추천)

```powershell
# 기본 실행 (시나리오 1)
.\build_and_run.ps1

# 특정 시나리오 실행
.\build_and_run.ps1 2
.\build_and_run.ps1 3
.\build_and_run.ps1 all
```

### 방법 2: 배치 파일 사용 (Windows)

```cmd
REM 기본 실행
build_and_test.bat

REM 특정 시나리오
build_and_test.bat 2
build_and_test.bat all
```

### 방법 3: 직접 명령어 사용

```powershell
cd C:\Project\OCPP201(P2M)\OCPPSimulator

# 빌드
dotnet build -c Release

# 실행
dotnet run -- 1
dotnet run -- 2
dotnet run -- all
```

---

## 5가지 테스트 시나리오

### 시나리오 1: 기본 연결 및 BootNotification

**실행:**
```powershell
dotnet run -- 1
```

**예상 결과:**
```
[emart_jeju_01] 서버에 연결 중... (ws://127.0.0.1:9000/emart_jeju_01)
[emart_jeju_01] WebSocket 연결 성공
[emart_jeju_01] BootNotification 전송
[emart_jeju_01] 메시지 수신: [3,"abc123",...
[emart_jeju_01] CALLRESULT 수신: abc123
[emart_jeju_01] 상태: Available, 전력: 0kW, 누적: 0.00kWh
[emart_jeju_01] 연결 해제
✅ 테스트 완료!
```

**테스트 항목:**
- ✅ WebSocket 연결
- ✅ BootNotification 전송
- ✅ CALLRESULT 수신
- ✅ 정상 연결 해제

---

### 시나리오 2: 충전 세션 (에너지 추적)

**실행:**
```powershell
dotnet run -- 2
```

**예상 결과:**
```
[emart_jeju_01] 서버에 연결 중...
[emart_jeju_01] WebSocket 연결 성공
[emart_jeju_01] BootNotification 전송
[emart_jeju_01] 충전 시작: abc1234
[emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.14 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.28 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.42 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.56 kWh
[emart_jeju_01] 충전 중지 요청
[emart_jeju_01] TransactionEvent 전송 (Ended): 0.56 kWh
[emart_jeju_01] 상태: Available, 전력: 0kW, 누적: 0.56kWh
[emart_jeju_01] 연결 해제
✅ 테스트 완료!
```

**시간:** 약 25-30초

**테스트 항목:**
- ✅ 충전 시작 (Started 이벤트)
- ✅ 에너지 누적 (0 → 0.56 kWh)
- ✅ 주기적 업데이트 (5초마다)
- ✅ 충전 중지 (Ended 이벤트)
- ✅ 비용 계산 (0.56 * 150 = 84원)

---

### 시나리오 3: 다중 충전기 동시 운영

**실행:**
```powershell
dotnet run -- 3
```

**예상 결과:**
```
[emart_jeju_01] 서버에 연결 중...
[emart_jeju_02] 서버에 연결 중...
[emart_shinjeju_01] 서버에 연결 중...
[emart_jeju_01] WebSocket 연결 성공
[emart_jeju_02] WebSocket 연결 성공
[emart_shinjeju_01] WebSocket 연결 성공

[emart_jeju_01] 충전 시작: abc1234
[emart_jeju_02] 충전 시작: def5678
[emart_shinjeju_01] 충전 시작: ghi9012

[최종 상태]
[emart_jeju_01] 상태: Available, 전력: 0kW, 누적: 1.12kWh
[emart_jeju_02] 상태: Available, 전력: 0kW, 누적: 1.12kWh
[emart_shinjeju_01] 상태: Available, 전력: 0kW, 누적: 0.56kWh

✅ 테스트 완료!
```

**시간:** 약 35-40초

**테스트 항목:**
- ✅ 다중 충전기 동시 연결
- ✅ 병렬 충전 시작
- ✅ 독립적 에너지 추적
- ✅ 서버 동시 메시지 처리
- ✅ 병렬 충전 중지

**충전기 사양:**
- emart_jeju_01: 100kW
- emart_jeju_02: 100kW
- emart_shinjeju_01: 50kW (절반 전력)

---

### 시나리오 4: 에너지 데이터 검증

**실행:**
```powershell
dotnet run -- 4
```

**예상 결과:**
```
[에너지 데이터 검증 테스트]
[emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.50 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 1.00 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 1.50 kWh
[emart_jeju_01] TransactionEvent 전송 (Ended): 1.50 kWh

[테스트 완료]
[emart_jeju_01] 연결 해제
✅ 테스트 완료!
```

**시간:** 약 10초

**테스트 항목:**
- ✅ 명시적 에너지 값 전송
- ✅ 0 → 0.5 → 1.0 → 1.5 kWh 진행
- ✅ 정확한 데이터 전달 확인
- ✅ 서버 에너지 수신 확인

---

### 시나리오 5: 스트레스 테스트 (5개 거래)

**실행:**
```powershell
dotnet run -- 5
```

**예상 결과:**
```
[스트레스 테스트] 5개 거래 반복
================================================================================

--- 거래 1/5 ---
[emart_jeju_01] 충전 시작: abc1234
[emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.14 kWh
[emart_jeju_01] 충전 중지 요청
[emart_jeju_01] TransactionEvent 전송 (Ended): 0.14 kWh
[emart_jeju_01] 상태: Available, 전력: 0kW, 누적: 0.14kWh

--- 거래 2/5 ---
[emart_jeju_01] 충전 시작: def5678
[emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.14 kWh
...
```

**시간:** 약 35-40초 (거래당 7초)

**테스트 항목:**
- ✅ 반복 거래 처리
- ✅ 상태 초기화
- ✅ 메모리 누수 확인
- ✅ 안정성 검증

---

### 모든 시나리오 실행

**실행:**
```powershell
dotnet run -- all
```

**예상 시간:** 약 2-3분

**순서:**
1. 시나리오 1 실행 (5초)
2. 3초 대기
3. 시나리오 2 실행 (30초)
4. 3초 대기
5. 시나리오 3 실행 (40초)
6. 3초 대기
7. 시나리오 4 실행 (10초)

---

## 파이썬 서버와 C# 클라이언트 테스트

### 1단계: 파이썬 서버 시작 (터미널 1)

```powershell
cd C:\Project\OCPP201(P2M)
python ocpp_server.py
```

**확인 메시지:**
```
[INFO] OCPP 2.0.1 서버 시작: ws://127.0.0.1:9000
[INFO] 서버 준비 완료. 클라이언트 연결 대기 중...
```

### 2단계: C# 클라이언트 실행 (터미널 2)

```powershell
cd C:\Project\OCPP201(P2M)
.\build_and_run.ps1 2
```

### 3단계: 결과 확인

**서버 로그 (터미널 1):**
```
[INFO] 새로운 클라이언트 연결: emart_jeju_01
[INFO] [emart_jeju_01] BootNotification 수신
[INFO] [emart_jeju_01] TransactionEvent (Started) 수신: 0.00 kWh
[INFO] [emart_jeju_01] TransactionEvent (Updated) 수신: 0.14 kWh
[INFO] [emart_jeju_01] TransactionEvent (Updated) 수신: 0.28 kWh
[INFO] [emart_jeju_01] TransactionEvent (Updated) 수신: 0.42 kWh
[INFO] [emart_jeju_01] TransactionEvent (Ended) 수신: 0.42 kWh
[INFO] 클라이언트 연결 해제: emart_jeju_01
```

**클라이언트 로그 (터미널 2):**
```
[emart_jeju_01] 서버에 연결 중...
[emart_jeju_01] WebSocket 연결 성공
[emart_jeju_01] BootNotification 전송
[emart_jeju_01] 충전 시작: abc1234
[emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.42 kWh
[emart_jeju_01] TransactionEvent 전송 (Ended): 0.42 kWh
[emart_jeju_01] 연결 해제
✅ 테스트 완료!
```

---

## 데이터베이스 검증

### 에너지 데이터 확인

```powershell
cd C:\Project\OCPP201(P2M)
python verify_energy_data.py
```

**출력 예시:**
```
데이터베이스 총 거래 기록: 342개

충전기별 에너지 통계:
────────────────────────────────────────────────────────────
충전기 ID              거래수    총에너지        평균        최대
────────────────────────────────────────────────────────────
emart_jeju_01          46     1202.08kWh    26.13kWh   49.95kWh
emart_jeju_02          38     1165.12kWh    30.66kWh   49.87kWh
emart_shinjeju_01      39     1157.28kWh    29.67kWh   49.49kWh

최근 10개 거래:
────────────────────────────────────────────────────────────
#    충전기 ID              에너지        비용         시간
────────────────────────────────────────────────────────────
1    emart_jeju_01          0.42 kWh      63원      2026-01-21 10:35:42
2    emart_jeju_02          0.42 kWh      63원      2026-01-21 10:35:15
...

✅ 서버에서 에너지 데이터를 정상적으로 수신하고 저장하고 있습니다!
```

---

## 트러블슈팅

### 문제 1: "WebSocket 연결 실패"

**원인:**
- 파이썬 서버가 실행되지 않음
- 포트 9000이 사용 중

**해결책:**
```powershell
# 기존 프로세스 종료
Stop-Process -Name python -Force

# 파이썬 서버 재시작
python ocpp_server.py
```

### 문제 2: "메시지 전송 오류"

**원인:**
- 서버와 클라이언트 버전 불일치
- JSON 직렬화 오류

**해결책:**
```powershell
# 의존성 재설치
cd OCPPSimulator
dotnet restore
dotnet clean
dotnet build -c Release
```

### 문제 3: "에너지 데이터가 0으로 표시됨"

**원인:**
- 충전 시뮬레이션이 완료되지 않음
- 타이밍 문제

**해결책:**
```powershell
# 더 긴 시간으로 시나리오 2 실행
# 시뮬레이션 대기 시간을 30초로 증가
dotnet run -- 2
```

---

## 성능 측정

### 실행 시간 및 메모리

| 시나리오 | 시간 | 메모리 | 메시지 수 |
|---------|------|--------|----------|
| 1 | 5초 | ~5MB | 2 |
| 2 | 30초 | ~10MB | 8 |
| 3 | 40초 | ~20MB | 24 |
| 4 | 10초 | ~5MB | 5 |
| 5 | 40초 | ~30MB | 40 |
| all | 2-3분 | ~50MB | 79 |

---

## 고급 기능 테스트

### 고급 예제 실행 (향후)

Program.cs의 AdvancedExamplesRunner를 사용하여:

```csharp
// 예제 1: 커스텀 서버 연결
await AdvancedExamples.Example1_CustomServerAsync();

// 예제 2: 30초 충전 세션
await AdvancedExamples.Example2_LongChargingSessionAsync();

// 예제 3: 충전기 비교
await AdvancedExamples.Example3_ChargerComparisonAsync();

// 예제 4: 충전소 운영
await AdvancedExamples.Example4_ChargingStationAsync();

// 예제 5: 성능 벤치마크
await AdvancedExamples.Example5_PerformanceBenchmarkAsync();

// 예제 6: 에러 처리
await AdvancedExamples.Example6_ErrorHandlingAsync();
```

---

## 로그 분석

### 성공 신호

✅ 모든 메시지가 정상적으로 수신되어야 함
✅ CALLRESULT가 모든 CALL에 응답해야 함
✅ 에너지가 계속 누적되어야 함
✅ 연결 해제가 정상적으로 진행되어야 함

### 경고 신호

⚠️ 메시지 수신 오류
⚠️ 타임아웃
⚠️ JSON 파싱 오류
⚠️ 연결 해제 오류

---

## 참고 자료

- [OCPPSimulator/README_KO.md](OCPPSimulator/README_KO.md) - 상세 문서
- [test_csharp_integration.py](test_csharp_integration.py) - 파이썬 비교 구현
- [ocpp_server.py](ocpp_server.py) - OCPP 서버
- [verify_energy_data.py](verify_energy_data.py) - 데이터 검증 도구

---

**시뮬레이터 테스트 준비 완료!** ✅
