#!/usr/bin/env pwsh
<#
.SYNOPSIS
    OCPP C# Simulator 빌드 및 테스트 스크립트

.DESCRIPTION
    프로젝트를 빌드하고 지정된 시나리오를 실행합니다.

.PARAMETER Scenario
    실행할 시나리오 번호 (1-5) 또는 'all'
    기본값: 1

.EXAMPLE
    .\build_and_run.ps1 2
    .\build_and_run.ps1 all

#>

param(
    [ValidateSet('1', '2', '3', '4', '5', 'all')]
    [string]$Scenario = '1'
)

$ErrorActionPreference = 'Stop'

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $($Text.PadRight(78)) ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Text, [int]$Number)
    Write-Host "[$Number/3] $Text" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

# 메인 로직
try {
    Write-Header "OCPP 2.0.1 C# Simulator 빌드 및 테스트"

    $projectDir = Join-Path (Get-Location) "OCPPSimulator"
    $buildDir = Join-Path $projectDir "bin\Release\net8.0"

    Write-Step "의존성 복원 중" 1
    Push-Location $projectDir
    
    dotnet restore
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "의존성 복원 실패"
        exit 1
    }
    Write-Success "의존성 복원 완료"

    Write-Step "프로젝트 빌드 중" 2
    dotnet build -c Release
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "빌드 실패"
        exit 1
    }
    Write-Success "빌드 완료"

    Pop-Location

    Write-Step "테스트 시나리오 실행" 3

    $exe = Join-Path $buildDir "OCPPSimulator.exe"
    
    if (-not (Test-Path $exe)) {
        Write-Error-Custom "실행 파일을 찾을 수 없습니다: $exe"
        exit 1
    }

    Write-Host ""
    Write-Host "사용 가능한 시나리오:" -ForegroundColor Cyan
    Write-Host "  1 - 기본 연결 및 BootNotification"
    Write-Host "  2 - 충전 세션 (에너지 추적)"
    Write-Host "  3 - 다중 충전기 동시 운영"
    Write-Host "  4 - 에너지 데이터 검증"
    Write-Host "  5 - 스트레스 테스트 (5개 거래)"
    Write-Host "  all - 모든 시나리오 실행"
    Write-Host ""
    Write-Host "실행 중인 시나리오: $Scenario" -ForegroundColor Green

    & $exe $Scenario

    Write-Success "테스트 완료!"
}
catch {
    Write-Error-Custom "오류 발생: $_"
    exit 1
}
