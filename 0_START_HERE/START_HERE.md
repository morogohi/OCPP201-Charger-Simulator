# 📖 시작 가이드 - 수작업 테스트

**이 문서를 먼저 읽으세요!**

---

## 🎯 당신의 상황은?

### ⏱️ **시간이 5분 밖에 없다**
```
👉 QUICK_TEST.md를 열고 5개 단계를 따라하세요
   (복사-붙여넣기만 하면 됨)
```

### 🤖 **자동으로 테스트하고 싶다**
```
👉 PowerShell에서 이 명령어를 실행하세요:
   
   .\.venv\Scripts\Activate.ps1
   python manual_test.py
```

### 🔍 **시스템을 완벽히 이해하며 테스트하고 싶다**
```
👉 MANUAL_TEST_GUIDE.md를 열고 단계별로 진행하세요
   (30-60분 소요)
```

### ❓ **어떤 방식이 나에게 맞는지 모르겠다**
```
👉 TEST_METHODS_COMPARISON.md를 읽으세요
   (2분이면 방식을 선택할 수 있습니다)
```

---

## 📚 생성된 문서 설명

### 1️⃣ **CODE_TEST_REPORT.md** (이미 읽으셨을 것)
- 자동 테스트의 결과 리포트
- 8개 항목 모두 ✅ 통과
- 현황 파악용

### 2️⃣ **QUICK_TEST.md** ⭐ 추천
- 5분 안에 끝내기
- 5개의 간단한 Python 코드 블록
- 복사-붙여넣기만 하면 됨
- 가장 인기 있는 방식

### 3️⃣ **manual_test.py** ⭐ 추천
- 1줄 명령어: `python manual_test.py`
- 3-5분 안에 자동 테스트
- 가장 쉬운 방식
- 자세한 결과 출력

### 4️⃣ **MANUAL_TEST_GUIDE.md** 
- 가장 상세한 가이드
- 6개의 개별 테스트
- 문제 해결 방법 포함
- 시간이 충분할 때 진행

### 5️⃣ **TEST_GUIDE_SUMMARY.md**
- 모든 가이드의 개요
- 어떤 문서를 선택해야 하는지 설명
- 체크리스트 포함

### 6️⃣ **TEST_METHODS_COMPARISON.md**
- 모든 테스트 방식 비교
- 상황별/목표별 추천
- 의사결정 가이드

---

## ✨ 가장 쉬운 방법 (추천)

### Step 1️⃣: 가상환경 활성화 (10초)
```powershell
cd "c:\Project\OCPP201(P2M)"
.\.venv\Scripts\Activate.ps1
```

### Step 2️⃣: 테스트 실행 (3분)
```powershell
python manual_test.py
```

### Step 3️⃣: 결과 확인 (30초)
```
✅ 모든 테스트 성공하면 완료!
❌ 실패하면 MANUAL_TEST_GUIDE.md 참고
```

**총 소요시간: 4분** ⏱️

---

## ⚡ 초(超)빠른 방법

### Step 1️⃣: 파일 열기
→ `QUICK_TEST.md` 파일 열기

### Step 2️⃣: 복사-붙여넣기
→ 5개 코드 블록을 순서대로 복사해서 PowerShell에 붙여넣기

### Step 3️⃣: 완료!
→ 예상 결과와 비교

**총 소요시간: 5분** ⏱️

---

## 📋 체크리스트

### 사전 준비
- [ ] PowerShell 열음
- [ ] 디렉토리 변경: `cd "c:\Project\OCPP201(P2M)"`
- [ ] 가상환경 활성화: `.\.venv\Scripts\Activate.ps1`

### 테스트 선택 (1개 선택)
- [ ] QUICK_TEST.md 수행 (5분)
  OR
- [ ] manual_test.py 실행 (3분)
  OR
- [ ] MANUAL_TEST_GUIDE.md 진행 (30분)

### 결과 확인
- [ ] 모든 항목이 ✅ 성공
- [ ] 예상 결과와 일치

---

## 🎓 각 방식의 학습 곡선

```
쉬움 ↑
     │
     │  manual_test.py
     │  (자동 실행)
     │
     │  QUICK_TEST.md
     │  (복사-붙여넣기)
     │
     │  MANUAL_TEST_GUIDE.md
     │  (상세 학습)
     │
어려움 └──────────────────→ 시간
```

---

## 💡 팁

### 팁 1: 시간이 없다면?
→ `manual_test.py` 실행 (3분)

### 팁 2: 복사-붙여넣기가 싫다면?
→ `python manual_test.py` 실행 (자동)

### 팁 3: 깊이 있게 배우고 싶다면?
→ `MANUAL_TEST_GUIDE.md` 읽고 진행 (60분)

### 팁 4: 문제가 발생했다면?
→ `MANUAL_TEST_GUIDE.md`의 "문제 해결" 섹션 참고

---

## 🚀 지금 바로 시작하세요!

### 옵션 A: 가장 빠른 방법 (3분)
```powershell
.\.venv\Scripts\Activate.ps1
python manual_test.py
```

### 옵션 B: 가장 쉬운 방법 (5분)
1. QUICK_TEST.md 열기
2. 5개 코드 블록 복사-붙여넣기
3. 결과 확인

### 옵션 C: 가장 완벽한 방법 (60분)
1. MANUAL_TEST_GUIDE.md 열기
2. Test 1부터 Test 6까지 진행
3. 모든 항목 이해

---

## ❓ FAQ

**Q: 어떤 방식을 선택해야 하나?**
A: 시간이 없으면 옵션 A (3분), 시간이 있으면 옵션 C (60분)

**Q: PostgreSQL이 없어도 테스트할 수 있나?**
A: Test 2 (DB 연결)를 제외한 나머지는 가능합니다

**Q: 테스트에 실패했다**
A: MANUAL_TEST_GUIDE.md의 "문제 해결" 섹션을 참고하세요

**Q: 테스트 결과를 어디에 저장하나?**
A: 콘솔 출력을 스크린샷으로 캡처하거나 로그 파일로 저장할 수 있습니다

---

## 🎯 다음 단계

### 테스트 완료 후:
1. 결과 확인 (성공/실패)
2. 필요시 MANUAL_TEST_GUIDE.md 참고
3. 개발/배포 진행

### 궁금한 점:
1. CODE_TEST_REPORT.md - 자동 테스트 결과
2. MANUAL_TEST_GUIDE.md - 상세 가이드
3. TEST_METHODS_COMPARISON.md - 방식 비교

---

**준비 완료! 이제 시작하세요!** 🚀

가장 편한 방식을 선택해서:
- `QUICK_TEST.md` 또는
- `python manual_test.py` 또는
- `MANUAL_TEST_GUIDE.md`

를 진행하면 됩니다!
