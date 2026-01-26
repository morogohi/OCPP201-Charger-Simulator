#!/bin/bash
# GitHub 업로드 스크립트 (PowerShell용)

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  OCPP 2.0.1 Charger Simulator - GitHub 업로드         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📋 GitHub 업로드 가이드" -ForegroundColor Yellow

Write-Host "`n1️⃣  GitHub에서 Personal Access Token 생성:" -ForegroundColor Green
Write-Host "   - https://github.com/settings/tokens?type=beta 방문"
Write-Host "   - 'Generate new token' 클릭"
Write-Host "   - Scopes에서 'repo' 체크"
Write-Host "   - 토큰 복사 (한 번만 표시됨)"

Write-Host "`n2️⃣  GitHub에서 새 저장소 생성:" -ForegroundColor Green
Write-Host "   - https://github.com/new 방문"
Write-Host "   - Repository name: OCPP201-Charger-Simulator"
Write-Host "   - 'Create repository' 클릭"

Write-Host "`n3️⃣  아래 명령어 실행 (YOUR_GITHUB_USERNAME, YOUR_TOKEN 교체):" -ForegroundColor Green
Write-Host "`n" 
Write-Host "git remote add origin https://YOUR_GITHUB_USERNAME:YOUR_TOKEN@github.com/YOUR_GITHUB_USERNAME/OCPP201-Charger-Simulator.git" -ForegroundColor Cyan
Write-Host "git branch -M main" -ForegroundColor Cyan
Write-Host "git push -u origin main" -ForegroundColor Cyan
Write-Host "`n"

Write-Host "또는 한 줄로:" -ForegroundColor Yellow
Write-Host "git remote add origin https://YOUR_GITHUB_USERNAME:YOUR_TOKEN@github.com/YOUR_GITHUB_USERNAME/OCPP201-Charger-Simulator.git; git branch -M main; git push -u origin main" -ForegroundColor Cyan

Write-Host "`n✅ 완료 후 확인:" -ForegroundColor Green
Write-Host "   https://github.com/YOUR_GITHUB_USERNAME/OCPP201-Charger-Simulator" -ForegroundColor Cyan

Write-Host "`n🔐 보안 팁:" -ForegroundColor Yellow
Write-Host "   - SSH 키를 사용하는 것이 더 안전합니다"
Write-Host "   - 토큰이 노출되면 즉시 GitHub에서 무효화하세요"
Write-Host "   - 자세한 가이드는 GITHUB_UPLOAD_GUIDE.md를 참고하세요"
Write-Host ""
