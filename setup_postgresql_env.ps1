#!/usr/bin/env powershell
<#
.SYNOPSIS
PostgreSQL 및 데이터베이스 환경 설정 스크립트

.DESCRIPTION
Windows 시스템에 PostgreSQL PATH 및 DATABASE_URL 환경변수를 설정합니다.

.NOTES
관리자 권한이 필요합니다.
#>

param(
    [switch]$TemporaryOnly = $false,
    [switch]$Permanent = $false
)

# 설치 경로
$pgBin = "C:\Program Files\PostgreSQL\18\bin"
$dbUrl = "postgresql://charger_user:admin@localhost:5432/charger_db"

Write-Host "╔════════════════════════════════════════════════════════════════╗"
Write-Host "║        PostgreSQL 및 데이터베이스 환경 설정                     ║"
Write-Host "╚════════════════════════════════════════════════════════════════╝"
Write-Host ""

# PostgreSQL 설치 확인
if (!(Test-Path $pgBin)) {
    Write-Host "❌ PostgreSQL이 설치되지 않았습니다."
    Write-Host "   설치 경로: $pgBin"
    exit 1
}

Write-Host "✅ PostgreSQL 설치 경로 확인"
Write-Host "   $pgBin"
Write-Host ""

# 현재 PATH 확인
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
$pgPathExists = $currentPath -like "*PostgreSQL\18\bin*"

if ($pgPathExists) {
    Write-Host "✅ PostgreSQL PATH가 이미 설정되어 있습니다."
} else {
    Write-Host "⚠️  PostgreSQL PATH가 설정되지 않았습니다."
}

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════════"
Write-Host "설정 옵션"
Write-Host "═════════════════════════════════════════════════════════════════"
Write-Host ""

# 설정 방식 선택
if ($TemporaryOnly) {
    $setupMode = "temporary"
} elseif ($Permanent) {
    $setupMode = "permanent"
} else {
    Write-Host "1. 임시 설정 (현재 PowerShell 세션만)"
    Write-Host "2. 영구 설정 (시스템 환경변수 - 관리자 권한 필요)"
    Write-Host "3. 둘 다 설정"
    Write-Host ""
    $choice = Read-Host "선택 (1-3, 기본값=3)"
    
    if ([string]::IsNullOrEmpty($choice)) {
        $setupMode = "both"
    } else {
        switch ($choice) {
            "1" { $setupMode = "temporary" }
            "2" { $setupMode = "permanent" }
            default { $setupMode = "both" }
        }
    }
}

Write-Host ""

# 임시 설정
if ($setupMode -eq "temporary" -or $setupMode -eq "both") {
    Write-Host "[1단계] 임시 PATH 설정 (현재 세션)"
    Write-Host "─────────────────────────────────────────────────────────────"
    
    if (-not ($env:PATH -like "*PostgreSQL\18\bin*")) {
        $env:PATH += ";$pgBin"
        Write-Host "✅ PATH 설정 완료"
    } else {
        Write-Host "✅ PATH가 이미 설정되어 있습니다."
    }
    
    Write-Host ""
    Write-Host "[2단계] 임시 DATABASE_URL 설정 (현재 세션)"
    Write-Host "─────────────────────────────────────────────────────────────"
    $env:DATABASE_URL = $dbUrl
    Write-Host "✅ DATABASE_URL 설정 완료"
    Write-Host "   $dbUrl"
    Write-Host ""
    
    # 연결 확인
    Write-Host "[3단계] PostgreSQL 연결 확인"
    Write-Host "─────────────────────────────────────────────────────────────"
    
    try {
        $version = &"$pgBin\psql" -U charger_user -d charger_db -h localhost -t -c "SELECT version();" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL 연결 성공"
            Write-Host "   $($version.Trim())"
        } else {
            Write-Host "⚠️  연결 실패 (암호 확인 필요)"
        }
    } catch {
        Write-Host "⚠️  연결 실패: $_"
    }
}

Write-Host ""

# 영구 설정
if ($setupMode -eq "permanent" -or $setupMode -eq "both") {
    Write-Host "[4단계] 영구 PATH 설정 (시스템 환경변수)"
    Write-Host "─────────────────────────────────────────────────────────────"
    
    # 관리자 권한 확인
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    
    if (-not $isAdmin) {
        Write-Host "❌ 관리자 권한이 필요합니다."
        Write-Host "   PowerShell을 '관리자로 실행'으로 다시 시작하세요."
        exit 1
    }
    
    if (-not ($currentPath -like "*PostgreSQL\18\bin*")) {
        $newPath = "$currentPath;$pgBin"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")
        Write-Host "✅ PATH 설정 완료"
        Write-Host "   다시 시작 후 적용됩니다."
    } else {
        Write-Host "✅ PATH가 이미 설정되어 있습니다."
    }
    
    Write-Host ""
    Write-Host "[5단계] 영구 DATABASE_URL 설정"
    Write-Host "─────────────────────────────────────────────────────────────"
    [Environment]::SetEnvironmentVariable("DATABASE_URL", $dbUrl, "User")
    Write-Host "✅ DATABASE_URL 설정 완료"
    Write-Host "   $dbUrl"
}

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════════"
Write-Host "✅ 설정 완료!"
Write-Host "═════════════════════════════════════════════════════════════════"
Write-Host ""
Write-Host "📌 다음 단계:"
Write-Host ""
Write-Host "1. API 서버 실행:"
Write-Host "   python gis_dashboard_api.py"
Write-Host ""
Write-Host "2. 대시보드 접속:"
Write-Host "   http://localhost:8000/docs  (API 문서)"
Write-Host "   gis_dashboard.html          (웹 대시보드)"
Write-Host ""
Write-Host "3. 연결 테스트:"
Write-Host "   python test_db_connection.py"
Write-Host ""
