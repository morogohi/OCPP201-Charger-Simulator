# ⚡ 5분 안에 통합 시스템 시작하기

**목표**: OCPP 서버 + GIS 대시보드 + Python 시뮬레이터를 5분 안에 실행하고 데이터 확인

---

## 🚀 최종 한 줄 명령어

```powershell
cd "c:\Project\OCPP201(P2M)" && .\run_integrated.ps1 -Mode all
```

**완료!** 🎉 4개의 터미널이 자동으로 열리고 모든 서비스가 시작됩니다.

---

## 단계별 확인

### ✅ Step 1: OCPP 서버 확인 (Terminal 1)
```
OCPP 2.0.1 서버 시작: ws://0.0.0.0:9000
✅ 나타나면 성공
```

### ✅ Step 2: GIS 대시보드 확인 (Terminal 2)
```
Uvicorn running on http://0.0.0.0:8000
✅ 나타나면 성공
```

### ✅ Step 3: Python 시뮬레이터 확인 (Terminal 3)
```
Python 충전기 시뮬레이터 시작
[PYTHON_SIM_001] 서버 연결 중...
[PYTHON_SIM_001] ✅ 연결 완료
✅ 나타나면 성공
```

### ✅ Step 4: 브라우저에서 GIS 대시보드 열기
```
http://localhost:8000
```

---

## 🎯 무엇을 확인해야 하나?

| 항목 | 확인 내용 |
|------|---------|
| 🗺️ **지도** | 제주 지역 지도와 3개 충전소 마커 |
| 📊 **통계** | 우측 상단 KPI (활성 충전기, 에너지, 매출) |
| 📈 **차트** | 시간별 전력 사용량 (꺾은선 그래프) |
| 📋 **테이블** | 충전 거래 기록 (PYTHON_SIM_001 포함) |

---

## 💡 한 번에 여러 시뮬레이터 실행

```powershell
# 3개의 시뮬레이터 동시 실행
.\run_integrated.ps1 -Mode all -SimulatorCount 3
```

결과: PYTHON_SIM_001, PYTHON_SIM_002, PYTHON_SIM_003가 동시에 실행되고, GIS 대시보드에 3개의 마커가 표시됩니다.

---

## 🔙 처음부터 정확하게 하려면

```powershell
# 1. 프로젝트 폴더로 이동
cd "c:\Project\OCPP201(P2M)"

# 2. 가상환경 활성화
.\.venv\Scripts\Activate.ps1

# 3. 데이터베이스 초기화 (선택)
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
python 6_PYTHON_SCRIPTS\init_jeju_chargers.py

# 4. 검증 스크립트 실행 (모든 모듈이 정상인지 확인)
python verify_setup.py

# 5. 통합 스크립트 실행
.\run_integrated.ps1 -Mode all
```

---

## ❌ 문제 발생 시

### OCPP 서버가 시작되지 않음
```powershell
# Terminal 1에서 직접 실행해보기
python 4_PYTHON_SOURCE\ocpp_server.py
# 에러 메시지 확인 후 해결
```

### GIS 대시보드 접속 불가
```powershell
# 포트 8000이 사용 중인지 확인
netstat -ano | findstr "8000"

# 방화벽 확인
# Windows Defender → 고급 설정 → 인바운드 규칙에서 포트 8000 허용
```

### 데이터가 표시되지 않음
```powershell
# 데이터베이스 초기화
python 6_PYTHON_SCRIPTS\init_jeju_chargers.py

# GIS 대시보드 새로고침 (F5)
```

---

## 📚 더 자세한 가이드

자세한 단계별 설명은 이 파일을 참고하세요:
👉 [INTEGRATED_EXECUTION_GUIDE.md](INTEGRATED_EXECUTION_GUIDE.md)

---

**🎉 이제 즉시 시작할 준비가 되었습니다!**
