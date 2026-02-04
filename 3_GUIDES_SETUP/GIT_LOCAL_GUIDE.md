# Git 로컬 저장소 관리 가이드

## 📋 현재 설정 상태

- **저장소 유형**: 로컬 Git 저장소 (원격 연결 없음)
- **GitHub 연동**: 비활성화 (수동으로만 관리)
- **저장 위치**: `c:\Project\OCPP201(P2M)\.git`

---

## 🔧 기본 Git 명령어

### 변경사항 확인

```powershell
# 변경된 파일 목록 확인
git status

# 상세 변경 내용 확인
git diff

# 특정 파일의 변경 내용
git diff <파일명>
```

### 변경사항 커밋

```powershell
# 모든 변경사항을 스테이징
git add -A

# 특정 파일만 스테이징
git add <파일명>

# 스테이징된 변경사항 커밋
git commit -m "커밋 메시지"

# 예시
git commit -m "feat: Add advanced dashboard with Smart Charging control"
git commit -m "fix: Update API endpoints"
git commit -m "docs: Update README"
```

### 커밋 이력 확인

```powershell
# 커밋 로그 확인 (최근 5개)
git log --oneline -5

# 상세 로그 확인
git log --pretty=format:"%h %s (%an, %ar)"

# 특정 파일의 변경 이력
git log -- <파일명>
```

### 변경사항 복구

```powershell
# 마지막 커밋 이후 모든 변경 취소
git checkout .

# 특정 파일의 변경 취소
git checkout <파일명>

# 스테이징 취소
git reset HEAD <파일명>

# 마지막 커밋 되돌리기 (변경사항 유지)
git reset --soft HEAD~1

# 마지막 커밋 완전 삭제
git reset --hard HEAD~1
```

---

## 📝 커밋 메시지 작성 규칙

### 형식

```
<타입>: <제목>

<본문>
```

### 타입 종류

| 타입 | 설명 | 예시 |
|------|------|------|
| **feat** | 새 기능 추가 | `feat: Add Smart Charging control` |
| **fix** | 버그 수정 | `fix: Fix API connection error` |
| **refactor** | 코드 리팩토링 | `refactor: Simplify chart rendering` |
| **perf** | 성능 개선 | `perf: Optimize database queries` |
| **docs** | 문서 수정 | `docs: Update installation guide` |
| **style** | 코드 스타일 변경 | `style: Format HTML code` |
| **test** | 테스트 추가/수정 | `test: Add database connection tests` |
| **chore** | 빌드/의존성 변경 | `chore: Update requirements.txt` |

### 예시

```powershell
# 좋은 예시
git commit -m "feat: Add advanced EV dashboard with real-time monitoring"
git commit -m "fix: Correct PostgreSQL connection timeout"
git commit -m "docs: Add setup instructions for Windows"

# 피해야 할 예시
git commit -m "fix stuff"
git commit -m "작업 완료"
git commit -m "update"
```

---

## 📊 일반적인 작업 흐름

### 1단계: 작업 수행
```powershell
# 파일 생성, 수정, 삭제 등의 작업 수행
# ...
```

### 2단계: 변경사항 확인
```powershell
cd c:\Project\OCPP201(P2M)
git status
```

### 3단계: 변경사항 스테이징
```powershell
# 모든 변경 스테이징
git add -A

# 또는 특정 파일만
git add advanced_dashboard.html
git add gis_dashboard_api.py
```

### 4단계: 커밋
```powershell
git commit -m "feat: Add advanced dashboard features"
```

### 5단계: 이력 확인
```powershell
git log --oneline -5
```

---

## 🔍 자주 사용되는 명령어

### 상태 확인
```powershell
# 간단한 상태
git status -s

# 상세 상태 (색상 포함)
git status
```

### 변경사항 비교
```powershell
# 마지막 커밋과 비교
git diff HEAD

# 스테이징된 변경사항 확인
git diff --cached

# 두 커밋 사이의 변경사항
git diff <커밋1> <커밋2>
```

### 분기 관리 (선택사항)
```powershell
# 현재 분기 확인
git branch

# 새 분기 생성
git branch <분기명>

# 분기 전환
git checkout <분기명>

# 분기 삭제
git branch -d <분기명>
```

---

## 💾 로컬 저장소 백업

### 전체 저장소 백업
```powershell
# 주기적으로 프로젝트 폴더를 다른 위치로 복사
Copy-Item -Path "c:\Project\OCPP201(P2M)" `
          -Destination "c:\Backup\OCPP201(P2M)-backup-$(Get-Date -Format 'yyyyMMdd')" `
          -Recurse -Force
```

### 커밋 번들 생성 (전체 이력 백업)
```powershell
# 모든 커밋 이력을 파일로 저장
git bundle create backup.bundle --all

# 복구 시
git clone backup.bundle <복구경로>
```

---

## ⚠️ 주의사항

### ✅ 할 것
- 작은 단위로 자주 커밋하기
- 명확한 커밋 메시지 작성
- 정기적으로 로컬 저장소 백업
- 중요한 코드는 별도로 저장

### ❌ 하지 말 것
- 큰 파일(동영상, 이미지 등)을 Git에 저장
- 민감한 정보(암호, API 키) 커밋
- `git reset --hard`로 많은 커밋 삭제
- 원격 저장소 없이 팀 협업 시도

---

## 🆘 문제 해결

### "Git이 인식되지 않음"
```powershell
# Git이 설치되어 있는지 확인
git --version

# 설치되지 않았으면 설치
# https://git-scm.com/download/win
```

### "파일을 커밋할 수 없음"
```powershell
# 1. 상태 확인
git status

# 2. 파일이 Add되지 않았다면 Add
git add <파일명>

# 3. 커밋
git commit -m "메시지"
```

### "실수로 커밋했을 때"
```powershell
# 마지막 커밋 취소 (변경사항 유지)
git reset --soft HEAD~1

# 파일 수정
# ...

# 다시 커밋
git commit -m "새로운 메시지"
```

### "이전 커밋으로 돌아가고 싶을 때"
```powershell
# 마지막 3개 커밋 전으로 이동
git reset --soft HEAD~3

# 또는 특정 커밋으로 이동
git reset --soft <커밋해시>

# 변경사항 유지하면서 되돌리기
```

---

## 📚 참고 자료

- [Git 공식 문서](https://git-scm.com/doc)
- [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials)
- [GitHub 가이드](https://docs.github.com/en)

---

## 📌 현재 저장소 정보

```
저장소 경로: c:\Project\OCPP201(P2M)
저장소 타입: 로컬 Git 저장소
원격 연결: 없음
현재 분기: main (기본값)
```

## 🎯 다음 작업

원격 저장소를 다시 추가하려면:

```powershell
# GitHub에 리포지토리 생성 후 실행
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

---

**마지막 업데이트**: 2026-01-19  
**Git 버전**: 2.x+  
**OS**: Windows PowerShell
