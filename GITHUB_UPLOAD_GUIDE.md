# GitHub 업로드 가이드

이 프로젝트를 GitHub에 업로드하는 방법을 설명합니다.

## 📋 전제 조건

- GitHub 계정 (없으면 https://github.com 에서 가입)
- Git이 설치되어 있음 (이미 완료됨 ✓)
- GitHub Personal Access Token 생성됨

## 🚀 Step 1: GitHub Personal Access Token 생성

1. GitHub에 로그인 (https://github.com)
2. 우측 상단 프로필 → **Settings**
3. 좌측 메뉴 → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
4. **Generate new token** → **Generate new token (classic)**
5. 설정:
   - **Note**: OCPP 2.0.1 Project
   - **Expiration**: 90 days (또는 원하는 기간)
   - **Scopes**: `repo` (전체 선택)
6. **Generate token** 클릭
7. **토큰 복사** (이 화면을 떠나면 다시 볼 수 없음!)

## 🎯 Step 2: GitHub에 저장소 생성

1. GitHub 홈페이지
2. 우측 상단 **+** → **New repository**
3. 설정:
   ```
   Repository name: OCPP201-Charger-Simulator
   Description: OCPP 2.0.1 based EV Charger Simulator with Protocol Debug Logging
   Visibility: Public (공개) 또는 Private (비공개) 선택
   ```
4. **Create repository** 클릭

## 🔗 Step 3: 로컬에서 원격 저장소 연결

다음 명령을 실행합니다 (YOUR_USERNAME과 YOUR_TOKEN을 실제 값으로 교체):

```powershell
cd "c:\Project\OCPP201(P2M)"

# 원격 저장소 추가
git remote add origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/OCPP201-Charger-Simulator.git

# 원격 저장소 확인
git remote -v
```

## 📤 Step 4: GitHub에 푸시

```powershell
# main 브랜치로 이름 변경 (GitHub 기본 브랜치)
git branch -M main

# 원격 저장소에 푸시
git push -u origin main
```

## ✅ 완료!

GitHub 저장소에 성공적으로 업로드되었습니다!

업로드 후 다음 URL로 확인할 수 있습니다:
```
https://github.com/YOUR_USERNAME/OCPP201-Charger-Simulator
```

## 🔐 보안 팁

- **Token 안전**: Personal Access Token을 git 명령어에 직접 입력하지 마세요
- **대신 사용**: GitHub CLI 또는 SSH 키 권장
- **Token 무효화**: 토큰이 노출되면 즉시 GitHub에서 삭제하세요

## 🔄 SSH 키 설정 (권장)

더 안전한 방법으로 SSH를 사용할 수 있습니다:

1. SSH 키 생성:
```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. GitHub에 공개 키 추가:
   - Settings → SSH and GPG keys → New SSH key
   - 공개 키 내용 붙여넣기

3. 원격 저장소 재설정:
```powershell
git remote remove origin
git remote add origin git@github.com:YOUR_USERNAME/OCPP201-Charger-Simulator.git
git push -u origin main
```

## 📚 이후 커밋

```powershell
# 변경 사항 추가
git add .

# 커밋
git commit -m "feat: 설명"

# 푸시
git push
```

## 🆘 문제 해결

### "fatal: unable to access repository"
- 토큰이 만료되었는지 확인
- GitHub 계정 정보 확인
- 인터넷 연결 확인

### "Permission denied (publickey)"
- SSH 키가 올바르게 설정되었는지 확인
- `ssh -T git@github.com` 로 테스트

### 기타 문제
```powershell
# 원격 저장소 상태 확인
git remote -v

# 로컬 커밋 로그 확인
git log --oneline
```

---

**질문이 있으면 GitHub Issues에 등록하세요!**
