#!/usr/bin/env powershell
<#
.SYNOPSIS
OCPP 2.0.1 통합 실행 스크립트

.DESCRIPTION
OCPP 서버, GIS 대시보드, Python 시뮬레이터를 자동으로 실행합니다.

.PARAMETER Mode
실행 모드:
  - server: OCPP 서버만 실행
  - dashboard: GIS 대시보드만 실행  
  - simulator: Python 시뮬레이터만 실행
  - all: 모두 실행 (기본값)

.EXAMPLE
.\run_services.ps1 -Mode all
.\run_services.ps1 -Mode server

#>

param(
    [ValidateSet('server', 'dashboard', 'simulator', 'all')]
    [string]$Mode = 'all'
)

$ProjectRoot = Get-Location

# 환경변수 설정
$env:DATABASE_URL = "postgresql://charger_user:admin@localhost:5432/charger_db"
$env:OCPP_PROTOCOL_DEBUG = "false"

function Start-ServerInNewTerminal {
    param(
        [string]$ServiceName,
        [string]$PythonScript,
        [int]$DelaySeconds = 2
    )
    
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "▶ $ServiceName 시작 중..." -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
    
    $cmdString = "Set-Location '$ProjectRoot'; & '.\.venv\Scripts\Activate.ps1'; python $PythonScript"
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmdString
    
    Write-Host "✅ $ServiceName 시작됨 (새 터미널에서 실행 중)" -ForegroundColor Green
    Start-Sleep -Seconds $DelaySeconds
}

function Start-SimulatorInNewTerminal {
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "▶ Python 충전기 시뮬레이터 시작 중..." -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host ""
    
    $cmdString = @"
Set-Location '$ProjectRoot'
& '.\.venv\Scripts\Activate.ps1'
python quick_start_helper.py
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmdString
    
    Write-Host "✅ Python 시뮬레이터 시작됨 (새 터미널에서 실행 중)" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

# 필수 조건 확인
Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "필수 조건 확인" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python을 찾을 수 없습니다" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 모드별 실행
switch ($Mode) {
    'server' {
        Start-ServerInNewTerminal "OCPP 서버 (Port 9000)" "4_PYTHON_SOURCE\ocpp_server.py"
    }
    'dashboard' {
        Start-ServerInNewTerminal "GIS 대시보드 API (Port 8000)" "4_PYTHON_SOURCE\gis_dashboard_api.py"
    }
    'simulator' {
        Start-SimulatorInNewTerminal
    }
    'all' {
        Start-ServerInNewTerminal "OCPP 서버 (Port 9000)" "4_PYTHON_SOURCE\ocpp_server.py" 3
        Start-ServerInNewTerminal "GIS 대시보드 API (Port 8000)" "4_PYTHON_SOURCE\gis_dashboard_api.py" 3
        Start-SimulatorInNewTerminal
    }
}

# 완료 메시지
Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Green
Write-Host "✅ 모든 서비스가 시작되었습니다!" -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Green
Write-Host ""
Write-Host "📊 GIS 대시보드: http://localhost:8000" -ForegroundColor Green
Write-Host "📖 Swagger 문서: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  각 터미널에서 Ctrl+C를 누르면 서비스를 종료할 수 있습니다." -ForegroundColor Yellow
Write-Host ""
