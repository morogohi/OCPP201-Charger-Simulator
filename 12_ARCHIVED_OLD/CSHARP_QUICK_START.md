# C# OCPP 시뮬레이터 - 빠른 시작 (5분)

## 🚀 최속 실행 가이드

### Step 1: 파이썬 서버 시작 (30초)

**터미널 1 실행:**
```powershell
cd C:\Project\OCPP201(P2M)
python ocpp_server.py
```

**확인:** "서버 준비 완료" 메시지가 표시되어야 함

---

### Step 2: C# 클라이언트 실행 (2분)

**터미널 2 실행:**
```powershell
cd C:\Project\OCPP201(P2M)
.\build_and_run.ps1 2
```

또는:
```powershell
cd C:\Project\OCPP201(P2M)\OCPPSimulator
dotnet run -- 2
```

**확인:** 에너지가 0에서 0.4+ kWh로 누적되어야 함

---

### Step 3: 결과 확인 (1분)

**데이터베이스 확인:**
```powershell
python verify_energy_data.py
```

**예상 출력:** 에너지 데이터가 저장되었는지 확인

---

## 🎯 5가지 시나리오 한 줄 명령어

| 시나리오 | 명령어 | 시간 |
|---------|--------|------|
| 1. 기본 연결 | `.\build_and_run.ps1 1` | 5초 |
| 2. 충전 세션 | `.\build_and_run.ps1 2` | 30초 |
| 3. 다중 충전기 | `.\build_and_run.ps1 3` | 40초 |
| 4. 에너지 검증 | `.\build_and_run.ps1 4` | 10초 |
| 5. 스트레스 테스트 | `.\build_and_run.ps1 5` | 40초 |
| 모두 실행 | `.\build_and_run.ps1 all` | 2분 |

---

## 📊 예상 결과

### 시나리오 2 결과
```
[emart_jeju_01] 서버에 연결 중...
[emart_jeju_01] WebSocket 연결 성공
[emart_jeju_01] BootNotification 전송
[emart_jeju_01] 충전 시작: abc1234
[emart_jeju_01] TransactionEvent 전송 (Started): 0.00 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.14 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.28 kWh
[emart_jeju_01] TransactionEvent 전송 (Updated): 0.42 kWh
[emart_jeju_01] TransactionEvent 전송 (Ended): 0.42 kWh
[emart_jeju_01] 상태: Available, 전력: 0kW, 누적: 0.42kWh
✅ 테스트 완료!
```

---

## ✅ 성공 확인 체크리스트

- [ ] 파이썬 서버 실행 중
- [ ] WebSocket 연결 성공
- [ ] BootNotification 전송됨
- [ ] TransactionEvent 메시지 수신 확인
- [ ] 에너지 값이 증가함 (0 → 0.4+ kWh)
- [ ] 연결 해제 정상
- [ ] 데이터베이스에 기록됨

---

## 🆘 일반적인 오류 및 해결책

### 오류: "WebSocket 연결 실패"
**해결:** 파이썬 서버가 실행 중인지 확인
```powershell
# 프로세스 확인
Get-Process python

# 파이썬 서버 시작
python ocpp_server.py
```

### 오류: "포트 9000이 사용 중"
**해결:** 기존 프로세스 종료
```powershell
Stop-Process -Name python -Force
```

### 오류: ".NET SDK를 찾을 수 없음"
**해결:** .NET 설치 확인
```powershell
dotnet --version

# .NET 6.0 이상 필요
```

---

## 📚 더 알아보기

- **상세 가이드:** [CSHARP_TEST_GUIDE.md](CSHARP_TEST_GUIDE.md)
- **프로젝트 설명:** [OCPPSimulator/README_KO.md](OCPPSimulator/README_KO.md)
- **완성 보고서:** [CSHARP_SIMULATOR_COMPLETION.md](CSHARP_SIMULATOR_COMPLETION.md)

---

**이제 C# 시뮬레이터를 즉시 테스트할 수 있습니다!** 🎉
