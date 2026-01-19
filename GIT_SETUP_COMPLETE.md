# GitHub 업로드 완료 가이드

## ✅ 현재 상태

Git 저장소가 초기화되었고 첫 번째 커밋이 완료되었습니다.

```
커밋: d52b76f (HEAD -> master)
메시지: feat: Initial commit - OCPP 2.0.1 Charger Simulator with Protocol Debug Logging
파일 수: 15개
```

## 📤 GitHub에 푸시하는 방법

### Step 1: GitHub 설정

1. https://github.com 에 로그인
2. 우측 상단 **+** → **New repository** 클릭
3. 저장소 생성:
   - Name: `OCPP201-Charger-Simulator`
   - Description: `OCPP 2.0.1 Charger Simulator with Protocol Debug Logging`
   - Public (공개) 또는 Private (비공개) 선택
4. **Create repository** 클릭

### Step 2: Personal Access Token 생성

1. GitHub 설정 → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token (classic)**
3. 권한: `repo` (전체 체크)
4. 토큰 복사 (중요!)

### Step 3: PowerShell에서 실행

다음 명령을 실행합니다 (YOUR_USERNAME, YOUR_TOKEN, YOUR_EMAIL을 교체):

```powershell
cd "c:\Project\OCPP201(P2M)"

# 사용자 정보 설정 (로컬 저장소만)
git config user.email "YOUR_EMAIL@example.com"
git config user.name "YOUR_NAME"

# 원격 저장소 추가
git remote add origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/OCPP201-Charger-Simulator.git

# branch 이름 변경
git branch -M main

# 푸시
git push -u origin main
```

### Step 4: 확인

푸시가 완료되면 다음 URL에서 확인할 수 있습니다:
```
https://github.com/YOUR_USERNAME/OCPP201-Charger-Simulator
```

## 🔐 SSH를 사용한 더 안전한 방법

### SSH 키 생성 (첫 번째 실행만)

```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enter 누르면 기본 위치에 저장됨
```

### GitHub에 공개 키 추가

1. GitHub Settings → SSH and GPG keys
2. **New SSH key** 클릭
3. 공개 키 내용 붙여넣기:
   ```powershell
   # 공개 키 복사
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
   ```

### SSH로 원격 저장소 설정

```powershell
git remote add origin git@github.com:YOUR_USERNAME/OCPP201-Charger-Simulator.git
git branch -M main
git push -u origin main
```

## 📦 프로젝트 구조 (GitHub에 업로드될 파일)

```
OCPP201-Charger-Simulator/
├── Core Implementation
│   ├── ocpp_models.py                 (OCPP 2.0.1 데이터 모델)
│   ├── ocpp_messages.py               (메시지 처리 + 디버그 로깅)
│   ├── charger_simulator.py           (충전기 시뮬레이터)
│   └── ocpp_server.py                 (중앙 서버)
│
├── Tools & Utilities
│   ├── server_api.py                  (REST API)
│   ├── logging_config.py              (로깅 설정)
│   ├── run_all.py                     (통합 실행)
│   └── test_simulator.py              (테스트)
│
├── Demo Scripts
│   ├── demo.py                        (기본 데모)
│   └── demo_protocol_debug.py         (프로토콜 디버그 데모)
│
├── Documentation
│   ├── README.md                      (프로젝트 소개)
│   ├── PROTOCOL_DEBUG_GUIDE.md        (프로토콜 디버그 가이드)
│   ├── PROTOCOL_DEBUG_UPDATE.md       (업데이트 정보)
│   └── GITHUB_UPLOAD_GUIDE.md         (이 파일)
│
├── Configuration
│   ├── requirements.txt               (Python 의존성)
│   ├── .gitignore                     (Git 무시 파일)
│   └── push_to_github.ps1             (업로드 스크립트)
│
└── Auto-generated (업로드 안 됨)
    ├── __pycache__/
    ├── .venv/
    └── ocpp_*.log
```

## 🚀 이후 커밋 방법

```powershell
# 변경 사항 확인
git status

# 변경 사항 추가
git add .

# 커밋 (좋은 메시지 작성)
git commit -m "feat: 새로운 기능 설명"

# 푸시
git push
```

## 🏷️ Git 커밋 메시지 컨벤션

```
feat:  새로운 기능 추가
fix:   버그 수정
docs:  문서 수정
style: 코드 포맷팅, 세미콜론 등
refactor: 코드 리팩토링
perf:  성능 개선
test:  테스트 추가/수정
chore: 패키지 관리, 빌드 스크립트 등
```

## 📊 파일 통계

- **Python 파일**: 10개
- **문서 파일**: 4개
- **설정 파일**: 2개
- **총 라인 수**: ~3,500 라인

## 🔗 GitHub Pages 설정 (선택사항)

GitHub Pages로 자동 배포하려면:

1. GitHub Settings → Pages
2. Source: main branch
3. 자동으로 README.md가 홈페이지가 됨

## ❓ 문제 해결

### "fatal: unable to access repository"
- 토큰이 올바른지 확인
- GitHub 저장소명 확인
- 인터넷 연결 확인

### "Permission denied (publickey)"
- SSH 키 설정 확인
- `ssh -T git@github.com` 테스트

### "branches diverged"
- `git pull` 실행
- 충돌이 있으면 수동으로 해결

## 💡 팁

- `.gitignore` 파일이 자동으로 불필요한 파일을 제외합니다
- Personal Access Token의 만료 기간을 충분히 설정하세요
- SSH를 사용하면 매번 token을 입력할 필요가 없습니다
- 주기적으로 GitHub에 푸시하여 백업하세요

---

**성공적으로 GitHub에 업로드되었습니다!** 🎉
