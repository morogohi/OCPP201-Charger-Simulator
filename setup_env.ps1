#!/usr/bin/env powershell
<#
.SYNOPSIS
OCPP 2.0.1 통합 실행 - 간단한 버전 (문제 해결)

.DESCRIPTION
PowerShell 실행 정책 문제를 피하고 간단하게 서비스를 시작합니다.
#>

# 현재 위치 확인
$projectRoot = Get-Location
Write-Host "프로젝트 경로: $projectRoot" -ForegroundColor Cyan

# 가상환경 확인
if (!(Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "❌ 가상환경이 없습니다!" -ForegroundColor Red
    Write-Host "생성 중..." -ForegroundColor Yellow
    python -m venv .venv
}

# 가상환경 활성화
& ".\.venv\Scripts\Activate.ps1"
Write-Host "✅ 가상환경 활성화됨" -ForegroundColor Green

# 환경변수 설정
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
$env:OCPP_PROTOCOL_DEBUG = "false"
Write-Host "✅ 환경변수 설정됨" -ForegroundColor Green

# 설정 검증
Write-Host ""
Write-Host "설정 검증 중..." -ForegroundColor Yellow
python verify_setup.py | Select-Object -Last 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "다음 명령어로 서비스를 시작할 수 있습니다:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[Terminal 1] OCPP 서버 (Port 9000)" -ForegroundColor Green
Write-Host "  python 4_PYTHON_SOURCE\ocpp_server.py" -ForegroundColor White
Write-Host ""
Write-Host "[Terminal 2] GIS 대시보드 (Port 8000)" -ForegroundColor Green
Write-Host "  python 4_PYTHON_SOURCE\gis_dashboard_api.py" -ForegroundColor White
Write-Host ""
Write-Host "[Terminal 3] Python 시뮬레이터" -ForegroundColor Green
Write-Host "  python 6_PYTHON_SCRIPTS\test_simulator.py" -ForegroundColor White
Write-Host ""
Write-Host "[Terminal 4 선택] 실시간 모니터링" -ForegroundColor Green
Write-Host "  python monitor_realtime.py" -ForegroundColor White
Write-Host ""
Write-Host "또는 다음 가이드를 참고하세요:" -ForegroundColor Cyan
Write-Host "  📖 QUICK_START_INTEGRATED.md" -ForegroundColor White
Write-Host "  📖 1_GUIDES_SERVER\INTEGRATED_EXECUTION_GUIDE.md" -ForegroundColor White
Write-Host ""
